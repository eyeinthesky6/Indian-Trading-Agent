from __future__ import annotations

from math import isfinite


def _number(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def derive_long_swing_setup(snapshot: dict, regime: dict) -> dict:
    """Derive one conservative long-only Level 1 cash-equity setup.

    Level 1 deliberately avoids inventing short-selling/product eligibility from
    EOD cash-equity data. A valid result may be `no_trade`; the caller decides
    whether a derived setup is only a watch or has triggered.
    """
    latest = _number(snapshot.get("latest_close"))
    sma20 = _number(snapshot.get("sma_fast"))
    sma50 = _number(snapshot.get("sma_slow"))
    atr = _number(snapshot.get("atr"))
    atr_pct = _number(snapshot.get("atr_pct"))
    high20 = _number(snapshot.get("high_20d"))
    low20 = _number(snapshot.get("low_20d"))
    rsi = _number(snapshot.get("rsi"))
    volume_ratio = _number(snapshot.get("volume_vs_20d"))
    missing = [
        name
        for name, value in {
            "latest_close": latest,
            "sma_fast": sma20,
            "sma_slow": sma50,
            "atr": atr,
            "high_20d": high20,
            "low_20d": low20,
            "rsi": rsi,
        }.items()
        if value is None
    ]
    if missing:
        return {
            "status": "no_trade",
            "reason": f"insufficient technical state: missing {', '.join(missing)}",
            "setup": None,
        }
    assert latest is not None and sma20 is not None and sma50 is not None
    assert atr is not None and high20 is not None and low20 is not None and rsi is not None

    if atr_pct is not None and atr_pct >= 6.0:
        return {"status": "no_trade", "reason": f"ATR {atr_pct:.2f}% is too high for the default Level 1 geometry", "setup": None}
    if rsi >= 82.0:
        return {"status": "no_trade", "reason": f"RSI {rsi:.2f} is too extended for a new long setup", "setup": None}
    if volume_ratio is not None and volume_ratio < 0.25:
        return {"status": "no_trade", "reason": f"latest volume is only {volume_ratio:.2f}x the 20-session average", "setup": None}

    direction = str(regime.get("direction") or "range_or_transition")
    rationale: list[str] = []
    risks: list[str] = []

    if direction == "trending_up":
        near_high = latest >= high20 * 0.98
        if near_high:
            setup_name = "20-session breakout continuation"
            entry_low = high20
            entry_high = high20 + max(0.25 * atr, high20 * 0.002)
            stop = min(sma20 - 0.5 * atr, entry_low - 1.25 * atr)
            rationale.extend([
                "price, 20-session average and 50-session average are positively ordered",
                "price is close enough to the 20-session high to define a breakout trigger",
            ])
            risks.append("a breakout can fail quickly if price closes back below the prior range")
        else:
            setup_name = "uptrend pullback to 20-session mean"
            entry_low = max(sma20 - 0.35 * atr, low20)
            entry_high = sma20 + 0.35 * atr
            stop = min(low20 - 0.25 * atr, sma20 - 1.5 * atr)
            rationale.extend([
                "the longer trend is positive but price is not at a fresh breakout level",
                "the 20-session mean provides a conditional pullback zone rather than a chase entry",
            ])
            risks.append("momentum can continue lower through the moving-average pullback zone")
        entry_condition = "cross_above_zone" if near_high else "within_zone"
    elif direction == "trending_down":
        setup_name = "conditional 20-session trend reclaim"
        entry_low = sma20 - 0.25 * atr
        entry_high = sma20 + 0.25 * atr
        stop = min(entry_low - 1.25 * atr, latest - 0.5 * atr)
        entry_condition = "cross_above_zone"
        rationale.extend([
            "the current trend is down, so Level 1 does not buy current weakness",
            "a reclaim of the 20-session mean is required before a long candidate exists",
        ])
        risks.append("the broader downtrend can resume even after a temporary reclaim")
    else:
        setup_name = "20-session range breakout"
        entry_low = high20
        entry_high = high20 + max(0.25 * atr, high20 * 0.002)
        stop = min(sma20 - 0.5 * atr, high20 - 1.5 * atr)
        entry_condition = "cross_above_zone"
        rationale.extend([
            "trend and momentum are not cleanly aligned",
            "Level 1 waits for price to clear the 20-session range instead of guessing inside it",
        ])
        risks.append("range breakouts frequently fail without follow-through")

    representative_entry = (entry_low + entry_high) / 2.0
    if stop <= 0 or stop >= entry_low:
        return {"status": "no_trade", "reason": "derived stop geometry is invalid", "setup": None}

    risk = representative_entry - stop
    technical_targets: list[float] = []
    if sma50 > representative_entry:
        technical_targets.append(sma50)
    technical_targets.extend([representative_entry + 2.0 * risk, representative_entry + 3.0 * risk])
    targets = sorted({round(value, 4) for value in technical_targets if value > representative_entry})
    if not targets:
        return {"status": "no_trade", "reason": "could not derive a positive target", "setup": None}

    if latest > entry_high + 0.75 * atr:
        return {
            "status": "no_trade",
            "reason": "price is already too far beyond the derived trigger; Level 1 will not chase",
            "setup": None,
        }

    risks.extend([
        "EOD data cannot describe intraday liquidity or gap risk at the next session open",
        "corporate actions or exceptional events can make purely technical geometry misleading",
    ])
    return {
        "status": "setup",
        "reason": None,
        "setup": setup_name,
        "side": "long",
        "entry_low": round(entry_low, 4),
        "entry_high": round(entry_high, 4),
        "entry_condition": entry_condition,
        "stop": round(stop, 4),
        "targets": targets,
        "target_basis": "technical level when available plus deterministic 2R/3R projections",
        "rationale": rationale,
        "risks": risks,
    }
