"""Ten reproducible public-data cases for the read-only analytical tool."""
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal

from .baseline import ROOT, oracle, rows

sys.path.insert(0, str(ROOT / "scripts"))
from phase1_mcp import execute_readonly_sql


def cases():
    expected = oracle()
    evidence = json.loads((ROOT / "artifacts/phase1/query_results.json").read_text(encoding="utf-8"))
    questions = {
        "overview": "How many orders, how much merchandise value, and what average value per order?",
        "top_categories": "Which five product categories contributed most merchandise value?",
        "jul_aug_change": "How much did merchandise value change from July to August 2018?",
        "category_contributions": "Which categories contributed the largest declines in that comparison?",
    }
    for key, question in questions.items():
        yield key, question, evidence[key]["sql"], expected[key]
    states = Counter(order["order_status"] for order in rows("orders"))
    freight = Decimal()
    seller_totals = defaultdict(Decimal)
    item_count = 0
    for item in rows("order_items"):
        freight += Decimal(item["freight_value"])
        seller_totals[item["seller_id"]] += Decimal(item["price"])
        item_count += 1
    payment = sum(Decimal(row["payment_value"]) for row in rows("order_payments"))
    best_seller = min(seller_totals, key=lambda key: (-seller_totals[key], key))
    yield "order_status_counts", "How many orders are in each recorded status?", (
        "SELECT order_status, COUNT(*) AS n FROM orders GROUP BY order_status ORDER BY order_status"
    ), [[status, count] for status, count in sorted(states.items())]
    yield "freight_total", "What is total item freight in BRL?", (
        "SELECT ROUND(SUM(freight_value),2) FROM order_items"
    ), [[freight]]
    yield "top_seller", "Which seller has the highest merchandise value?", (
        "SELECT seller_id, ROUND(SUM(price),2) AS sales FROM order_items GROUP BY seller_id ORDER BY sales DESC, seller_id LIMIT 1"
    ), [[best_seller, seller_totals[best_seller]]]
    yield "payment_total", "What is total recorded payment value, including payment components?", (
        "SELECT ROUND(SUM(payment_value),2) FROM order_payments"
    ), [[payment]]
    yield "item_count", "How many order item records are present?", (
        "SELECT COUNT(*) FROM order_items"
    ), [[item_count]]
    yield "product_count", "How many product identifiers are present?", (
        "SELECT COUNT(DISTINCT product_id) FROM products"
    ), [[len({product["product_id"] for product in rows("products")})]]


def main():
    findings = []
    for case_id, question, sql, expected in cases():
        result = execute_readonly_sql(sql)
        actual = json.loads(json.dumps(result["rows"]), parse_float=Decimal)
        findings.append({
            "id": case_id, "question": question, "sql": sql, "result": result,
            "expected": expected, "passed": actual == expected,
        })
    target = ROOT / "artifacts/phase3/golden_sql_results.json"
    target.write_text(json.dumps(findings, default=str, indent=2), encoding="utf-8")
    passed = sum(case["passed"] for case in findings)
    print(f"{passed}/{len(findings)} golden SQL cases passed")
    return int(passed != len(findings))


if __name__ == "__main__":
    raise SystemExit(main())

