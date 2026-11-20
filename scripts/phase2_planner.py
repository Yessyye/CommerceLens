"""Run a bounded model planner over public Olist aggregate MCP queries."""
import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
from phase1_mcp import DATA, PROFILE
from analysis_periods import Comparison
from analyst_adapter import AnalystAdapter, AnalystError, McpAnalystAdapter, QueryEvidence, review_evidence
from sales_drivers import decompose
from diagnostic_report import report_facts, render_report, validate_facts
from decimal import Decimal

ROOT = DATA.parents[1]
MAX_TASKS = 4
CATALOG = {
    "overview": "All-time order count, merchandise amount, and average per order",
    "top_categories": "All-time top five categories by merchandise amount",
    "jul_aug_change": "Target month minus baseline month merchandise amount",
    "category_contributions": "Up to five largest negative category contributions for the selected comparison",
}
DEPENDENCIES = {"category_contributions": "jul_aug_change"}
DIAGNOSTIC_TASKS = {
    "monthly_drivers": "Compare monthly order count and merchandise amount, then decompose the change",
    "category_contributions": "Rank negative category contributions in BRL",
    "category_order_declines": "Rank categories by decline in distinct orders containing the category",
    "seller_sales_declines": "Within the leading declining category, rank seller merchandise declines",
    "seller_order_declines": "Within the leading declining category, rank seller order-count declines",
}


class State(TypedDict):
    question: str
    scenario: str
    periods: dict[str, str]
    next_task: str
    evidence: list[QueryEvidence]
    execution_error: dict
    drivers: dict
    decisions: list[dict]
    status: str


def diagnostic_tasks(observed, drivers):
    if "monthly_drivers" not in observed:
        return ["monthly_drivers"]
    if Decimal(drivers["sales_change_brl"]) >= 0:
        return []
    volume = Decimal(drivers["volume_contribution_brl"]) < Decimal(drivers["average_contribution_brl"])
    category = "category_order_declines" if volume else "category_contributions"
    seller = "seller_order_declines" if volume else "seller_sales_declines"
    if category not in observed:
        return [category]
    rows = observed[category]["rows"]
    if rows and rows[0][0] is not None and seller not in observed:
        return [seller]
    return []


def build_workflow(choose, analyst: AnalystAdapter, diagnosis=False):
    async def plan(state):
        completed = {entry["task"] for entry in state["evidence"]}
        observed = {entry["task"]: entry for entry in state["evidence"]}
        available = {
            task: description for task, description in CATALOG.items()
            if task not in completed and DEPENDENCIES.get(task) in completed | {None}
            and (task != "category_contributions" or observed["jul_aug_change"]["rows"][0][0] < 0)
        }
        if diagnosis:
            available = {task: DIAGNOSTIC_TASKS[task] for task in diagnostic_tasks(observed, state.get("drivers", {}))}
        if len(completed) >= MAX_TASKS or not available:
            return {"next_task": "finish", "status": "completed" if diagnosis else "budget_or_catalog_exhausted"}
        valid_ids = [*available, *(["finish"] if completed and not diagnosis else [])]
        feedback = None
        for _ in range(2):
            try:
                decision = await choose(state["question"], available, state["evidence"], valid_ids, feedback)
            except json.JSONDecodeError:
                decision = None
            task = decision.get("task") if isinstance(decision, dict) else None
            reason = decision.get("reason") if isinstance(decision, dict) else None
            if task in valid_ids and isinstance(reason, str) and reason.strip():
                break
            feedback = f"Invalid selection {task!r}. Use an exact ID from allowed_ids and include a reason."
        else:
            return {"next_task": "finish", "status": "planning_failed",
                    "execution_error": {"code": "invalid_plan", "message": "模型两次未返回有效任务。"}}
        return {"next_task": task, "decisions": [*state["decisions"], {"task": task, "reason": reason}],
                "status": "completed" if task == "finish" else "running"}

    async def execute(state):
        task = state["next_task"]
        try:
            evidence = await analyst.execute(task, state["evidence"])
        except AnalystError as error:
            return {"status": "execution_failed", "execution_error": {"task": task, "code": error.code, "message": str(error)}}
        update = {"evidence": [*state["evidence"], evidence]}
        if task == "monthly_drivers":
            try:
                update["drivers"] = decompose(evidence["rows"][0])
            except (ValueError, IndexError) as error:
                update.update(status="execution_failed", execution_error={"task": task, "code": "no_comparable_orders", "message": str(error)})
        return update

    def route(state):
        return END if state["next_task"] == "finish" else "execute"

    graph = StateGraph(State)
    graph.add_node("plan", plan)
    graph.add_node("execute", execute)
    graph.add_edge(START, "plan")
    graph.add_conditional_edges("plan", route, [END, "execute"])
    graph.add_conditional_edges("execute", lambda state: END if state["status"] == "execution_failed" else "plan", [END, "plan"])
    return graph.compile()


