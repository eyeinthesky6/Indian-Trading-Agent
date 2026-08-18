from __future__ import annotations

from datetime import datetime, timezone


def _parse(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamps must include a timezone offset")
    return dt.astimezone(timezone.utc)


def assess_data_freshness(data_timestamp: str, *, as_of_timestamp: str | None = None, max_age_minutes: float = 30.0) -> dict:
    """Check timestamp age. Market-calendar/session semantics remain an agent-level concern."""
    if max_age_minutes < 0:
        raise ValueError("max_age_minutes must be non-negative")
    data_time = _parse(data_timestamp)
    as_of = _parse(as_of_timestamp) if as_of_timestamp else datetime.now(timezone.utc)
    age_minutes = (as_of - data_time).total_seconds() / 60.0
    if age_minutes < -1:
        status = "future_timestamp"
        actionable = False
    elif age_minutes <= max_age_minutes:
        status = "fresh"
        actionable = True
    else:
        status = "stale"
        actionable = False
    return {
        "status": status,
        "actionable": actionable,
        "age_minutes": round(age_minutes, 2),
        "max_age_minutes": float(max_age_minutes),
        "data_timestamp": data_timestamp,
        "as_of_timestamp": as_of.isoformat(),
        "note": "This is a clock-age check; verify exchange session/calendar context separately.",
    }
