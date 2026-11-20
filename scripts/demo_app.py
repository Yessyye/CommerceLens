"""Local CommerceLens demonstration for saved and live analysis traces."""
import asyncio
import json
import logging
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analysis_periods import Comparison, available_months
from business_questions import EXAMPLES, interpret_question

ARTIFACTS = ROOT / "artifacts"
EVAL = ARTIFACTS / "phase3"
LOGGER = logging.getLogger(__name__)
DRIVER_LABELS = {
    "volume_contribution_brl": "订单量变化贡献",
    "average_contribution_brl": "每单商品金额变化贡献",
}
OLIST_ARCHIVE_END = "2018-10-17"
CATEGORY_NAMES = {
    "beleza_saude": "美妆健康",
    "cama_mesa_banho": "床品、餐桌与卫浴",
    "esporte_lazer": "运动休闲",
    "informatica_acessorios": "电脑及配件",
    "relogios_presentes": "钟表与礼品",
}
SCENARIOS = {
    "商品金额变化诊断": ("Compare order volume and average merchandise per order, explain the contributions to sales change, and if declining drill down to categories and sellers.", False),
    "经营总览": ("Report the all-time order count, item sales, and average item sales per order.", False),
    "品类销售排名": ("List the five categories with the highest all-time item sales.", False),
    "销售下降与品类下钻": ("Compare merchandise sales for the scenario's two months. If sales fell, list the largest negative category contributions.", False),
    "增长场景对照": ("Compare merchandise sales for the scenario's two months. If sales fell, list the largest negative category contributions.", True),
}
TASK_LABELS = {
    "monthly_drivers": "两月订单与商品金额",
    "category_order_declines": "品类订单量下降",
    "seller_sales_declines": "品类内卖家金额下降",
    "seller_order_declines": "品类内卖家订单量下降",
    "overview": "经营总览",
    "top_categories": "品类销售排名",
    "jul_aug_change": "商品金额变化",
    "category_contributions": "品类下降贡献",
    "finish": "完成分析",
}


def read_json(path):
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def show_evaluation():
    checks = [
        ("SQL 基准题", read_json(EVAL / "golden_sql_results.json"), "passed"),
        ("Agent 端到端", read_json(EVAL / "agent_eval.json"), "cases"),
        ("只读策略", read_json(EVAL / "sql_policy_validation.json"), "rejections"),
    ]
    columns = st.columns(len(checks))
    for column, (label, document, key) in zip(columns, checks):
        if document is None:
            column.metric(label, "无记录")
            continue
        cases = document if isinstance(document, list) else document[key]
        column.metric(label, f"{sum(item['passed'] for item in cases)}/{len(cases)}", border=True)
    evaluation = checks[1][1]
    container_evaluation = read_json(EVAL / "agent_eval_docker.json")
    if container_evaluation:
        st.caption(f"Docker 容器回归：{container_evaluation['passed']}/{container_evaluation['total']} 道通过。")
    if evaluation:
        rows = [
            {"案例": case["id"], "通过": case["passed"], "模型调用": case.get("model_calls"),
             "Token": case.get("tokens"), "用时（秒）": case.get("elapsed_seconds")}
            for case in evaluation["cases"]
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True)
        st.caption("通过标准包括任务路径、工具结果与独立复算一致，以及报告引用查询 ID。")


def show_key_figures(trace):
    if trace.get("drivers"):
        drivers = trace["drivers"]
        for column, label, key in zip(
            st.columns(3),
            ("商品金额变化", *DRIVER_LABELS.values()),
            ("sales_change_brl", *DRIVER_LABELS),
        ):
            amount = float(drivers[key])
            tone = "decrease" if amount < 0 else "increase" if amount > 0 else "neutral"
            with column.container(key=f"metric_{tone}_{key}"):
                st.metric(label, f"R$ {amount:+,.2f}", border=True)
        return
    results = {item["task"]: item for item in trace["evidence"]}
    overview = results.get("overview")
    change = results.get("jul_aug_change")
    if overview and overview["rows"] and len(overview["rows"][0]) == 3:
        orders, sales, average = overview["rows"][0]
        for column, label, value in zip(
            st.columns(3),
            ("订单数", "商品金额", "平均每单商品金额"),
            (f"{orders:,}", f"R$ {sales:,.2f}", f"R$ {average:,.2f}"),
        ):
            column.metric(label, value, border=True)
    elif change and change["rows"]:
        value = change["rows"][0][0]
        st.metric("商品金额变化", f"R$ {value:+,.2f}", border=True)


