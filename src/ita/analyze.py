from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from .contracts import validate_trade_packet
from .indicators import technical_snapshot
from .marketdata import BhavcopyHistoryProvider
from .regime import classify_regime
from .setups import derive_long_swing_setup
from .tradeplan import build_trade_plan

IST = ZoneInfo("Asia/Kolkata")


def _eod_freshness(latest_trade_date: str, as_of_date: date) -> dict:
    latest = date.fromisoformat(latest_trade_date)
    age_days = (as_of_date - latest).days
    if age_days < 0:
        status = "future_eod"
        actionable = False
    elif age_days <= 5:
        status = "latest_available_eod"
        actionable = True
    else:
        status = "stale_eod"
        actionable = False
    return {
        "status": status,
        "actionable": actionable,
        "calendar_age_days": age_days,
        "latest_trade_date": latest_trade_date,
        "as_of_date": as_of_date.isoformat(),
        "note": "Level 1 uses EOD reports; weekend/holiday semantics are bounded conservatively by calendar age.",
    }


def _no_trade_packet(*, symbol: str, horizon: str, current_price: float | None, market_data: dict, reason: str, status: str = "no_trade") -> dict:
    return {
        "schema_version": "1.0",
        "symbol": symbol.upper(),
        "side": "long",
        "status": status,
        "horizon": horizon,
        "setup": None,
        "current_price": current_price,
        "entry_zone": None,
        "entry_condition": None,
        "trigger_state": None,
        "trigger_note": None,
        "representative_entry": None,
        "invalidation_stop": None,
        "targets": [],
        "reward_to_risk": [],
        "position_sizing": None,
        "rationale": [],
        "risks": [],
        "reasons_not_to_trade": [reason],
        "market_data": market_data,
        "generated_at_utc": datetime.now().astimezone().isoformat(),
        "execution": {
            "allowed": False,
            "note": "Decision-support output only; no broker order is generated or submitted.",
        },
    }


def analyze_symbol(
    symbol: str,
    *,
    exchange: str = "NSE",
    horizon: str = "swing",
    sessions: int = 80,
    as_of: str | date | None = None,
    capital: float | None = None,
    risk_fraction: float = 0.0075,
    max_position_fraction: float = 0.20,
    cache_dir: str | None = None,
    provider: BhavcopyHistoryProvider | None = None,
) -> dict:
    """Run the complete Level 1 ticker-to-Trade-Packet path.

    Level 1 is daily EOD cash-equity decision support. It needs no IFMA, PP,
    broker login or runtime service. It deliberately rejects intraday horizons.
    """
    symbol = str(symbol).strip().upper()
    exchange = str(exchange).strip().upper()
    horizon = str(horizon).strip().lower()
    if not symbol:
        raise ValueError("symbol is required")
    if exchange not in {"NSE", "BSE"}:
        raise ValueError("exchange must be NSE or BSE")
    if horizon not in {"swing", "positional"}:
        raise ValueError("Level 1 supports only swing or positional EOD analysis")
    if sessions < 55:
        raise ValueError("sessions must be at least 55 so 50-session state is meaningful")

    if isinstance(as_of, date):
        as_of_date = as_of
    elif isinstance(as_of, str) and as_of.strip():
        as_of_date = date.fromisoformat(as_of.strip()[:10])
    else:
        as_of_date = datetime.now(IST).date()

    history_provider = provider or BhavcopyHistoryProvider(cache_dir=cache_dir)
    history = history_provider.fetch_symbol_history(
        symbol,
        exchange=exchange,
        sessions=sessions,
        as_of=as_of_date,
        max_calendar_days=max(180, sessions * 2 + 30),
    )
    bars = history.bars
    closes = [bar.close for bar in bars]
    highs = [bar.high for bar in bars]
    lows = [bar.low for bar in bars]
    volumes = [bar.volume for bar in bars]
    snapshot = technical_snapshot(closes, highs, lows, volumes)
    regime = classify_regime(snapshot)
    derivation = derive_long_swing_setup(snapshot, regime)
    eod_freshness = _eod_freshness(history.latest_trade_date, as_of_date)
    latest_timestamp = bars[-1].timestamp
    market_data = {
        "timestamp": latest_timestamp,
        "source": history.source_name,
        "source_kind": history.source_kind,
        "authoritative": history.authoritative,
        "exchange": exchange,
        "mode": "daily_eod",
        "observations": len(bars),
        "history_start": bars[0].trade_date,
        "history_end": bars[-1].trade_date,
        "requested_as_of": as_of_date.isoformat(),
        "adjustment_basis": "unadjusted official bhavcopy; verify corporate actions when material",
        "freshness": eod_freshness,
    }

    current_price = snapshot.get("latest_close")
    if not eod_freshness["actionable"]:
        packet = _no_trade_packet(
            symbol=symbol,
            horizon=horizon,
            current_price=current_price,
            market_data=market_data,
            reason=f"Level 1 EOD freshness check failed: {eod_freshness['status']}",
            status="invalid",
        )
    elif derivation.get("status") != "setup":
        packet = _no_trade_packet(
            symbol=symbol,
            horizon=horizon,
            current_price=current_price,
            market_data=market_data,
            reason=str(derivation.get("reason") or "no coherent Level 1 setup"),
        )
    else:
        packet = build_trade_plan(
            symbol=symbol,
            side="long",
            current_price=float(current_price),
            entry_low=float(derivation["entry_low"]),
            entry_high=float(derivation["entry_high"]),
            stop=float(derivation["stop"]),
            targets=[float(value) for value in derivation["targets"]],
            horizon=horizon,
            entry_condition=str(derivation["entry_condition"]),
            capital=capital,
            risk_fraction=risk_fraction,
            max_position_fraction=max_position_fraction,
            data_timestamp=latest_timestamp,
            data_source=history.source_name,
            setup=str(derivation["setup"]),
            rationale=list(derivation.get("rationale") or []),
            risks=list(derivation.get("risks") or []),
        )
        packet["market_data"] = market_data

    validation = validate_trade_packet(packet)
    if not validation["valid"]:
        raise RuntimeError(f"generated Trade Packet failed validation: {validation['errors']}")

    return {
        "level": 1,
        "symbol": symbol,
        "exchange": exchange,
        "horizon": horizon,
        "market_data": market_data,
        "technical_snapshot": snapshot,
        "regime": regime,
        "setup_derivation": derivation,
        "trade_packet": packet,
    }
