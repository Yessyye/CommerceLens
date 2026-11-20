"""Build the local DuckDB snapshot from the original nine Olist CSVs."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    table: f"olist_{table}_dataset.csv"
    for table in ("customers", "geolocation", "order_items", "order_payments",
                  "order_reviews", "orders", "products", "sellers")
}
TABLES["product_category_name_translation"] = "product_category_name_translation.csv"


def main():
    raw = ROOT / "data/raw/olist"
    out = ROOT / "artifacts/phase1"
    database = out / "olist.duckdb"
    profile_path = out / "data_profile.json"
    missing = [name for name in TABLES.values() if not (raw / name).is_file()]
    if missing:
        raise SystemExit(f"Missing Olist CSVs in {raw}: {', '.join(missing)}")
    out.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="olist-build-", dir=out) as directory:
        temporary = Path(directory)
        build = temporary / database.name
        source = database if database.is_file() else build
        if source == build:
            with duckdb.connect(str(build)) as conn:
                for table, name in TABLES.items():
                    conn.execute(f'CREATE TABLE "{table}" AS SELECT * FROM read_csv_auto(?, sample_size=-1)',
                                 [str(raw / name)])
        with duckdb.connect(str(source), read_only=True) as conn:
            profile = {
                table: {
                    "rows": conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0],
                    "columns": conn.execute(f'DESCRIBE "{table}"').fetchall(),
                }
                for table in TABLES
            }
            profile["purchase_range"] = conn.execute(
                "SELECT min(order_purchase_timestamp), max(order_purchase_timestamp) FROM orders"
            ).fetchone()
        staged_profile = temporary / profile_path.name
        staged_profile.write_text(json.dumps(profile, default=str, indent=2), encoding="utf-8")
        if source == build:
            build.rename(database)
        staged_profile.replace(profile_path)
    print({table: profile[table]["rows"] for table in TABLES})


if __name__ == "__main__":
    main()