def show_contributions(drivers):
    data = pd.DataFrame([
        {"驱动因素": label, "贡献金额": float(drivers[key])}
        for key, label in DRIVER_LABELS.items()
    ])
    magnitude = max(data["贡献金额"].abs().max(), 1) * 1.08
    bars = alt.Chart(data).mark_bar(size=20, cornerRadius=3).encode(
        x=alt.X("贡献金额:Q", title="贡献金额（BRL）",
                scale=alt.Scale(domain=[-magnitude, magnitude]),
                axis=alt.Axis(format="~s", tickCount=5, gridColor="#e3eaf4")),
        y=alt.Y("驱动因素:N", title=None, sort=list(DRIVER_LABELS.values()),
                axis=alt.Axis(labelLimit=180, domain=False, ticks=False, labelPadding=8)),
        color=alt.condition("datum['贡献金额'] < 0", alt.value("#cb581c"), alt.value("#176853")),
        tooltip=[alt.Tooltip("驱动因素:N"), alt.Tooltip("贡献金额:Q", title="BRL", format="+,.2f")],
    )
    zero = alt.Chart(pd.DataFrame({"zero": [0]})).mark_rule(color="#526485").encode(x="zero:Q")
    st.markdown("**商品金额变化贡献**")
    st.altair_chart((bars + zero).properties(height=96).configure_view(stroke=None), theme=None)


def show_business_summary(trace):
    drivers = trace["drivers"]
    periods = trace["periods"]
    change = Decimal(drivers["sales_change_brl"])
    volume, average = (Decimal(drivers[key]) for key in DRIVER_LABELS)
    direction = "减少" if change < 0 else "增加"
    headline = f"{periods['target']} 比 {periods['baseline']} 的商品金额{direction} **R$ {abs(change):,.2f}**。"
    if not change:
        headline = f"{periods['target']} 与 {periods['baseline']} 的商品金额持平。"

    if volume * average < 0:
        up = "订单量" if volume > 0 else "每单商品金额"
        down = "订单量" if volume < 0 else "每单商品金额"
        explanation = f"{up}上升，{down}下降，两项影响相互抵消。"
        if change:
            explanation += f"{up if change > 0 else down}的影响更大。"
    elif abs(volume) == abs(average):
        explanation = "订单量和每单商品金额没有贡献变化。" if not change else "订单量和每单商品金额各贡献了一半。"
    else:
        driver, impact = ("订单量", volume) if abs(volume) > abs(average) else ("每单商品金额", average)
        movement = "下降" if impact < 0 else "上升"
        explanation = f"**{driver}{movement}**是主要影响项，约占本次金额变化的 **{abs(impact / change):.0%}**。"

    next_step = "持续对比后续完整月份，观察订单量和每单金额的变化是否延续。"
    if change < 0:
        evidence = {item["task"]: item["rows"] for item in trace["evidence"]}
        order_rows = evidence.get("category_order_declines", [])
        category_rows = order_rows or evidence.get("category_contributions", [])
        seller_rows = evidence.get("seller_order_declines") or evidence.get("seller_sales_declines") or []
        if category_rows:
            category, delta = category_rows[0]
            name = CATEGORY_NAMES.get(category, f"`{category}`") if category else "未分类商品"
            decline = f"{abs(delta):,} 单" if order_rows else f"R$ {abs(delta):,.2f}"
            scope = f"**{name}**（减少 {decline}）"
            if seller_rows:
                scope += "及其中降幅最大的卖家，卖家明细见完整报告"
            next_step = f"优先排查{scope}。结合库存、流量和促销记录确认原因。"
        else:
            next_step = "先检查品类明细，再结合库存、流量和促销记录确认原因。"

    coverage = (trace.get("data_purchase_end") or OLIST_ARCHIVE_END)[:10]
    with st.container(key="business_summary", border=True):
        st.subheader("经营摘要", anchor=False)
        st.caption(f"Olist 历史快照 · 订单数据覆盖至 {coverage} · 分析仅使用所选完整月份")
        st.markdown(f"**发生了什么**  \n{headline}")
        st.markdown(f"**主要差在哪**  \n{explanation}")
        st.markdown(f"**下一步看哪里**  \n{next_step}")
        st.caption("贡献按订单量和每单商品金额的变化拆算。确认业务原因需要额外证据。")


