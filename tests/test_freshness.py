import unittest

from ita.freshness import assess_data_freshness
from ita.tradeplan import build_trade_plan


class FreshnessTests(unittest.TestCase):
    def test_fresh_clock_age(self):
        out = assess_data_freshness("2026-08-10T15:29:00+05:30", as_of_timestamp="2026-08-10T15:30:00+05:30", max_age_minutes=5)
        self.assertEqual(out["status"], "fresh")
        self.assertTrue(out["actionable"])

    def test_stale_data_blocks_actionable_plan(self):
        plan = build_trade_plan(
            symbol="X", side="long", current_price=100, entry_low=99, entry_high=101, stop=95, targets=[110],
            data_timestamp="2026-08-10T15:30:00+05:30", freshness_as_of="2026-08-11T15:30:00+05:30", max_data_age_minutes=60
        )
        self.assertEqual(plan["status"], "invalid")
        self.assertTrue(any("freshness" in x for x in plan["reasons_not_to_trade"]))


if __name__ == "__main__":
    unittest.main()
