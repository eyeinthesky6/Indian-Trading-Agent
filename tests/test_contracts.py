import unittest

from ita.contracts import validate_trade_packet
from ita.tradeplan import build_trade_plan


class ContractTests(unittest.TestCase):
    def test_generated_plan_contract(self):
        packet = build_trade_plan(
            symbol="X", side="long", current_price=100, entry_low=99, entry_high=101, stop=95, targets=[110],
            data_timestamp="2026-08-10T15:29:00+05:30", data_source="test feed",
            freshness_as_of="2026-08-10T15:30:00+05:30", max_data_age_minutes=5
        )
        self.assertTrue(validate_trade_packet(packet)["valid"])

    def test_execution_true_is_rejected(self):
        packet = {
            "schema_version":"1.0", "symbol":"X", "status":"watch", "horizon":"swing",
            "reasons_not_to_trade":[], "market_data":{}, "execution":{"allowed":True}
        }
        self.assertFalse(validate_trade_packet(packet)["valid"])

if __name__ == "__main__":
    unittest.main()