def show_trace(trace, *, show_summary=True):
    st.subheader("分析结果")
    failure = trace.get("execution_error")
    if failure:
        st.error(failure["message"])
    review = trace.get("docker_review")
    if review:
        if review["passed"]:
            st.success(f"Docker 容器复核通过 · {len(review['checks'])} 项查询")
        else:
            st.error("Docker 复算发现不一致，请查看执行证据。")
    periods = trace.get("periods")
    if periods:
        st.caption(f"{periods['baseline']} → {periods['target']}")
    elif trace.get("scenario") and any(item["task"] in {"jul_aug_change", "monthly_drivers"} for item in trace["evidence"]):
        st.caption(trace["scenario"])
    if show_summary:
        if trace.get("drivers") and not failure and trace.get("status") != "review_mismatch":
            show_business_summary(trace)
        show_key_figures(trace)
    result_tab, evidence_tab, eval_tab = st.tabs(["分析报告", "执行证据", "评测"])
    with result_tab:
        with st.container(border=True, key="result_panel"):
            if show_summary and trace.get("drivers"):
                show_contributions(trace["drivers"])
                st.divider()
            st.markdown(trace["answer"])
            st.download_button("下载分析报告", trace["answer"], "commercelens-analysis.md", "text/markdown")
    with evidence_tab:
        if trace.get("report_validation"):
            verified = trace["report_validation"]["model_fields_match"]
            st.caption("模型报告字段通过核验。" if verified else "模型报告字段未通过核验，已用查询证据生成报告。")
        if review:
            with st.expander("Docker 容器复核", expanded=True):
                st.caption(f"容器 {review['container_id'][:12]} · 断网 · {review['executor']}")
                st.dataframe(pd.DataFrame(review["checks"]), hide_index=True)
        st.caption(f"实际执行 {len(trace['evidence'])} 条查询。展开可查看 SQL 和返回结果。")
        decisions = pd.DataFrame([
            {"步骤": index, "任务": TASK_LABELS.get(item["task"], item["task"]), "规划理由": item["reason"]}
            for index, item in enumerate(trace["decisions"], start=1)
        ])
        st.dataframe(decisions, hide_index=True)
        for item in trace["evidence"]:
            title = TASK_LABELS.get(item["task"], item["task"])
            with st.expander(title):
                st.caption(f"查询 ID：{item['query_id']}")
                st.dataframe(pd.DataFrame(item["rows"], columns=item["columns"]), hide_index=True)
                st.code(item["sql"], language="sql")
        st.download_button("下载完整轨迹", json.dumps(trace, ensure_ascii=False, indent=2),
                           "commercelens-trace.json", "application/json")
    with eval_tab:
        show_evaluation()


