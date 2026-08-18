from __future__ import annotations

from datetime import datetime, timezone

from .freshness import assess_data_freshness
from .risk import position_size, reward_to_risk


def _trigger_state(current: float, low: float, high: float, condition: str) -> tuple[str, str]:
    if condition == "within_zone":
        triggered = low <= current <= high
        note = "price is inside entry zone" if triggered else "wait for price to enter the entry zone"
    elif condition == "cross_above_zone":
        triggered = current >= high
        note = "price is at/above breakout trigger" if triggered else "wait for a confirmed move above the entry zone"
    elif condition == "cross_below_zone":
        triggered = current <= low
        note = "price is at/below breakdown trigger" if triggered else "wait for a confirmed move below the entry zone"
    else:
        raise ValueError("entry_condition must be within_zone, cross_above_zone or cross_below_zone")
    return ("triggered" if triggered else "waiting", note)


def build_trade_plan(
    *,
    symbol: str,
    side: str,
    current_price: float,
    entry_low: float,
    entry_high: float,
    stop: float,
    targets: list[float],
    horizon: str = "swing",
    entry_condition: str = "within_zone",
    capital: float | None = None,
    risk_fraction: float = 0.01,
    max_position_fraction: float = 0.25,
    min_reward_to_risk: float = 1.5,
    data_timestamp: str | None = None,
    data_source: str | None = None,
    freshness_as_of: str | None = None,
    max_data_age_minutes: float | None = None,
    setup: str | None = None,
    rationale: list[str] | None = None,
    risks: list[str] | None = None,
) -> dict:
    """Build a structured, non-executing trade plan with geometry and trigger checks."""
    side = side.lower()
    if side not in {"long", "short"}:
        raise ValueError("side must be 'long' or 'short'")
    if entry_low <= 0 or entry_high <= 0 or current_price <= 0 or stop <= 0:
        raise ValueError("prices must be positive")
    if entry_low > entry_high:
        raise ValueError("entry_low cannot exceed entry_high")
    if not targets:
        raise ValueError("at least one target is required")
    if min_reward_to_risk < 0:
        raise ValueError("min_reward_to_risk must be non-negative")

    entry = (float(entry_low) + float(entry_high)) / 2.0
    invalid_reasons: list[str] = []
    if side == "long" and stop >= entry_low:
        invalid_reasons.append("long stop must sit below the entry zone")
    if side == "short" and stop <= entry_high:
        invalid_reasons.append("short stop must sit above the entry zone")

    rr: list[float] = []
    for target in targets:
        try:
            ratio = reward_to_risk(entry, stop, float(target), side)
            if ratio <= 0:
                invalid_reasons.append(f"target {target} is on the wrong side of the entry")
            rr.append(ratio)
        except ValueError as exc:
            invalid_reasons.append(str(exc))
            rr.append(float("nan"))

    valid_rr = [x for x in rr if x == x and x > 0]
    if valid_rr and max(valid_rr) < min_reward_to_risk:
        invalid_reasons.append(
            f"best target offers less than {min_reward_to_risk:.2f}R from the midpoint entry"
        )

    trigger_state, trigger_note = _trigger_state(
        float(current_price), float(entry_low), float(entry_high), entry_condition
    )

    freshness = None
    if max_data_age_minutes is not None:
        if not data_timestamp:
            invalid_reasons.append("data timestamp is required when freshness gating is enabled")
        else:
            freshness = assess_data_freshness(
                data_timestamp, as_of_timestamp=freshness_as_of, max_age_minutes=max_data_age_minutes
            )
            if not freshness["actionable"]:
                invalid_reasons.append(f"market data freshness check failed: {freshness['status']}")

    sizing = None
    if capital is not None:
        sizing = position_size(
            capital=float(capital),
            entry=entry,
            stop=float(stop),
            risk_fraction=risk_fraction,
            max_position_fraction=max_position_fraction,
        )

    if invalid_reasons:
        status = "invalid"
    elif trigger_state == "waiting":
        status = "watch"
    else:
        status = "actionable_candidate"

    return {
        "schema_version": "1.0",
        "symbol": symbol.upper(),
        "side": side,
        "status": status,
        "horizon": horizon,
        "setup": setup,
        "current_price": round(float(current_price), 4),
        "entry_zone": [round(float(entry_low), 4), round(float(entry_high), 4)],
        "entry_condition": entry_condition,
        "trigger_state": trigger_state,
        "trigger_note": trigger_note,
        "representative_entry": round(entry, 4),
        "invalidation_stop": round(float(stop), 4),
        "targets": [round(float(t), 4) for t in targets],
        "reward_to_risk": [round(x, 2) if x == x else None for x in rr],
        "position_sizing": sizing,
        "decision_thresholds": {"min_reward_to_risk": float(min_reward_to_risk)},
        "rationale": rationale or [],
        "risks": risks or [],
        "reasons_not_to_trade": invalid_reasons,
        "market_data": {"timestamp": data_timestamp, "source": data_source, "freshness": freshness},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution": {
            "allowed": False,
            "note": "Decision-support output only; no broker order is generated or submitted.",
        },
    }
