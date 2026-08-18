from __future__ import annotations

from math import sqrt
from statistics import pstdev
from typing import Iterable, Sequence


def _floats(values: Iterable[float]) -> list[float]:
    out = [float(v) for v in values]
    if not out:
        raise ValueError("series must not be empty")
    if any(v <= 0 for v in out):
        raise ValueError("price series must contain positive values")
    return out


def sma(values: Sequence[float], period: int) -> float | None:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) < period:
        return None
    window = values[-period:]
    return sum(window) / period


def ema(values: Sequence[float], period: int) -> float | None:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) < period:
        return None
    alpha = 2.0 / (period + 1.0)
    value = sum(values[:period]) / period
    for price in values[period:]:
        value = alpha * price + (1 - alpha) * value
    return value


def rsi(values: Sequence[float], period: int = 14) -> float | None:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) <= period:
        return None
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = ((period - 1) * avg_gain + gain) / period
        avg_loss = ((period - 1) * avg_loss + loss) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> float | None:
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("highs, lows and closes must have equal length")
    if len(closes) < period + 1:
        return None
    true_ranges: list[float] = []
    for i in range(1, len(closes)):
        high = float(highs[i])
        low = float(lows[i])
        prev_close = float(closes[i - 1])
        true_ranges.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
    value = sum(true_ranges[:period]) / period
    for tr in true_ranges[period:]:
        value = ((period - 1) * value + tr) / period
    return value


def pct_change(values: Sequence[float], periods: int) -> float | None:
    if periods <= 0:
        raise ValueError("periods must be positive")
    if len(values) <= periods:
        return None
    start = values[-periods - 1]
    end = values[-1]
    return (end / start - 1.0) * 100.0


def realised_volatility(values: Sequence[float], period: int = 20, annualisation: int = 252) -> float | None:
    if len(values) <= period:
        return None
    returns = [(values[i] / values[i - 1]) - 1.0 for i in range(len(values) - period, len(values))]
    return pstdev(returns) * sqrt(annualisation) * 100.0


def _zone_rsi(value: float | None) -> str | None:
    if value is None:
        return None
    if value >= 70:
        return "overbought"
    if value <= 30:
        return "oversold"
    if value >= 55:
        return "bullish"
    if value <= 45:
        return "bearish"
    return "neutral"


def technical_snapshot(
    closes: Iterable[float],
    highs: Iterable[float] | None = None,
    lows: Iterable[float] | None = None,
    volumes: Iterable[float] | None = None,
    fast_period: int = 20,
    slow_period: int = 50,
    rsi_period: int = 14,
    atr_period: int = 14,
) -> dict:
    """Return a deterministic technical snapshot.

    The function intentionally describes state; it does not emit a buy/sell recommendation.
    """
    c = _floats(closes)
    h = [float(v) for v in highs] if highs is not None else None
    l = [float(v) for v in lows] if lows is not None else None
    v = [float(x) for x in volumes] if volumes is not None else None
    if h is not None and len(h) != len(c):
        raise ValueError("highs must match closes length")
    if l is not None and len(l) != len(c):
        raise ValueError("lows must match closes length")
    if v is not None and len(v) != len(c):
        raise ValueError("volumes must match closes length")

    fast = sma(c, fast_period)
    slow = sma(c, slow_period)
    rsi_value = rsi(c, rsi_period)
    atr_value = atr(h, l, c, atr_period) if h is not None and l is not None else None
    latest = c[-1]
    trend = "unknown"
    if fast is not None and slow is not None:
        if latest > fast > slow:
            trend = "up"
        elif latest < fast < slow:
            trend = "down"
        else:
            trend = "mixed"

    volume_ratio = None
    if v is not None and len(v) >= 20:
        avg_volume = sum(v[-20:]) / 20.0
        if avg_volume:
            volume_ratio = v[-1] / avg_volume

    level_high = max(h[-20:]) if h is not None and len(h) >= 20 else (max(c[-20:]) if len(c) >= 20 else None)
    level_low = min(l[-20:]) if l is not None and len(l) >= 20 else (min(c[-20:]) if len(c) >= 20 else None)

    return {
        "latest_close": round(latest, 4),
        "sma_fast": round(fast, 4) if fast is not None else None,
        "sma_slow": round(slow, 4) if slow is not None else None,
        "trend": trend,
        "rsi": round(rsi_value, 2) if rsi_value is not None else None,
        "rsi_zone": _zone_rsi(rsi_value),
        "momentum_5d_pct": round(pct_change(c, 5), 2) if pct_change(c, 5) is not None else None,
        "momentum_20d_pct": round(pct_change(c, 20), 2) if pct_change(c, 20) is not None else None,
        "realised_vol_20d_pct": round(realised_volatility(c, 20), 2) if realised_volatility(c, 20) is not None else None,
        "atr": round(atr_value, 4) if atr_value is not None else None,
        "atr_pct": round((atr_value / latest) * 100.0, 2) if atr_value is not None else None,
        "volume_vs_20d": round(volume_ratio, 2) if volume_ratio is not None else None,
        "high_20d": round(level_high, 4) if level_high is not None else None,
        "low_20d": round(level_low, 4) if level_low is not None else None,
        "distance_from_20d_high_pct": round((latest / level_high - 1.0) * 100.0, 2) if level_high else None,
        "distance_from_20d_low_pct": round((latest / level_low - 1.0) * 100.0, 2) if level_low else None,
        "observations": len(c),
        "parameters": {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "rsi_period": rsi_period,
            "atr_period": atr_period,
        },
    }
