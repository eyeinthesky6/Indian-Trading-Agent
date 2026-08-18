from __future__ import annotations


def classify_regime(snapshot: dict) -> dict:
    """Classify price regime from a technical snapshot with explicit rationale."""
    trend = snapshot.get("trend")
    mom = snapshot.get("momentum_20d_pct")
    atr_pct = snapshot.get("atr_pct")
    vol = snapshot.get("realised_vol_20d_pct")

    reasons: list[str] = []
    if trend == "up" and (mom is None or mom > 0):
        direction = "trending_up"
        reasons.append("price/fast/slow averages are positively ordered")
        if mom is not None:
            reasons.append(f"20-session momentum is {mom:.2f}%")
    elif trend == "down" and (mom is None or mom < 0):
        direction = "trending_down"
        reasons.append("price/fast/slow averages are negatively ordered")
        if mom is not None:
            reasons.append(f"20-session momentum is {mom:.2f}%")
    else:
        direction = "range_or_transition"
        reasons.append("trend and momentum are not cleanly aligned")

    if atr_pct is None:
        volatility = "unknown"
    elif atr_pct >= 3.0:
        volatility = "high"
        reasons.append(f"ATR is {atr_pct:.2f}% of price")
    elif atr_pct >= 1.5:
        volatility = "normal"
        reasons.append(f"ATR is {atr_pct:.2f}% of price")
    else:
        volatility = "low"
        reasons.append(f"ATR is {atr_pct:.2f}% of price")

    if direction.startswith("trending") and volatility == "high":
        label = f"{direction}_high_vol"
    elif direction.startswith("trending"):
        label = direction
    elif volatility == "high":
        label = "volatile_transition"
    else:
        label = "range_or_transition"

    return {
        "regime": label,
        "direction": direction,
        "volatility": volatility,
        "realised_vol_20d_pct": vol,
        "rationale": reasons,
    }
