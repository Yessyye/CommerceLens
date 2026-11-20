"""Compare a fixed SQL diagnosis and the model workflow on three real periods."""
import argparse
import asyncio
import json
import sys
from decimal import Decimal
from time import monotonic

from .baseline import ROOT, oracle

sys.path.insert(0, str(ROOT / "scripts"))
from analysis_periods import Comparison
from analyst_adapter import cells_match
from phase1_mcp import execute_readonly_sql
from phase2_planner import run

QUESTION = "Explain whether merchandise sales changed mainly because of order volume or average merchandise per order. If sales declined, drill down by category and seller."
CASES = [
    ("volume_decline", "2018-05", "2018-06", ["monthly_drivers", "category_order_declines", "seller_order_declines"]),
    ("average_decline", "2018-07", "2018-08", ["monthly_drivers", "category_contributions", "seller_sales_declines"]),
    ("growth", "2018-06", "2018-07", ["monthly_drivers"]),
]
PILOT_CASES = [
    ("A", "2017-11", "2017-12", ["monthly_drivers", "category_order_declines", "seller_order_declines"]),
    ("B", "2018-04", "2018-02", ["monthly_drivers", "category_contributions", "seller_sales_declines"]),
    ("C", "2018-03", "2018-04", ["monthly_drivers"]),
]


def matches(actual, expected):
    return len(actual) == len(expected) and all(
        len(a) == len(b) and all(cells_match(x, y) for x, y in zip(a, b)) for a, b in zip(actual, expected)
    )


def fixed_sql(comparison, tasks):
    queries = {
        "monthly_drivers": comparison.monthly_query(),
        "category_order_declines": comparison.breakdown_query("category", "orders"),
        **comparison.queries(),
    }
    evidence = []
    for task in tasks:
        if task.startswith("seller_"):
            metric = "orders" if task == "seller_order_declines" else "sales"
            sql = comparison.breakdown_query("seller", metric, evidence[-1]["rows"][0][0])
        else:
            sql = queries[task]
        evidence.append({"task": task, "sql": sql, **execute_readonly_sql(sql)})
    return evidence


async def main(cases=CASES, output_name="diagnostic_eval.json"):
    results = []
    for name, baseline, target, tasks in cases:
        comparison = Comparison(baseline, target)
        expected = oracle(baseline_month=baseline, target_month=target)
        started = monotonic()
        fixed = fixed_sql(comparison, tasks)
        fixed_time = monotonic() - started
        started = monotonic()
        path = await run(QUESTION, comparison=comparison, diagnosis=True, docker_review=True)
        elapsed = monotonic() - started
        trace = json.loads(path.read_text(encoding="utf-8"))
        evidence = trace["evidence"]
        started = monotonic()
        numeric = all(matches(item["rows"], expected[item["task"]]) for item in evidence)
        ids = all(item["query_id"] in trace["answer"] for item in evidence)
        decomposition = trace.get("drivers", {})
        additive = bool(decomposition) and (
            Decimal(decomposition["volume_contribution_brl"]) + Decimal(decomposition["average_contribution_brl"])
            == Decimal(decomposition["sales_change_brl"])
        )
        automated_review_time = monotonic() - started
        fixed_match = all(matches(item["rows"], expected[item["task"]]) for item in fixed)
        passed = (trace["status"] == "completed" and [item["task"] for item in evidence] == tasks
                  and numeric and ids and additive and fixed_match and trace.get("docker_review", {}).get("passed"))
        results.append({
            "case": name, "periods": trace["periods"], "trace": str(path.relative_to(ROOT)), "passed": bool(passed),
            "actual_path": [item["task"] for item in evidence], "expected_path": tasks,
            "agent_seconds": round(elapsed, 3), "agent_queries": len(evidence),
            "tokens": sum(call["total_tokens"] for call in trace["usage"]),
            "fixed_sql_seconds": round(fixed_time, 3), "fixed_sql_queries": len(fixed),
            "fixed_sql_correct": fixed_match, "fixed_sql_evidence": fixed,
            "agent_numeric_correct": numeric, "agent_citations_present": ids,
            "decomposition_balanced": additive, "docker_review_passed": trace.get("docker_review", {}).get("passed"),
            "automated_review_seconds": round(automated_review_time, 6),
            "human_review_seconds": None,
        })
        print(name, "PASS" if passed else "FAIL", flush=True)
    output = ROOT / "artifacts/phase3" / output_name
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return int(not all(case["passed"] for case in results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Run the BI comparison pilot periods.")
    args = parser.parse_args()
    suite = main(PILOT_CASES, "bi_comparison_pilot.json") if args.pilot else main()
    raise SystemExit(asyncio.run(suite))
