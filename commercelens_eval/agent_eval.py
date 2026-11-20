"""Run the supported planner questions against independent CSV expectations."""
import asyncio
import argparse
import json
import sys
from decimal import Decimal
from time import monotonic

from .baseline import ROOT, oracle

sys.path.insert(0, str(ROOT / "scripts"))

COMPARISON = "Compare merchandise sales for the scenario's two periods. If sales fell, identify the largest negative category contributions."
CASES = [
    ("overview", "For all recorded orders, give order count, total item sales and average item sales per order.", False, ["overview"]),
    ("ranking", "List the five product categories with the greatest all-time item sales.", False, ["top_categories"]),
    ("comparison_only", "Give only the merchandise sales difference for the two months in the scenario. No category breakdown is needed.", False, ["jul_aug_change"]),
    ("decline", COMPARISON, False, ["jul_aug_change", "category_contributions"]),
    ("growth", COMPARISON, True, ["jul_aug_change"]),
]


def score_trace(path, expected, reverse, tasks, docker_review=False):
    state = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    evidence = state["evidence"]
    values = {**expected}
    if reverse:
        values["jul_aug_change"] = [[-expected["jul_aug_change"][0][0]]]
    actual_path = [item["task"] for item in evidence]
    numeric_match = bool(evidence) and all(item["rows"] == values[item["task"]] for item in evidence)
    citations = bool(evidence) and all(item["query_id"] in state["answer"] for item in evidence)
    review = state.get("docker_review", {})
    verified_ids = [item["query_id"] for item in review.get("checks", []) if item["matched"]]
    container_match = bool(review.get("passed") and verified_ids == [item["query_id"] for item in evidence])
    return {
        "trace": str(path.relative_to(ROOT)),
        "actual_path": actual_path,
        "numeric_match": numeric_match,
        "citations": citations,
        "tokens": sum(call["total_tokens"] for call in state["usage"]),
        "model_calls": len(state["usage"]),
        "docker_review": container_match if docker_review else None,
        "passed": actual_path == tasks and numeric_match and citations and (container_match or not docker_review),
    }


def main(replay=False, docker_review=False):
    if not replay:
        from phase2_planner import run

    expected = oracle()
    name = "agent_eval_docker" if docker_review else "agent_eval"
    output = ROOT / "artifacts/phase3" / f"{name}.json"
    saved = {}
    if replay:
        saved = {item["id"]: item for item in json.loads(output.read_text(encoding="utf-8"))["cases"]}
    findings = []
    for name, question, reverse, tasks in CASES:
        started = monotonic()
        entry = {"id": name, "expected_path": tasks, "passed": False}
        try:
            path = (ROOT / saved[name]["trace"].replace("\\", "/") if replay
                    else asyncio.run(run(question, reverse, docker_review=docker_review)))
            entry.update(score_trace(path, expected, reverse, tasks, docker_review))
        except Exception as error:
            entry["error_type"] = type(error).__name__
        entry["elapsed_seconds"] = round(monotonic() - started, 2)
        findings.append(entry)
        print(name, "PASS" if entry["passed"] else "FAIL", flush=True)
    if replay:
        output = output.with_stem(output.stem + "_replay")
    output.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(item["passed"] for item in findings)
    output.write_text(json.dumps({"passed": passed, "total": len(findings), "cases": findings}, indent=2), encoding="utf-8")
    print(f"{passed}/{len(findings)} Agent cases passed")
    return int(passed != len(findings))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true", help="Score saved traces without making API calls.")
    parser.add_argument("--docker-review", action="store_true", help="Require matching Docker review evidence.")
    args = parser.parse_args()
    raise SystemExit(main(args.replay, args.docker_review))
