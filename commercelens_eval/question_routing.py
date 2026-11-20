"""Offline regression cases for the public Chinese question entry point."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analysis_periods import Comparison
from business_questions import EXAMPLES, interpret_question

PURCHASE_RANGE = ("2016-09-04", "2018-10-17")


class BusinessQuestionTests(unittest.TestCase):
    def test_home_examples(self):
        expected = ("comparison", "overview", "top_categories")
        for question, kind in zip(EXAMPLES.values(), expected, strict=True):
            with self.subTest(question=question):
                self.assertEqual(interpret_question(question, PURCHASE_RANGE).kind, kind)

    def test_comparison_direction(self):
        for question, comparison in (
            ("2018年8月比7月，销售额为什么下降？", Comparison("2018-07", "2018-08")),
            ("从2018-04到2018-02，商品金额变化了多少？", Comparison("2018-04", "2018-02")),
            ("2017年12月相较于11月的GMV降了多少？", Comparison("2017-11", "2017-12")),
        ):
            with self.subTest(question=question):
                self.assertEqual(interpret_question(question, PURCHASE_RANGE).comparison, comparison)

    def test_unsupported_questions_do_not_silently_change_scope(self):
        for question in (
            "利润是多少？", "2018年8月的订单量是多少？", "哪些品类的销售额最高，只看巴西圣保罗？",
            "8月比7月销售额变化了多少？", "2018-08比2018-08销售额变化了多少？",
            "2018-10比2018-09销售额变化了多少？",
        ):
            with self.subTest(question=question), self.assertRaises(ValueError):
                interpret_question(question, PURCHASE_RANGE)


if __name__ == "__main__":
    unittest.main()
