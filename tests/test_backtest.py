import unittest

from ita.backtest import backtest_ma_crossover


class BacktestTests(unittest.TestCase):
    def test_runs_and_reports_costs(self):
        closes = [100 + i * 0.25 for i in range(120)]
        out = backtest_ma_crossover(closes, fast_period=10, slow_period=30)
        self.assertGreater(out["final_equity"], 100000)
        self.assertGreaterEqual(out["trades"], 1)
        self.assertIn("execution_model", out["assumptions"])

    def test_requires_sufficient_history(self):
        with self.assertRaises(ValueError):
            backtest_ma_crossover([100] * 16, fast_period=5, slow_period=15)


if __name__ == "__main__":
    unittest.main()
