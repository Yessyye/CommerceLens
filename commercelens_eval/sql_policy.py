"""Check SQL policy rejections and verify that the dataset stays unchanged."""
import hashlib
import json
import sys
from pathlib import Path

from .baseline import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from phase1_mcp import DATA, execute_readonly_sql


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main():
    db = DATA / "olist.duckdb"
    before = digest(db)
    allowed = execute_readonly_sql("SELECT COUNT(*) FROM orders", limit=1)
    cases = [
        ("write_statement", "CREATE TABLE regression_probe (x INTEGER)", 1),
        ("unknown_table", "SELECT * FROM unknown_table", 1),
        ("multiple_statements", "SELECT 1; SELECT 2", 1),
        ("oversized_result_limit", "SELECT COUNT(*) FROM orders", 501),
        ("cross_join_without_condition", "SELECT COUNT(*) FROM orders CROSS JOIN products", 1),
    ]
    results = []
    for name, sql, limit in cases:
        try:
            execute_readonly_sql(sql, limit)
        except ValueError as error:
            results.append({"case": name, "passed": True, "rejection": str(error)})
        else:
            results.append({"case": name, "passed": False})
    unchanged = before == digest(db)
    target = DATA.parent / "phase3" / "sql_policy_validation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"positive_control": allowed, "database_unchanged": unchanged,
                                  "rejections": results}, indent=2), encoding="utf-8")
    print(f"{sum(item['passed'] for item in results)}/{len(results)} rejections passed; unchanged={unchanged}")
    return int(not unchanged or not all(item["passed"] for item in results))


if __name__ == "__main__":
    raise SystemExit(main())
