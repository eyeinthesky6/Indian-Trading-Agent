import unittest

from ita.risk import position_size, reward_to_risk


class RiskTests(unittest.TestCase):
    def test_stop_based_position_size(self):
        out = position_size(100000, 100, 95, risk_fraction=0.01, max_position_fraction=0.25)
        self.assertEqual(out["quantity"], 200)
        self.assertEqual(out["actual_risk"], 1000.0)

    def test_exposure_cap_can_limit(self):
        out = position_size(100000, 1000, 990, risk_fraction=0.05, max_position_fraction=0.10)
        self.assertEqual(out["quantity"], 10)
        self.assertEqual(out["limiting_factor"], "exposure_cap")

    def test_reward_risk(self):
        self.assertAlmostEqual(reward_to_risk(100, 95, 110), 2.0)
        self.assertAlmostEqual(reward_to_risk(100, 105, 90, "short"), 2.0)


if __name__ == "__main__":
    unittest.main()
