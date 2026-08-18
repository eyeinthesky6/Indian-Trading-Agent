import unittest

from ita.tradeplan import build_trade_plan


class TradePlanTests(unittest.TestCase):
    def test_valid_long_plan(self):
        plan = build_trade_plan(
            symbol="RELIANCE",
            side="long",
            current_price=100,
            entry_low=99,
            entry_high=101,
            stop=95,
            targets=[110, 115],
            capital=100000,
        )
        self.assertEqual(plan["status"], "actionable_candidate")
        self.assertEqual(plan["reward_to_risk"][0], 2.0)
        self.assertFalse(plan["execution"]["allowed"])
        self.assertGreater(plan["position_sizing"]["quantity"], 0)

    def test_bad_stop_rejected_in_packet(self):
        plan = build_trade_plan(
            symbol="X",
            side="long",
            current_price=100,
            entry_low=99,
            entry_high=101,
            stop=100,
            targets=[110],
        )
        self.assertEqual(plan["status"], "invalid")
        self.assertTrue(plan["reasons_not_to_trade"])

    def test_minimum_reward_risk_is_not_hidden_constant(self):
        plan = build_trade_plan(
            symbol="X",
            side="long",
            current_price=100,
            entry_low=99,
            entry_high=101,
            stop=95,
            targets=[110, 115],
            min_reward_to_risk=3.5,
        )
        self.assertEqual(plan["status"], "invalid")
        self.assertIn("3.50R", plan["reasons_not_to_trade"][0])
        self.assertEqual(plan["decision_thresholds"]["min_reward_to_risk"], 3.5)


if __name__ == "__main__":
    unittest.main()