def show_pilot():
    st.header("诊断试点")
    cases = read_json(EVAL / "bi_comparison_pilot.json")
    if not cases:
        st.info("目前没有诊断试点记录。")
        return

    def period_label(case):
        periods = case["periods"]
        return f"{periods['baseline']} → {periods['target']}"

    rows = pd.DataFrame([
        {"案例": case["case"], "基准月 → 目标月": period_label(case),
         "Agent（秒）": case["agent_seconds"], "固定 SQL（秒）": case["fixed_sql_seconds"],
         "Agent 数值正确": case["agent_numeric_correct"],
         "固定 SQL 数值正确": case["fixed_sql_correct"],
         "Docker 复核通过": case["docker_review_passed"]}
        for case in cases
    ])
    with st.expander("查看 Agent 与固定 SQL 的评测对照"):
        st.dataframe(rows, hide_index=True, column_config={
            "Agent（秒）": st.column_config.NumberColumn(format="%.2f"),
            "固定 SQL（秒）": st.column_config.NumberColumn(format="%.2f"),
        })
        st.caption("Agent 用时包含规划、查询、报告和 Docker 复核。固定 SQL 已有下钻路径，仅计查询执行时间。人工计时待测。")
    cases_by_id = {case["case"]: case for case in cases}
    selected = st.selectbox("查看试点报告", list(cases_by_id),
                            format_func=lambda case_id: f"{case_id} · {period_label(cases_by_id[case_id])}")
    case = cases_by_id[selected]
    trace = read_json(ARTIFACTS / "phase2" / Path(case["trace"].replace("\\", "/")).name)
    if trace is None:
        st.warning("本地缺少该案例的分析轨迹。")
        return
    show_trace(trace)


def show_question_result(trace):
    if trace.get("execution_error") or trace.get("status") == "review_mismatch":
        st.error(trace["answer"])
        with st.expander("查看执行记录"):
            show_trace(trace)
        return
    if not trace.get("evidence"):
        st.warning("这次查询没有返回可用结果。")
        return
    with st.container(border=True, key="question_answer"):
        st.subheader("答案")
        if trace.get("drivers"):
            drivers = trace["drivers"]
            show_business_summary(trace)
            show_key_figures(trace)
            show_contributions(drivers)
        else:
            st.markdown(trace["answer"])
        review = trace.get("docker_review")
        if review and review["passed"]:
            st.caption(f"已通过 Docker 独立复算 · {len(review['checks'])} 项查询")
        with st.expander("查看完整报告、SQL 和评测"):
            show_trace(trace, show_summary=False)


def run_business_question(request):
    command = [sys.executable, str(SCRIPTS / "phase2_planner.py"), request.prompt, "--docker-review"]
    if request.comparison:
        command.extend(["--baseline-month", request.comparison.baseline,
                        "--target-month", request.comparison.target, "--diagnosis"])
    result = subprocess.run(command, capture_output=True, encoding="utf-8",
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=300)
    if result.returncode:
        LOGGER.error("Business question worker exited with code %s\n%s", result.returncode, result.stderr)
        raise RuntimeError("分析进程未完成。")
    return read_json(Path(result.stdout.strip().splitlines()[-1]))


def show_questions():
    with st.container(key="ask_workspace"):
        st.markdown(
            '<div class="ask-intro"><h1>经营数据，直接问</h1>'
            '<p>看销售涨跌、整体订单和畅销品类。先读经营摘要，再按需查看查询证据。</p></div>',
            unsafe_allow_html=True,
        )
        with st.form("business_question", border=True):
            question = st.text_area("你的问题", key="business_question_text",
                                    placeholder=EXAMPLES["销售变化"], height=88, max_chars=250)
            submitted = st.form_submit_button("开始分析", type="primary", icon=":material/arrow_upward:")
        for column, (label, example) in zip(st.columns(len(EXAMPLES)), EXAMPLES.items()):
            column.button(label, width="stretch", on_click=st.session_state.update,
                          kwargs={"business_question_text": example})
        st.caption("数据来源为公开 Olist 样本。两月对比请写明月份和年份。")
        st.button("查看离线演示", icon=":material/play_circle:", on_click=st.session_state.update,
                  kwargs={"workspace_mode": "评测与对照"})
        if not (ARTIFACTS / "phase1/olist.duckdb").is_file():
            st.info("实时问数需要先准备本地 Olist 数据。")
            return

        if submitted:
            st.session_state.pop("question_result", None)
            try:
                profile = read_json(ARTIFACTS / "phase1/data_profile.json")
                if not profile:
                    raise ValueError("本地 Olist 数据尚未就绪，请先生成数据概况。")
                request = interpret_question(question, profile["purchase_range"])
            except ValueError as error:
                st.info(str(error))
                return
            with st.spinner("正在查询数据并复算结果…"):
                try:
                    st.session_state["question_result"] = (question, run_business_question(request))
                except Exception as error:
                    LOGGER.exception("Business question analysis failed")
                    st.error(f"分析未完成（{type(error).__name__}）。请检查模型连接和 Docker Desktop 后重试。")
        if "question_result" in st.session_state:
            submitted_question, trace = st.session_state["question_result"]
            st.text(submitted_question)
            show_question_result(trace)


