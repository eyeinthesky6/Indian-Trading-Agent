import unittest

from ita.portfolio import portfolio_risk_summary


class PortfolioTests(unittest.TestCase):
    def test_concentration_warning(self):
        out = portfolio_risk_summary(100000, [
            {"symbol": "A", "market_value": 45000, "sector": "Bank", "side": "long"},
            {"symbol": "B", "market_value": 10000, "sector": "IT", "side": "long"},
        ])
        self.assertEqual(out["gross_exposure_pct"], 55.0)
        self.assertTrue(any("sector concentration" in x for x in out["warnings"]))


if __name__ == "__main__":
    unittest.main()
