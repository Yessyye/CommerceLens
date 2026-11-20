"""Validate Olist calendar periods and build the two bounded comparison queries."""
import re
from dataclasses import dataclass
from datetime import date


def month_start(value):
    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", value):
        raise ValueError("月份必须使用 YYYY-MM 格式。")
    return date.fromisoformat(f"{value}-01")


def next_month(value):
    return date(value.year + (value.month == 12), value.month % 12 + 1, 1)


def available_months(purchase_range):
    current = next_month(month_start(purchase_range[0][:7]))
    end = month_start(purchase_range[1][:7])
    months = []
    while current < end:
        months.append(current.strftime("%Y-%m"))
        current = next_month(current)
    return months


@dataclass(frozen=True)
class Comparison:
    baseline: str
    target: str

    def validate(self, purchase_range):
        month_start(self.baseline)
        month_start(self.target)
        if self.baseline == self.target:
            raise ValueError("基准月与目标月必须不同。")
        valid = available_months(purchase_range)
        if self.baseline not in valid or self.target not in valid:
            raise ValueError("请选择数据覆盖范围内的完整月份。")

    def predicate(self, month):
        timestamp = "o.order_purchase_timestamp"
        start = month_start(month)
        return f"({timestamp} >= '{start}' AND {timestamp} < '{next_month(start)}')"

    def queries(self):
        base = self.predicate(self.baseline)
        target = self.predicate(self.target)
        delta = f"ROUND(SUM(CASE WHEN {target} THEN i.price ELSE -i.price END),2)"
        source = "FROM order_items i JOIN orders o ON i.order_id=o.order_id"
        period = f"WHERE {base} OR {target}"
        return {
            "jul_aug_change": f"SELECT {delta} AS delta_brl {source} {period}",
            "category_contributions": (
                f"SELECT p.product_category_name, {delta} AS delta_brl {source} "
                "LEFT JOIN products p ON i.product_id=p.product_id "
                f"{period} GROUP BY p.product_category_name HAVING {delta} < 0 "
                "ORDER BY delta_brl, p.product_category_name NULLS LAST LIMIT 5"
            ),
        }

    def monthly_query(self):
        base = self.predicate(self.baseline)
        target = self.predicate(self.target)
        return (
            f"SELECT COUNT(DISTINCT CASE WHEN {base} THEN o.order_id END) AS baseline_orders, "
            f"ROUND(SUM(CASE WHEN {base} THEN COALESCE(i.price,0) ELSE 0 END),2) AS baseline_sales, "
            f"COUNT(DISTINCT CASE WHEN {target} THEN o.order_id END) AS target_orders, "
            f"ROUND(SUM(CASE WHEN {target} THEN COALESCE(i.price,0) ELSE 0 END),2) AS target_sales "
            "FROM orders o LEFT JOIN order_items i ON o.order_id=i.order_id "
            f"WHERE {base} OR {target}"
        )

    def breakdown_query(self, dimension, metric, category=None):
        columns = {"category": "p.product_category_name", "seller": "i.seller_id"}
        if dimension not in columns or metric not in {"sales", "orders"}:
            raise ValueError("Unknown dimension or metric")
        if category is not None and (dimension != "seller" or not re.fullmatch(r"[a-z0-9_]{1,100}", category)):
            raise ValueError("Invalid seller category filter")
        target = self.predicate(self.target)
        period = f"({self.predicate(self.baseline)} OR {target})"
        if category is not None:
            period += f" AND p.product_category_name = '{category}'"
        if metric == "sales":
            delta = f"ROUND(SUM(CASE WHEN {target} THEN i.price ELSE -i.price END),2)"
        else:
            base = self.predicate(self.baseline)
            delta = (f"COUNT(DISTINCT CASE WHEN {target} THEN o.order_id END) - "
                     f"COUNT(DISTINCT CASE WHEN {base} THEN o.order_id END)")
        group = columns[dimension]
        return (
            f"SELECT {group} AS dimension_key, {delta} AS change_value "
            "FROM order_items i JOIN orders o ON i.order_id=o.order_id "
            "LEFT JOIN products p ON i.product_id=p.product_id "
            f"WHERE {period} GROUP BY {group} HAVING {delta} < 0 "
            f"ORDER BY change_value, {group} NULLS LAST LIMIT 5"
        )
