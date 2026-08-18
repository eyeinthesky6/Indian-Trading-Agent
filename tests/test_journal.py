import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from ita.analyze import analyze_symbol
from ita.journal import DecisionJournal
from ita.marketdata import DailyBar, HistoryResult


class FakeHistoryProvider:
    def fetch_symbol_history(self, symbol, *, exchange, sessions, as_of, max_calendar_days):
        end = as_of if isinstance(as_of, date) else date.fromisoformat(str(as_of)[:10])
        start = end - timedelta(days=sessions - 1)
        bars = []
        for i in range(sessions):
            trade_date = start + timedelta(days=i)
            close = 120.0 - i * 0.45
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


class DecisionJournalTests(unittest.TestCase):
    def test_recorded_analysis_can_be_read_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.jsonl"
            result = analyze_symbol(
                "RELIANCE",
                provider=FakeHistoryProvider(),
                as_of="2026-08-18",
                capital=500000,
                record=True,
                journal_path=path,
            )
            self.assertTrue(path.exists())
            self.assertTrue(result["journal"]["recorded"])
            records = DecisionJournal(path).list()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["analysis_id"], result["analysis_id"])
            self.assertEqual(records[0]["status"], result["trade_packet"]["status"])
            self.assertEqual(records[0]["policy_id"], result["policy"]["id"])

    def test_journal_filters_by_symbol(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.jsonl"
            for symbol in ("RELIANCE", "TCS"):
                analyze_symbol(
                    symbol,
                    provider=FakeHistoryProvider(),
                    as_of="2026-08-18",
                    record=True,
                    journal_path=path,
                )
            records = DecisionJournal(path).list(symbol="TCS")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["symbol"], "TCS")


if __name__ == "__main__":
    unittest.main()
