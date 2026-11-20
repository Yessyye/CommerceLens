"""Recompute the phase 1 evidence from the source CSVs, independently of SQL."""
import csv
import json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/olist"
CENT = Decimal("0.01")


def rows(table):
    with (RAW / f"olist_{table}_dataset.csv").open(encoding="utf-8", newline="") as source:
        yield from csv.DictReader(source)


def oracle(reverse_periods=False, *, baseline_month="2018-07", target_month="2018-08"):
    if reverse_periods:
        baseline_month, target_month = target_month, baseline_month
    orders = {row["order_id"]: row["order_purchase_timestamp"][:7] for row in rows("orders")}
    categories = {row["product_id"]: row["product_category_name"] or None for row in rows("products")}
    totals = defaultdict(Decimal)
    changes = defaultdict(Decimal)
    monthly_sales = defaultdict(Decimal)
    monthly_orders = defaultdict(int)
    dimension_orders = defaultdict(set)
    seller_changes = defaultdict(Decimal)
    seller_orders = defaultdict(set)
    for month in orders.values():
        monthly_orders[month] += 1
    total = Decimal(0)
    for row in rows("order_items"):
        category = categories.get(row["product_id"])
        price = Decimal(row["price"])
        total += price
        totals[category] += price
        month = orders[row["order_id"]]
        monthly_sales[month] += price
        if month in (baseline_month, target_month):
            direction = 1 if month == target_month else -1
            dimension_orders[(category, month)].add(row["order_id"])
            seller_changes[(category, row["seller_id"])] += direction * price
            seller_orders[(category, row["seller_id"], month)].add(row["order_id"])
        if month == target_month:
            changes[category] += price
        elif month == baseline_month:
            changes[category] -= price
    declines = sorted(
        ((key, value) for key, value in changes.items() if value < 0),
        key=lambda item: (item[1], item[0] is None, item[0] or ""),
    )
    order_changes = {
        key: len(dimension_orders[(key, target_month)]) - len(dimension_orders[(key, baseline_month)])
        for key in {key for key, _ in dimension_orders}
    }
    order_declines = sorted(
        ((key, value) for key, value in order_changes.items() if value < 0),
        key=lambda item: (item[1], item[0] is None, item[0] or ""),
    )

    def sellers_for(ranked_categories, order_metric=False):
        if not ranked_categories or ranked_categories[0][0] is None:
            return []
        category = ranked_categories[0][0]
        ranking = []
        for (key, seller), amount in seller_changes.items():
            if key != category:
                continue
            if order_metric:
                amount = (len(seller_orders[(key, seller, target_month)])
                          - len(seller_orders[(key, seller, baseline_month)]))
            if amount < 0:
                ranking.append([seller, amount])
        return sorted(ranking, key=lambda item: (item[1], item[0]))[:5]
    return {
        "overview": [[len(orders), total, (total / len(orders)).quantize(CENT, rounding=ROUND_HALF_UP)]],
        "top_categories": [[key, value] for key, value in sorted(totals.items(), key=lambda item: -item[1])[:5]],
        "jul_aug_change": [[sum(changes.values())]],
        "category_contributions": [[key, value] for key, value in declines[:5]],
        "monthly_drivers": [[monthly_orders[baseline_month], monthly_sales[baseline_month],
                             monthly_orders[target_month], monthly_sales[target_month]]],
        "category_order_declines": [[key, value] for key, value in order_declines[:5]],
        "seller_sales_declines": sellers_for(declines),
        "seller_order_declines": sellers_for(order_declines, order_metric=True),
    }


def main():
    path = ROOT / "artifacts/phase1/query_results.json"
    evidence = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    report = {}
    for name, expected in oracle().items():
        if name not in evidence:
            continue
        result = evidence[name]["result"]
        report[name] = {
            "passed": result["rows"] == expected,
            "query_id": result["query_id"],
            "expected": expected,
            "actual": result["rows"],
        }
    target = ROOT / "artifacts/phase3/baseline_validation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, default=str, indent=2), encoding="utf-8")
    print(f"{sum(row['passed'] for row in report.values())}/{len(report)} checks passed")
    return 0 if all(row["passed"] for row in report.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