def main():
    st.set_page_config(page_title="CommerceLens · Olist 分析", layout="wide")
    st.html(SCRIPTS / "demo_theme.css")
    st.html('<header class="commerce-brand">CommerceLens</header>')
    with st.container(key="workspace_navigation"):
        mode = st.radio("工作区", ["业务问数", "历史报告", "评测与对照", "高级分析"],
                        horizontal=True, label_visibility="collapsed", key="workspace_mode")
    if mode == "业务问数":
        show_questions()
        return
    if mode == "评测与对照":
        show_pilot()
        return
    st.sidebar.header("分析设置")
    if mode == "历史报告":
        paths = sorted((ARTIFACTS / "phase2").glob("planner_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        if not paths:
            st.info("目前没有可回放的分析记录。")
            show_evaluation()
            return
        traces = {path: read_json(path) for path in paths}
        def record_label(candidate):
            trace = traces[candidate]
            first = next(iter(trace["evidence"]), {})
            task = first.get("task")
            label = TASK_LABELS.get(task, "历史分析")
            periods = trace.get("periods")
            if periods:
                return f"{periods['baseline']} → {periods['target']} · {candidate.stem[-6:]}"
            return f"{label} · {candidate.stem[-8:]}"

        path = st.sidebar.selectbox("分析记录", paths, format_func=record_label)
        st.sidebar.caption(traces[path]["question"])
        show_trace(traces[path])
        return

    scenario = st.sidebar.selectbox("分析任务", list(SCENARIOS))
    docker_review = st.sidebar.checkbox("Docker 容器复核", value=True)
    comparison = None
    if scenario in ("商品金额变化诊断", "销售下降与品类下钻", "增长场景对照"):
        profile = read_json(ARTIFACTS / "phase1/data_profile.json")
        months = available_months(profile["purchase_range"]) if profile else []
        if len(months) < 2:
            st.error("数据概况缺少可比较的完整月份。")
            return
        defaults = ("2018-08", "2018-07") if SCENARIOS[scenario][1] else ("2018-07", "2018-08")
        baseline = st.sidebar.selectbox("基准月", months,
                                        index=months.index(defaults[0]) if defaults[0] in months else 0,
                                        key=f"baseline_{scenario}")
        targets = [month for month in months if month != baseline]
        target = st.sidebar.selectbox("目标月", targets,
                                      index=targets.index(defaults[1]) if defaults[1] in targets else 0,
                                      key=f"target_{scenario}_{baseline}")
        comparison = Comparison(baseline, target)
        st.sidebar.caption("金额变化 = 目标月 − 基准月。首尾不完整月份已排除。")
    selection = (scenario, docker_review, comparison)
    st.sidebar.caption("真实分析会将选定问题与公开 Olist 的聚合结果发送给已配置的 DeepSeek API。")
    if st.sidebar.button("运行分析", type="primary"):
        question, reverse = SCENARIOS[scenario]
        from phase2_planner import run

        with st.spinner("正在规划、查询并生成分析…"):
            try:
                path = asyncio.run(run(question, reverse if comparison is None else False,
                                       docker_review=docker_review, comparison=comparison,
                                       diagnosis=scenario == "商品金额变化诊断"))
                st.session_state["live_trace"] = read_json(path)
                st.session_state["live_selection"] = selection
            except Exception as error:
                st.session_state.pop("live_trace", None)
                st.error(f"分析未完成（{type(error).__name__}）。请检查模型连接、本地数据及 Docker Desktop。")
    if st.session_state.get("live_selection") == selection and "live_trace" in st.session_state:
        show_trace(st.session_state["live_trace"])
    else:
        st.info("选择分析任务并点击「运行分析」，即可查看报告和查询证据。")


if __name__ == "__main__":
    main()
