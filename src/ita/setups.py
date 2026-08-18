from __future__ import annotations

from math import isfinite

from .policy import Level1Policy, load_level1_policy


def _number(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def derive_long_swing_setup(
    snapshot: dict,
    regime: dict,
    policy: Level1Policy | dict | None = None,
) -> dict:
    """Derive one conservative long-only Level 1 cash-equity setup.

    Level 1 deliberately avoids inventing short-selling/product eligibility from
    EOD cash-equity data. Breakout triggers use the prior 20-session range,
    excluding the current bar, so a breakout can actually trigger instead of
    moving its own threshold upward. All thresholds/geometry come from the
    explicit Level1Policy rather than hidden constants in this function.
    """
    p = load_level1_policy(policy)
    latest = _number(snapshot.get("latest_close"))
    sma20 = _number(snapshot.get("sma_fast"))
    sma50 = _number(snapshot.get("sma_slow"))
    atr = _number(snapshot.get("atr"))
    atr_pct = _number(snapshot.get("atr_pct"))
    high20 = _number(snapshot.get("high_20d"))
    low20 = _number(snapshot.get("low_20d"))
    prior_high20 = _number(snapshot.get("prior_high_20d")) or high20
    prior_low20 = _number(snapshot.get("prior_low_20d")) or low20
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
            "prior_high_20d": prior_high20,
            "prior_low_20d": prior_low20,
            "rsi": rsi,
        }.items()
        if value is None
    ]
    if missing:
        return {
            "status": "no_trade",
            "reason": f"insufficient technical state: missing {', '.join(missing)}",
            "setup": None,
            "policy_id": p.policy_id,
        }
    assert latest is not None and sma20 is not None and sma50 is not None
    assert atr is not None and high20 is not None and low20 is not None and rsi is not None
    assert prior_high20 is not None and prior_low20 is not None

    if atr_pct is not None and atr_pct >= p.max_atr_pct:
        return {
            "status": "no_trade",
            "reason": f"ATR {atr_pct:.2f}% exceeds policy maximum {p.max_atr_pct:.2f}%",
            "setup": None,
            "policy_id": p.policy_id,
        }
    if rsi >= p.max_rsi_new_long:
        return {
            "status": "no_trade",
            "reason": f"RSI {rsi:.2f} exceeds policy maximum {p.max_rsi_new_long:.2f} for a new long",
            "setup": None,
            "policy_id": p.policy_id,
        }
    if volume_ratio is not None and volume_ratio < p.min_volume_ratio:
        return {
            "status": "no_trade",
            "reason": (
                f"latest volume is {volume_ratio:.2f}x the 20-session average; "
                f"policy minimum is {p.min_volume_ratio:.2f}x"
            ),
            "setup": None,
            "policy_id": p.policy_id,
        }

    direction = str(regime.get("direction") or "range_or_transition")
    rationale: list[str] = []
    risks: list[str] = []

    if direction == "trending_up":
        near_prior_high = latest >= prior_high20 * p.breakout_near_high_ratio
        if near_prior_high:
            setup_name = "prior-20-session breakout continuation"
            entry_low = prior_high20
            entry_high = prior_high20 + max(
                p.breakout_buffer_atr * atr,
                prior_high20 * p.breakout_buffer_pct,
            )
            stop = min(
                sma20 - p.breakout_sma_stop_atr * atr,
                entry_low - p.breakout_stop_atr * atr,
            )
            rationale.extend([
                "price, fast average and slow average are positively ordered",
                "price is close to or through the prior 20-session high, which defines a fixed breakout reference",
            ])
            risks.append("a breakout can fail quickly if price closes back below the prior range")
        else:
            setup_name = "uptrend pullback to fast mean"
            entry_low = max(sma20 - p.pullback_band_atr * atr, prior_low20)
            entry_high = sma20 + p.pullback_band_atr * atr
            stop = min(
                prior_low20 - p.pullback_low_stop_atr * atr,
                sma20 - p.pullback_stop_atr * atr,
            )
            rationale.extend([
                "the longer trend is positive but price is not at a fresh breakout level",
                "the fast mean provides a conditional pullback zone rather than a chase entry",
            ])
            risks.append("momentum can continue lower through the moving-average pullback zone")
        entry_condition = "cross_above_zone" if near_prior_high else "within_zone"
    elif direction == "trending_down":
        setup_name = "conditional fast-mean trend reclaim"
        entry_low = sma20 - p.reclaim_band_atr * atr
        entry_high = sma20 + p.reclaim_band_atr * atr
        stop = min(
            entry_low - p.reclaim_stop_atr * atr,
            prior_low20 - p.pullback_low_stop_atr * atr,
        )
        entry_condition = "cross_above_zone"
        rationale.extend([
            "the current trend is down, so Level 1 does not buy current weakness",
            "a reclaim of the fast mean is required before a long candidate exists",
        ])
        risks.append("the broader downtrend can resume even after a temporary reclaim")
    else:
        setup_name = "prior-20-session range breakout"
        entry_low = prior_high20
        entry_high = prior_high20 + max(
            p.breakout_buffer_atr * atr,
            prior_high20 * p.breakout_buffer_pct,
        )
        stop = min(
            sma20 - p.breakout_sma_stop_atr * atr,
            prior_high20 - p.range_stop_atr * atr,
        )
        entry_condition = "cross_above_zone"
        rationale.extend([
            "trend and momentum are not cleanly aligned",
            "Level 1 waits for price to clear the prior 20-session range instead of guessing inside it",
        ])
        risks.append("range breakouts frequently fail without follow-through")

    representative_entry = (entry_low + entry_high) / 2.0
    if stop <= 0 or stop >= entry_low:
        return {
            "status": "no_trade",
            "reason": "derived stop geometry is invalid",
            "setup": None,
            "policy_id": p.policy_id,
        }

    risk = representative_entry - stop
    technical_targets: list[float] = []
    if sma50 > representative_entry:
        technical_targets.append(sma50)
    technical_targets.extend(
        representative_entry + float(multiple) * risk for multiple in p.target_r_multiples
    )
    targets = sorted({round(value, 4) for value in technical_targets if value > representative_entry})
    if not targets:
        return {
            "status": "no_trade",
            "reason": "could not derive a positive target",
            "setup": None,
            "policy_id": p.policy_id,
        }

    if latest > entry_high + p.chase_limit_atr * atr:
        return {
            "status": "no_trade",
            "reason": "price is already too far beyond the derived trigger under the selected policy",
            "setup": None,
            "policy_id": p.policy_id,
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
        "target_basis": "technical level when available plus policy-defined R projections",
        "rationale": rationale,
        "risks": risks,
        "policy_id": p.policy_id,
    }
