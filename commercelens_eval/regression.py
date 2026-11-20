"""Score the local evidence independently of the planner and database."""
import argparse
import json
from decimal import Decimal
from pathlib import Path

from .baseline import ROOT, oracle


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)


def check(name, actual, expected):
    return {"name": name, "passed": actual == expected, "actual": actual, "expected": expected}


def evaluate(planner_path, growth_path=None):
    expected = oracle()
    phase1 = ROOT / "artifacts/phase1"
    baseline = load(phase1 / "query_results.json")
    routing = load(ROOT / "artifacts/phase2/routing_smoke.json")
    model = load(phase1 / "model_mcp_trace.json")
    result = model["tool_result"]
    model_output = result["structuredContent"] or json.loads(result["content"][0]["text"], parse_float=Decimal)
    cases = [
        check("order_count", baseline["overview"]["result"]["rows"][0][0], expected["overview"][0][0]),
        check("merchandise_amount", baseline["overview"]["result"]["rows"][0][1], expected["overview"][0][1]),
        check("average_per_order", baseline["overview"]["result"]["rows"][0][2], expected["overview"][0][2]),
        check("category_ranking", baseline["top_categories"]["result"]["rows"], expected["top_categories"]),
        check("month_delta", baseline["jul_aug_change"]["result"]["rows"], expected["jul_aug_change"]),
        check("category_declines", baseline["category_contributions"]["result"]["rows"], expected["category_contributions"]),
        check("model_mcp_overview", model_output["rows"], expected["overview"]),
        check("model_cites_query", model_output["query_id"] in model["answer"], True),
        check("decline_adds_drilldown", [e["task"] for e in routing["decline"]["evidence"]], ["compare_sales", "category_contributions"]),
        check("growth_stops_after_comparison", [e["task"] for e in routing["growth"]["evidence"]], ["compare_sales"]),
    ]
    if planner_path:
        plan = load(planner_path)
        evidence = plan["evidence"]
        tasks = [entry["task"] for entry in evidence]
        cases.extend([
            check("planner_queries_match_oracle", bool(evidence) and all(e["rows"] == expected[e["task"]] for e in evidence), True),
            check("planner_trace_matches_execution", [d["task"] for d in plan["decisions"] if d["task"] != "finish"], tasks),
            check("planner_decline_path", tasks, ["jul_aug_change", "category_contributions"]),
            check("planner_report_cites_evidence", bool(evidence) and all(e["query_id"] in plan["answer"] for e in evidence), True),
        ])
    if growth_path:
        growth = load(growth_path)
        evidence = growth["evidence"]
        cases.extend([
            check("growth_model_stops_without_drilldown", [e["task"] for e in evidence], ["jul_aug_change"]),
            check("growth_result_matches_reverse_oracle", [e["rows"] for e in evidence], [[[-expected["jul_aug_change"][0][0]]]]),
            check("growth_report_cites_query", bool(evidence) and evidence[0]["query_id"] in growth["answer"], True),
        ])
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--planner-trace", type=Path)
    parser.add_argument("--growth-trace", type=Path)
    args = parser.parse_args()
    cases = evaluate(args.planner_trace, args.growth_trace)
    passed = sum(case["passed"] for case in cases)
    output = ROOT / "artifacts/phase3/regression_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"passed": passed, "total": len(cases), "cases": cases}, default=str, indent=2), encoding="utf-8")
    print(f"{passed}/{len(cases)} evidence checks passed")
    return int(passed != len(cases))


if __name__ == "__main__":
    raise SystemExit(main())
