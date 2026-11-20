"""Map supported business questions to the existing bounded analysis workflows."""
import re
import unicodedata
from dataclasses import dataclass

from analysis_periods import Comparison

EXAMPLES = {
    "销售变化": "2018年8月比7月，销售额为什么下降？",
    "整体经营": "整体销售额和订单量是多少？",
    "畅销品类": "哪些品类的销售额最高？",
}
MONTH = r"(?:20\d{2}年(?:0?[1-9]|1[0-2])月|20\d{2}-(?:0?[1-9]|1[0-2])|(?:0?[1-9]|1[0-2])月)"
METRIC = r"(?:销售额|销售金额|商品金额|商品销售额|gmv)"
MOVEMENT = r"(?:下降|下滑|减少|上涨|增长|增加|变化)"
CHANGE = (
    rf"(?:的)?(?:{METRIC}(?:"
    rf"(?:为什么|为何){MOVEMENT}|(?:变化|增加|减少|上涨|下滑|升|降)了多少|差了?多少|"
    r"怎么变了|怎么样|有何变化|变化如何|有(?:什么)?变化)"
    rf"|(?:为什么|为何){METRIC}{MOVEMENT}|销售(?:为什么|为何)(?:下降|下滑|增长))"
)
OVERVIEW_METRIC = rf"(?:{METRIC}|订单量|订单数|每单商品金额)"
OVERVIEW = (
    r"(?:看一下|看下|看看|告诉我)?(?:整体|全量|总体|历史|全部)?"
    rf"(?:经营总览|经营概况|的?{OVERVIEW_METRIC}(?:(?:和|与|及|、){OVERVIEW_METRIC})*(?:各)?(?:是)?多少)"
)
RANKING = (
    rf"(?:哪些品类(?:的)?{METRIC}(?:最高|排在前面)|品类{METRIC}排名|"
    rf"(?:{METRIC}最高|最畅销)的(?:前五个|前5个)?品类(?:有哪些|是什么)?)"
)


@dataclass(frozen=True)
class BusinessQuestion:
    kind: str
    prompt: str
    comparison: Comparison | None = None


def interpret_question(question, purchase_range):
    query = re.sub(r"[\s,，。?!？！]+", "", unicodedata.normalize("NFKC", question)).lower()
    if re.fullmatch(OVERVIEW, query):
        return BusinessQuestion("overview", "Report the all-time order count, item sales, and average item sales per order.")
    if re.fullmatch(RANKING, query):
        return BusinessQuestion("top_categories", "List the five categories with the highest all-time item sales.")

    for pattern, baseline_group, target_group in (
        (rf"(?:对比|比较)?({MONTH})(?:相比|相较于|相较|比|对比)({MONTH}){CHANGE}", 2, 1),
        (rf"从({MONTH})(?:到|至)({MONTH}){CHANGE}", 1, 2),
    ):
        match = re.fullmatch(pattern, query)
        if match is None:
            continue
        baseline_text, target_text = match.group(baseline_group, target_group)
        years = re.findall(r"20\d{2}", baseline_text + " " + target_text)
        if not years:
            raise ValueError("请至少写出一个月份的年份，例如「2018年8月比7月，销售额为什么下降？」")

        def month_value(value):
            parts = re.findall(r"\d+", value)
            return f"{parts[0] if len(parts) == 2 else years[0]}-{int(parts[-1]):02d}"

        comparison = Comparison(month_value(baseline_text), month_value(target_text))
        comparison.validate(purchase_range)
        return BusinessQuestion(
            "comparison",
            "Compare the two months' merchandise sales, explain the contributions of order volume and average merchandise per order, and drill down on a decline.",
            comparison,
        )
    raise ValueError("目前支持两月销售对比、全量经营指标和销售额最高的品类。可以点一个示例，再改成你的问题。")
