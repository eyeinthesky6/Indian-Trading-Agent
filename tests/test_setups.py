import unittest

from ita.setups import derive_long_swing_setup
from ita.tradeplan import build_trade_plan


class SetupDerivationTests(unittest.TestCase):
    def test_breakout_uses_prior_range_and_can_trigger(self):
        snapshot = {
            "latest_close": 111.0,
            "sma_fast": 105.0,
            "sma_slow": 100.0,
            "atr": 2.0,
            "atr_pct": 1.8,
            "high_20d": 112.0,
            "low_20d": 96.0,
            "prior_high_20d": 110.0,
            "prior_low_20d": 96.0,
            "rsi": 64.0,
            "volume_vs_20d": 1.3,
        }
        regime = {"direction": "trending_up"}
        derived = derive_long_swing_setup(snapshot, regime)
        self.assertEqual(derived["status"], "setup")
        self.assertIn("prior-20-session breakout", derived["setup"])
        self.assertEqual(derived["entry_low"], 110.0)
        self.assertLessEqual(derived["entry_high"], snapshot["latest_close"])

        packet = build_trade_plan(
            symbol="RELIANCE",
            side="long",
            current_price=snapshot["latest_close"],
            entry_low=derived["entry_low"],
            entry_high=derived["entry_high"],
            stop=derived["stop"],
            targets=derived["targets"],
            entry_condition=derived["entry_condition"],
        )
        self.assertEqual(packet["status"], "actionable_candidate")
        self.assertEqual(packet["trigger_state"], "triggered")
        self.assertFalse(packet["execution"]["allowed"])


if __name__ == "__main__":
    unittest.main()
