"""Phase 1 local stdio MCP server for Olist."""
import json
from pathlib import Path
from time import monotonic
from threading import Timer
from uuid import uuid4

import duckdb
import sqlglot
import yaml
from sqlglot import exp
from mcp.server.mcpserver import MCPServer

DATA = Path(__file__).resolve().parents[1] / "artifacts/phase1"
PROFILE = json.loads((DATA / "data_profile.json").read_text(encoding="utf-8"))
METRICS = yaml.safe_load(Path(__file__).with_name("phase1_metrics.yaml").read_text(encoding="utf-8-sig"))
TABLES = {name for name, info in PROFILE.items() if isinstance(info, dict)}
server = MCPServer("CommerceLens Olist")


@server.tool()
def get_dataset_profile(dataset_id: str = "olist") -> dict:
    """Return the Olist schema, counts, and purchase date range."""
    if dataset_id != "olist":
        raise ValueError("Unknown dataset")
    return PROFILE


@server.tool()
def get_schema(table_filter: str | None = None) -> dict:
    """Return column names and DuckDB types for the selected table."""
    return {name: PROFILE[name] for name in sorted(TABLES) if table_filter in (None, name)}


@server.tool()
def get_metric_definition(metric_ids: list[str] | None = None) -> dict:
    """Return registered metric formulas and interpretation rules."""
    return {name: METRICS[name] for name in (METRICS if metric_ids is None else metric_ids)}


ALLOWED_NODES = set("""
Select From Table Identifier Column Alias TableAlias Join Where Group Having Order Ordered
Limit Literal Distinct Star Count Sum Avg Min Max Round Coalesce Nullif
Case If Neg Add Sub Mul Div EQ NEQ LT LTE GT GTE And Or Not Between In Is Null Boolean Paren
""".split())


@server.tool()
def execute_readonly_sql(sql: str, limit: int = 100) -> dict:
    """Execute one bounded aggregate or SELECT over Olist tables."""
    if not 1 <= limit <= 500 or len(sql) > 10000:
        raise ValueError("Query exceeds size or row limit")
    statements = sqlglot.parse(sql, read="duckdb")
    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError("Expected one SELECT")
    statement = statements[0]
    for node in statement.walk():
        if type(node).__name__ not in ALLOWED_NODES:
            raise ValueError(f"Unsupported SQL expression: {type(node).__name__}")
        if isinstance(node, exp.Table) and (
            not isinstance(node.this, exp.Identifier) or node.catalog or node.db or node.name.lower() not in TABLES
        ):
            raise ValueError("Query references a table outside Olist")
        if isinstance(node, exp.Join) and node.args.get("on") is None:
            raise ValueError("JOIN requires an ON condition")
    started = monotonic()
    with duckdb.connect(str(DATA / "olist.duckdb"), read_only=True,
                        config={"enable_external_access": "false", "threads": "2", "memory_limit": "512MB"}) as conn:
        deadline = Timer(15, conn.interrupt)
        deadline.start()
        try:
            cursor = conn.execute(f"SELECT * FROM ({statement.sql(dialect='duckdb')}) AS result LIMIT ?", [limit])
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        finally:
            deadline.cancel()
            deadline.join()
    return {"columns": columns, "rows": json.loads(json.dumps(rows, default=str)),
            "query_id": uuid4().hex, "elapsed_seconds": round(monotonic() - started, 4)}


if __name__ == "__main__":
    server.run()


