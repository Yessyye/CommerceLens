"""Execution boundary for Olist analysis and Docker review."""
import json
import subprocess
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Protocol, TypedDict
from mcp import MCPError
from mcp_types import REQUEST_TIMEOUT


class QueryEvidence(TypedDict):
    task: str
    sql: str
    query_id: str
    columns: list[str]
    rows: list[list]
    elapsed_seconds: float
    attempts: int


class AnalystError(RuntimeError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


class AnalystAdapter(Protocol):
    async def execute(self, task: str, dependencies=()) -> QueryEvidence: ...


class McpAnalystAdapter:
    def __init__(self, session, queries: dict[str, str]):
        self.session = session
        self.queries = queries

    async def execute(self, task: str, dependencies=()) -> QueryEvidence:
        if task not in self.queries:
            raise AnalystError("unknown_task", "任务不在查询目录中。")
        template = self.queries[task]
        sql = template(dependencies) if callable(template) else template
        for attempt in (1, 2):
            try:
                result = await self.session.call_tool("execute_readonly_sql", {"sql": sql}, read_timeout_seconds=20)
                break
            except (TimeoutError, OSError, MCPError) as error:
                retryable = not isinstance(error, MCPError) or error.code == REQUEST_TIMEOUT
                if not retryable:
                    raise AnalystError("mcp_rejected", "MCP 拒绝或未能执行查询。") from error
                if attempt == 2:
                    raise AnalystError("mcp_unavailable", "MCP 查询连接失败或超时，重试一次后仍未恢复。") from error
            except Exception as error:
                raise AnalystError("mcp_unavailable", "MCP 查询连接失败。") from error
        if result.is_error:
            raise AnalystError("mcp_rejected", "MCP 拒绝或未能执行查询。")
        try:
            payload = result.structured_content or json.loads(result.content[0].text)
            columns = payload["columns"]
            rows = payload["rows"]
            query_id = payload["query_id"]
            elapsed = payload["elapsed_seconds"]
            if not (
                isinstance(query_id, str) and query_id
                and isinstance(columns, list) and columns and all(isinstance(name, str) for name in columns)
                and isinstance(rows, list)
                and all(isinstance(row, list) and len(row) == len(columns) for row in rows)
                and type(elapsed) in (float, int) and elapsed >= 0
            ):
                raise ValueError("Invalid evidence")
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
            raise AnalystError("invalid_evidence", "MCP 返回的查询证据格式不完整。") from error
        return QueryEvidence(task=task, sql=sql, query_id=query_id,
                             columns=columns, rows=rows, elapsed_seconds=elapsed, attempts=attempt)


def cells_match(actual, expected):
    if type(actual) not in (int, float):
        return actual == expected
    try:
        return Decimal(str(actual)) == Decimal(str(expected))
    except InvalidOperation:
        return False


def review_evidence(evidence: list[QueryEvidence], comparison):
    command = [
        sys.executable, str(Path(__file__).with_name("docker_review.py")),
        "--baseline-month", comparison.baseline, "--target-month", comparison.target,
    ]
    monthly = next((item for item in evidence if item["task"] == "monthly_drivers"), None)
    if monthly:
        command += ["--driver-row", json.dumps(monthly["rows"][0])]
    try:
        process = subprocess.run(command, capture_output=True, encoding="utf-8", timeout=100)
    except subprocess.TimeoutExpired as error:
        raise AnalystError("docker_timeout", "Docker 复核超时。") from error
    if process.returncode:
        raise AnalystError("docker_unavailable", "Docker 复核未运行成功。请检查 Docker Desktop 和 Python 镜像。")
    try:
        review = json.loads(process.stdout)
        rows = review.pop("rows")
        checks = []
        for item in evidence:
            expected = rows[item["task"]]
            actual = item["rows"]
            matches = len(actual) == len(expected) and all(
                len(left) == len(right) and all(cells_match(a, b) for a, b in zip(left, right))
                for left, right in zip(actual, expected)
            )
            checks.append({"task": item["task"], "query_id": item["query_id"], "matched": matches})
        return {**review, "checks": checks, "passed": bool(checks) and all(check["matched"] for check in checks)}
    except (KeyError, TypeError, ValueError) as error:
        raise AnalystError("invalid_docker_evidence", "Docker 返回的复核证据无法读取。") from error
