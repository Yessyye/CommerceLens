"""Deterministic decomposition of the merchandise sales difference."""
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def decompose(row):
    n0, raw0, n1, raw1 = row
    if not n0 or not n1:
        raise ValueError("两个周期都需要有订单才能拆解每单金额。")
    s0, s1 = Decimal(str(raw0)), Decimal(str(raw1))
    a0, a1 = s0 / n0, s1 / n1
    change = s1 - s0
    volume = (Decimal(n1 - n0) * (a0 + a1) / 2).quantize(CENT, rounding=ROUND_HALF_UP)
    value = change - volume
    return {
        "baseline_orders": n0, "target_orders": n1,
        "baseline_sales_brl": str(s0), "target_sales_brl": str(s1),
        "baseline_average_brl": str(a0.quantize(CENT, rounding=ROUND_HALF_UP)),
        "target_average_brl": str(a1.quantize(CENT, rounding=ROUND_HALF_UP)),
        "sales_change_brl": str(change.quantize(CENT)),
        "volume_contribution_brl": str(volume),
        "average_contribution_brl": str(value.quantize(CENT)),
    }
