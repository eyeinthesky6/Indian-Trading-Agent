import unittest
from datetime import date, timedelta

from ita.analyze import analyze_symbol
from ita.marketdata import DailyBar, HistoryResult


class FakeHistoryProvider:
    def __init__(self, direction: str):
        self.direction = direction

    def fetch_symbol_history(self, symbol, *, exchange, sessions, as_of, max_calendar_days):
        end = as_of if isinstance(as_of, date) else date.fromisoformat(str(as_of)[:10])
        start = end - timedelta(days=sessions - 1)
        bars = []
        for i in range(sessions):
            trade_date = start + timedelta(days=i)
            if self.direction == "down":
                close = 120.0 - i * 0.45
            else:
                close = 80.0 + i * 0.55
            bars.append(
                DailyBar(
                    timestamp=f"{trade_date.isoformat()}T15:30:00+05:30",
                    trade_date=trade_date.isoformat(),
                    open=close - 0.4,
                    high=close + 1.0,
                    low=close - 1.0,
                    close=close,
                    volume=1_000_000 + i * 1000,
                    exchange=exchange,
                    symbol=symbol,
                    source=f"{exchange.lower()}_udiff_bhavcopy",
                )
            )
        return HistoryResult(
            symbol=symbol,
            exchange=exchange,
            bars=bars,
            source_name=f"{exchange.lower()}_udiff_bhavcopy",
            source_kind="exchange_public_report",
            authoritative=True,
            as_of_date=end.isoformat(),
            latest_trade_date=end.isoformat(),
            attempted_calendar_days=sessions,
            cache_dir="test-cache",
        )


class Level1AnalyzeTests(unittest.TestCase):
    def test_symbol_only_path_builds_complete_packet_without_ifma(self):
        result = analyze_symbol(
            "RELIANCE",
            provider=FakeHistoryProvider("down"),
            sessions=80,
            as_of="2026-08-18",
            capital=500000,
        )
        self.assertEqual(result["level"], 1)
        self.assertEqual(result["symbol"], "RELIANCE")
        self.assertTrue(result["analysis_id"].startswith("ita1_"))
        self.assertIn("fingerprint", result["policy"])
        self.assertEqual(result["market_data"]["source"], "nse_udiff_bhavcopy")
        self.assertTrue(result["market_data"]["authoritative"])
        self.assertEqual(result["regime"]["direction"], "trending_down")
        packet = result["trade_packet"]
        self.assertEqual(packet["analysis_id"], result["analysis_id"])
        self.assertEqual(packet["policy"]["id"], result["policy"]["id"])
        self.assertEqual(packet["status"], "watch")
        self.assertEqual(packet["trigger_state"], "waiting")
        self.assertFalse(packet["execution"]["allowed"])
        self.assertIsNotNone(packet["position_sizing"])

    def test_same_evidence_and_policy_produce_same_analysis_id(self):
        kwargs = dict(
            symbol="RELIANCE",
            provider=FakeHistoryProvider("down"),
            sessions=80,
            as_of="2026-08-18",
            capital=500000,
        )
        first = analyze_symbol(**kwargs)
        second = analyze_symbol(**kwargs)
        self.assertEqual(first["analysis_id"], second["analysis_id"])

    def test_policy_change_can_change_decision_and_analysis_id(self):
        default = analyze_symbol(
            "RELIANCE",
            provider=FakeHistoryProvider("down"),
            as_of="2026-08-18",
        )
        strict = analyze_symbol(
            "RELIANCE",
            provider=FakeHistoryProvider("down"),
            as_of="2026-08-18",
            policy={"name": "strict-volume", "version": "1", "min_volume_ratio": 2.0},
        )
        self.assertEqual(default["trade_packet"]["status"], "watch")
        self.assertEqual(strict["trade_packet"]["status"], "no_trade")
        self.assertNotEqual(default["analysis_id"], strict["analysis_id"])
        self.assertIn("policy minimum", strict["trade_packet"]["reasons_not_to_trade"][0])

    def test_overextended_uptrend_can_return_no_trade(self):
        result = analyze_symbol(
            "TCS",
            provider=FakeHistoryProvider("up"),
            sessions=80,
            as_of="2026-08-18",
        )
        self.assertEqual(result["technical_snapshot"]["trend"], "up")
        self.assertEqual(result["trade_packet"]["status"], "no_trade")
        self.assertIn("RSI", result["trade_packet"]["reasons_not_to_trade"][0])

    def test_level1_rejects_intraday_horizon(self):
        with self.assertRaises(ValueError):
            analyze_symbol(
                "INFY",
                horizon="intraday",
                provider=FakeHistoryProvider("down"),
                sessions=80,
                as_of="2026-08-18",
            )


if __name__ == "__main__":
    unittest.main()
