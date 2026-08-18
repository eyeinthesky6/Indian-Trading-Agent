import csv
import io
import tempfile
import unittest
from datetime import date
from zipfile import ZIP_DEFLATED, ZipFile

from ita.marketdata import BhavcopyHistoryProvider


FIELDS = [
    "Sgmt", "FinInstrmTp", "TckrSymb", "SctySrs", "TradDt",
    "OpnPric", "HghPric", "LwPric", "ClsPric", "TtlTradgVol",
]


def _csv_bytes(trade_date: str, exchange: str) -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    for idx, symbol in enumerate(("RELIANCE", "TCS")):
        close = 100.0 + idx * 50 + date.fromisoformat(trade_date).day
        writer.writerow(
            {
                "Sgmt": "CM",
                "FinInstrmTp": "STK",
                "TckrSymb": symbol,
                "SctySrs": "EQ" if exchange == "NSE" else "A",
                "TradDt": trade_date,
                "OpnPric": close - 1,
                "HghPric": close + 2,
                "LwPric": close - 2,
                "ClsPric": close,
                "TtlTradgVol": 100000 + idx,
            }
        )
    return output.getvalue().encode("utf-8")


def _zip(payload: bytes) -> bytes:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("bhavcopy.csv", payload)
    return buffer.getvalue()


def _fake_fetcher(url: str, _referer: str, _timeout: float) -> bytes:
    token = next(part for part in url.replace(".", "_").split("_") if len(part) == 8 and part.isdigit())
    trade_date = f"{token[:4]}-{token[4:6]}-{token[6:]}"
    if "NSE" in url:
        return _zip(_csv_bytes(trade_date, "NSE"))
    return _csv_bytes(trade_date, "BSE")


class Level1MarketDataTests(unittest.TestCase):
    def test_nse_history_is_generic_sorted_and_authoritative(self):
        with tempfile.TemporaryDirectory() as cache:
            provider = BhavcopyHistoryProvider(cache_dir=cache, fetcher=_fake_fetcher)
            history = provider.fetch_symbol_history(
                "RELIANCE", exchange="NSE", sessions=55, as_of="2026-08-18", max_calendar_days=60
            )
            self.assertEqual(history.symbol, "RELIANCE")
            self.assertEqual(history.exchange, "NSE")
            self.assertEqual(len(history.bars), 55)
            self.assertTrue(history.authoritative)
            self.assertEqual(history.source_name, "nse_udiff_bhavcopy")
            self.assertLess(history.bars[0].trade_date, history.bars[-1].trade_date)
            self.assertTrue(all(bar.symbol == "RELIANCE" for bar in history.bars))

    def test_same_provider_handles_another_symbol(self):
        with tempfile.TemporaryDirectory() as cache:
            provider = BhavcopyHistoryProvider(cache_dir=cache, fetcher=_fake_fetcher)
            history = provider.fetch_symbol_history(
                "TCS", exchange="NSE", sessions=55, as_of="2026-08-18", max_calendar_days=60
            )
            self.assertEqual(history.symbol, "TCS")
            self.assertEqual(len(history.bars), 55)

    def test_bse_plain_csv_path(self):
        with tempfile.TemporaryDirectory() as cache:
            provider = BhavcopyHistoryProvider(cache_dir=cache, fetcher=_fake_fetcher)
            history = provider.fetch_symbol_history(
                "RELIANCE", exchange="BSE", sessions=2, as_of="2026-08-18", max_calendar_days=2
            )
            self.assertEqual(history.exchange, "BSE")
            self.assertEqual(history.source_name, "bse_udiff_bhavcopy")
            self.assertEqual(len(history.bars), 2)


if __name__ == "__main__":
    unittest.main()
