import os
import tempfile
import unittest
from datetime import date

from ita.marketdata import BhavcopyHistoryProvider


@unittest.skipUnless(os.getenv("ITA_NETWORK_SMOKE") == "1", "opt-in network smoke")
class Level1NetworkSmokeTests(unittest.TestCase):
    def test_real_nse_udiff_file_parses_reliance(self):
        # NSE's public All Reports page lists this exact UDiFF file for 13-Jul-2026.
        with tempfile.TemporaryDirectory() as cache:
            provider = BhavcopyHistoryProvider(cache_dir=cache, timeout=45)
            bar = provider._bar_for_date("RELIANCE", "NSE", date(2026, 7, 13))
            self.assertIsNotNone(bar)
            self.assertEqual(bar.symbol, "RELIANCE")
            self.assertEqual(bar.exchange, "NSE")
            self.assertEqual(bar.trade_date, "2026-07-13")
            self.assertGreater(bar.close, 0)
            self.assertGreaterEqual(bar.high, bar.close)
            self.assertLessEqual(bar.low, bar.close)
            self.assertEqual(bar.source, "nse_udiff_bhavcopy")


if __name__ == "__main__":
    unittest.main()
