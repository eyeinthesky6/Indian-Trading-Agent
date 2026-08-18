import unittest

from ita.indicators import technical_snapshot
from ita.regime import classify_regime


class IndicatorTests(unittest.TestCase):
    def test_uptrend_snapshot_and_regime(self):
        closes = [100 + i * 0.8 for i in range(70)]
        highs = [x + 1.2 for x in closes]
        lows = [x - 1.0 for x in closes]
        snap = technical_snapshot(closes, highs, lows)
        self.assertEqual(snap["trend"], "up")
        self.assertGreater(snap["rsi"], 50)
        regime = classify_regime(snap)
        self.assertEqual(regime["direction"], "trending_up")

    def test_mismatched_ohlc_rejected(self):
        with self.assertRaises(ValueError):
            technical_snapshot([1, 2, 3], [1, 2], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
