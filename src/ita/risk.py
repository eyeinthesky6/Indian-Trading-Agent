from __future__ import annotations

from math import floor


def _positive(name: str, value: float) -> float:
    value = float(value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def reward_to_risk(entry: float, stop: float, target: float, side: str = "long") -> float:
    entry = _positive("entry", entry)
    stop = _positive("stop", stop)
    target = _positive("target", target)
    side = side.lower()
    if side not in {"long", "short"}:
        raise ValueError("side must be 'long' or 'short'")
    risk = (entry - stop) if side == "long" else (stop - entry)
    reward = (target - entry) if side == "long" else (entry - target)
    if risk <= 0:
        raise ValueError("stop must be below entry for long trades and above entry for short trades")
    return reward / risk


def position_size(
    capital: float,
    entry: float,
    stop: float,
    risk_fraction: float = 0.01,
    max_position_fraction: float = 0.25,
    lot_size: int = 1,
) -> dict:
    """Size a position using stop-distance risk and a notional exposure cap."""
    capital = _positive("capital", capital)
    entry = _positive("entry", entry)
    stop = _positive("stop", stop)
    if not 0 < risk_fraction <= 1:
        raise ValueError("risk_fraction must be in (0, 1]")
    if not 0 < max_position_fraction <= 1:
        raise ValueError("max_position_fraction must be in (0, 1]")
    if lot_size <= 0:
        raise ValueError("lot_size must be positive")

    risk_per_unit = abs(entry - stop)
    if risk_per_unit == 0:
        raise ValueError("entry and stop cannot be equal")
    risk_budget = capital * risk_fraction
    exposure_cap = capital * max_position_fraction
    risk_qty = floor((risk_budget / risk_per_unit) / lot_size) * lot_size
    exposure_qty = floor((exposure_cap / entry) / lot_size) * lot_size
    quantity = max(0, min(risk_qty, exposure_qty))
    actual_risk = quantity * risk_per_unit
    position_value = quantity * entry
    limiting_factor = "risk_budget" if risk_qty <= exposure_qty else "exposure_cap"
    warnings: list[str] = []
    if quantity == 0:
        warnings.append("risk or exposure budget is too small for one lot")
    if position_value > capital:
        warnings.append("position notional exceeds capital")

    return {
        "quantity": int(quantity),
        "risk_budget": round(risk_budget, 2),
        "risk_per_unit": round(risk_per_unit, 4),
        "actual_risk": round(actual_risk, 2),
        "actual_risk_pct_capital": round((actual_risk / capital) * 100.0, 3),
        "position_value": round(position_value, 2),
        "position_pct_capital": round((position_value / capital) * 100.0, 2),
        "limiting_factor": limiting_factor,
        "warnings": warnings,
    }
