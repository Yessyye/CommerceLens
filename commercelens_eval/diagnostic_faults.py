"""Reproduce recovery paths with injected failures and no external services."""
import asyncio
import json
import sys
from types import SimpleNamespace
from unittest.mock import patch

from mcp import MCPError
from mcp_types import REQUEST_TIMEOUT
from .baseline import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from analyst_adapter import AnalystError, McpAnalystAdapter, review_evidence
from analysis_periods import Comparison
from diagnostic_report import validate_facts
from phase2_planner import build_workflow


def inputs():
    return {"question": "diagnose", "scenario": "test", "periods": {}, "next_task": "",
            "evidence": [], "decisions": [], "status": "running"}


async def main():
    results = {}
    valid = {"query_id": "test", "columns": ["n"], "rows": [[1]], "elapsed_seconds": 0.0}

    class Session:
        def __init__(self, recover):
            self.calls = 0
            self.recover = recover

        async def call_tool(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1 or not self.recover:
                raise MCPError(REQUEST_TIMEOUT, "fixture timeout")
            return SimpleNamespace(is_error=False, structured_content=valid)

    session = Session(recover=True)
    recovered = await McpAnalystAdapter(session, {"overview": "SELECT 1"}).execute("overview")
    results["timeout_recovers_once"] = recovered["attempts"] == 2
    session = Session(recover=False)
    try:
        await McpAnalystAdapter(session, {"overview": "SELECT 1"}).execute("overview")
    except AnalystError as error:
        results["timeout_exhaustion"] = error.code == "mcp_unavailable" and session.calls == 2

    async def invalid(*args):
        return {"task": "outside_catalog", "reason": "fixture"}

    graph = build_workflow(invalid, None)
    trace = await graph.ainvoke(inputs())
    results["invalid_plan_stops"] = trace["status"] == "planning_failed"

    async def select(*args):
        return {"task": "monthly_drivers", "reason": "fixture"}

    class Empty:
        async def execute(self, task, dependencies):
            return {"task": task, "rows": [], "query_id": "empty"}

    trace = await build_workflow(select, Empty(), diagnosis=True).ainvoke(inputs())
    results["no_data_keeps_evidence"] = (trace["execution_error"]["code"] == "no_comparable_orders"
                                         and trace["evidence"][0]["query_id"] == "empty")
    with patch("analyst_adapter.subprocess.run", return_value=SimpleNamespace(returncode=1)):
        try:
            review_evidence([], Comparison("2018-07", "2018-08"))
        except AnalystError as error:
            results["docker_failure_typed"] = error.code == "docker_unavailable"

    expected = {"sales_change_brl": "-1.00", "direction": "decline", "unit": "BRL",
                "periods": {"baseline": "2018-07", "target": "2018-08"}, "query_ids": ["a"]}
    for field, wrong in [("sales_change_brl", "-2.00"), ("direction", "growth"),
                         ("unit", "USD"), ("periods", {}), ("query_ids", ["b"])]:
        results[f"report_rejects_{field}"] = field in validate_facts({**expected, field: wrong}, expected)
    results["report_rejects_unsupported_claim"] = "unsupported_fields" in validate_facts(
        {**expected, "profit": "100.00"}, expected)
    path = ROOT / "artifacts/phase3/diagnostic_fault_checks.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"{sum(results.values())}/{len(results)} fault and report checks passed")
    return int(len(results) != 11 or not all(results.values()))


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