async def run(question, reverse_periods=False, *, docker_review=False, comparison=None, diagnosis=False):
    if comparison is None:
        comparison = Comparison("2018-08", "2018-07") if reverse_periods else Comparison("2018-07", "2018-08")
    elif reverse_periods:
        raise ValueError("Set explicit months or reverse the default periods, not both.")
    comparison.validate(PROFILE["purchase_range"])
    configured_path = os.environ.get("COMMERCE_LLM_CONFIG")
    local_pointer = ROOT / ".local-llm-config"
    if not configured_path and local_pointer.is_file():
        configured_path = local_pointer.read_text(encoding="utf-8-sig").strip()
    config = Path(configured_path).expanduser() if configured_path else ROOT / ".env"
    settings = dict(re.findall(r"^\s*(LLM_\w+)\s*=\s*(.+)$", config.read_text(encoding="utf-8-sig"), re.M))
    settings = {key: value.strip().strip("'\"") for key, value in settings.items()}
    endpoint = settings["LLM_BASE_URL"].rstrip("/")
    if endpoint not in {"https://api.deepseek.com", "https://api.deepseek.com/v1"}:
        raise ValueError("Expected authorized DeepSeek endpoint")
    baseline = json.loads((DATA / "query_results.json").read_text(encoding="utf-8"))
    queries = {task: baseline[task]["sql"] for task in ("overview", "top_categories")}
    queries.update(comparison.queries())
    if diagnosis:
        queries["monthly_drivers"] = comparison.monthly_query()
        queries["category_order_declines"] = comparison.breakdown_query("category", "orders")

        def seller_query(metric, category_task):
            def build(dependencies):
                category = next(item["rows"][0][0] for item in dependencies if item["task"] == category_task)
                return comparison.breakdown_query("seller", metric, category)
            return build

        queries["seller_sales_declines"] = seller_query("sales", "category_contributions")
        queries["seller_order_declines"] = seller_query("orders", "category_order_declines")
    scenario = f"{comparison.target} versus {comparison.baseline}"
    params = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).with_name("phase1_mcp.py"))])
    usage = []
    async with AsyncOpenAI(api_key=settings["LLM_API_KEY"], base_url=endpoint, timeout=45, max_retries=0) as client:
        async def complete(system, payload, structured=False):
            options = {"response_format": {"type": "json_object"}} if structured else {}
            response = await client.chat.completions.create(
                model=settings["LLM_MODEL_ID"], max_tokens=1000,
                extra_body={"thinking": {"type": "disabled"}},
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}], **options)
            if response.usage:
                usage.append(response.usage.model_dump())
            return response.choices[0].message.content or ""

        async def choose(prompt, available, evidence, valid_ids, feedback):
            return json.loads(await complete(
                "Choose the next available query needed to answer the question, or finish when the question is answered. "
                "The scenario is context for a requested period comparison only. It is not a request to compare periods. "
                "Never add investigations the question does not ask for. "
                "Return a JSON object with task and reason. The task MUST be an exact string from allowed_ids. "
                "For a decline investigation, first measure the change; "
                "only investigate negative contributions if the observed change is negative.",
                {"question": prompt, "scenario": scenario, "allowed_ids": valid_ids, "available": available,
                 "evidence": evidence, "validation_feedback": feedback}, structured=True))

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await asyncio.wait_for(session.initialize(), 45)

                analyst = McpAnalystAdapter(session, queries)
                state = await build_workflow(choose, analyst, diagnosis).ainvoke({
                    "question": question, "scenario": scenario,
                    "periods": {"baseline": comparison.baseline, "target": comparison.target},
                    "next_task": "", "evidence": [], "decisions": [], "status": "running",
                })
        review = None
        if "execution_error" not in state and docker_review:
            try:
                review = await asyncio.to_thread(review_evidence, state["evidence"], comparison)
            except AnalystError as error:
                state["status"] = "review_failed"
                state["execution_error"] = {"code": error.code, "message": str(error)}
        if review is not None and diagnosis:
            review["drivers_match"] = review.get("drivers") == state.get("drivers")
            review["passed"] = review["passed"] and review["drivers_match"]
        if "execution_error" in state:
            state["answer"] = state["execution_error"]["message"]
        elif review is not None and not review["passed"]:
            state["status"] = "review_mismatch"
            state["answer"] = "容器复算与 SQL 结果不一致。请在执行证据中检查对应任务。"
        elif diagnosis:
            expected = report_facts(state)
            try:
                proposal = json.loads(await complete(
                    "Return a JSON report with exactly the same fields and values as verified_facts. "
                    "Preserve strings, dates, unit, direction, and all query IDs. Do not add causal, profit, or advertising claims.",
                    {"verified_facts": expected}, structured=True))
                mismatches = validate_facts(proposal, expected)
            except json.JSONDecodeError:
                mismatches = ["invalid_report_json"]
            state["report_validation"] = {"model_fields_match": not mismatches, "rejected_fields": mismatches}
            state["answer"] = render_report(state, expected)
        else:
            state["answer"] = await complete(
                "Answer in Chinese, follow the scenario's period order, use only supplied aggregate evidence and cite all query IDs. "
                "Do not infer causes, profit, or advertising performance from this dataset.", state)
        if review is not None:
            state["docker_review"] = review
    state["usage"] = usage
    state["data_purchase_end"] = PROFILE["purchase_range"][1]
    out = DATA.parent / "phase2" / f"planner_{uuid4().hex}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", default="Compare merchandise sales for the scenario's two periods. If they fell, find the largest negative category contributions.")
    parser.add_argument("--reverse-periods", action="store_true", help="Use July as the target and August as the baseline.")
    parser.add_argument("--docker-review", action="store_true", help="Recompute aggregate evidence in Docker.")
    parser.add_argument("--baseline-month")
    parser.add_argument("--target-month")
    parser.add_argument("--diagnosis", action="store_true", help="Decompose sales and drill down by the dominant factor.")
    args = parser.parse_args()
    if bool(args.baseline_month) != bool(args.target_month):
        parser.error("Provide both --baseline-month and --target-month")
    comparison = Comparison(args.baseline_month, args.target_month) if args.baseline_month else None
    asyncio.run(run(args.question, args.reverse_periods, docker_review=args.docker_review, comparison=comparison, diagnosis=args.diagnosis))
