"""Validate structured report facts and render a report from verified evidence."""
from decimal import Decimal


def report_facts(state):
    drivers = state["drivers"]
    change = Decimal(drivers["sales_change_brl"])
    return {
        "periods": state["periods"],
        "direction": "decline" if change < 0 else "growth" if change > 0 else "flat",
        "unit": "BRL",
        "sales_change_brl": drivers["sales_change_brl"],
        "volume_contribution_brl": drivers["volume_contribution_brl"],
        "average_contribution_brl": drivers["average_contribution_brl"],
        "query_ids": [entry["query_id"] for entry in state["evidence"]],
    }


def validate_facts(proposed, expected):
    if not isinstance(proposed, dict):
        return ["invalid_report_shape"]
    mismatches = [field for field, value in expected.items() if proposed.get(field) != value]
    if set(proposed) - set(expected):
        mismatches.append("unsupported_fields")
    return mismatches


def render_report(state, facts):
    drivers = state["drivers"]
    direction = {"decline": "下降", "growth": "增长", "flat": "持平"}[facts["direction"]]
    baseline = facts["periods"]["baseline"]
    target = facts["periods"]["target"]
    lines = [
        f"### {target} 对比 {baseline}",
        f"商品金额**{direction}**，差额为 **{facts['sales_change_brl']} BRL**。",
        "",
        "| 月份 | 订单量 | 商品金额（BRL） | 每单商品金额（BRL） |",
        "|---|---:|---:|---:|",
        f"| {baseline} | {drivers['baseline_orders']:,} | {drivers['baseline_sales_brl']} | {drivers['baseline_average_brl']} |",
        f"| {target} | {drivers['target_orders']:,} | {drivers['target_sales_brl']} | {drivers['target_average_brl']} |",
        "",
        f"订单量变化贡献 **{facts['volume_contribution_brl']} BRL**，每单商品金额变化贡献 **{facts['average_contribution_brl']} BRL**。",
        "订单量贡献用订单数差乘两期平均每单金额。每单金额贡献为总差额减订单量贡献，包含分币舍入差。",
    ]
    for entry in state["evidence"][1:]:
        metric = "单" if "order" in entry["task"] else "BRL"
        kind = "品类内卖家" if entry["task"].startswith("seller") else "品类"
        lines += ["", f"**{kind}下降排行（{metric}）**"]
        if kind == "品类内卖家":
            category = state["evidence"][1]["rows"][0][0]
            lines.append(f"筛选品类：`{category}`")
        if not entry["rows"]:
            lines.append("当前范围内没有下降项。")
        else:
            lines.extend(f"- `{key if key is not None else '未分类'}`：{value:+,.2f} {metric}"
                         if metric == "BRL" else f"- `{key if key is not None else '未分类'}`：{value:+,d} 单"
                         for key, value in entry["rows"])
    lines += ["", "查询证据：" + "、".join(f"`{value}`" for value in facts["query_ids"]),
              "", "按下单月份统计全部记录状态，商品金额不含运费。一个订单可涉及多个品类或卖家，分组订单量不可相加。变化贡献是算术拆解，数据缺少完整成本和广告投入。"]
    return "\n".join(lines)
