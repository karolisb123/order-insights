import unittest
from datetime import date

from order_insights.cli import summarize, top_products, revenue_by_day, low_stock, sparkline


def make_orders():
    return [
        {"order_id": "1", "date": date(2026, 6, 1), "sku": "A", "product": "Widget", "quantity": 2, "price": 10.0},
        {"order_id": "1", "date": date(2026, 6, 1), "sku": "B", "product": "Gadget", "quantity": 1, "price": 5.0},
        {"order_id": "2", "date": date(2026, 6, 2), "sku": "A", "product": "Widget", "quantity": 3, "price": 10.0},
    ]


class TestSummarize(unittest.TestCase):
    def test_revenue_and_orders(self):
        s = summarize(make_orders())
        self.assertEqual(s["revenue"], 55.0)
        self.assertEqual(s["orders"], 2)
        self.assertEqual(s["units"], 6)
        self.assertAlmostEqual(s["aov"], 27.5)

    def test_empty(self):
        s = summarize([])
        self.assertEqual(s["revenue"], 0)
        self.assertEqual(s["aov"], 0)


class TestTopProducts(unittest.TestCase):
    def test_ranking(self):
        top = top_products(make_orders(), n=2)
        self.assertEqual(top[0][0], "A")  # Widget leads on revenue
        self.assertEqual(top[0][3], 50.0)


class TestRevenueByDay(unittest.TestCase):
    def test_grouping(self):
        daily = revenue_by_day(make_orders())
        self.assertEqual(daily[date(2026, 6, 1)], 25.0)
        self.assertEqual(daily[date(2026, 6, 2)], 30.0)


class TestLowStock(unittest.TestCase):
    def test_threshold(self):
        stock = {"A": 3, "B": 50}
        flagged = low_stock(stock, make_orders(), threshold=5)
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0][0], "A")


class TestSparkline(unittest.TestCase):
    def test_length(self):
        self.assertEqual(len(sparkline([1, 2, 3, 4])), 4)

    def test_empty(self):
        self.assertEqual(sparkline([]), "")


if __name__ == "__main__":
    unittest.main()
