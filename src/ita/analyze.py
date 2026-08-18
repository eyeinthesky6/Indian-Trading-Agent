from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .contracts import validate_trade_packet
from .indicators import technical_snapshot
from .journal import DecisionJournal
from .marketdata import BhavcopyHistoryProvider
from .policy import Level1Policy, load_level1_policy
from .regime import classify_regime
from .setups import derive_long_swing_setup
from .tradeplan import build_trade_plan

IST = ZoneInfo("Asia/Kolkata")


def _eod_freshness(latest_trade_date: str, as_of_date: date, max_age_days: int) -> dict:
    latest = date.fromisoformat(latest_trade_date)
    age_days = (as_of_date - latest).days
    if age_days < 0:
        status = "future_eod"
        actionable = False
    elif age_days <= max_age_days:
        status = "latest_available_eod"
        actionable = True
    else:
        status = "stale_eod"
        actionable = False
    return {
        "status": status,
        "actionable": actionable,
        "calendar_age_days": age_days,
        "max_calendar_age_days": int(max_age_days),
        "latest_trade_date": latest_trade_date,
        "as_of_date": as_of_date.isoformat(),
        "note": "Level 1 uses EOD reports; weekend/holiday semantics are bounded conservatively by calendar age.",
    }


def _no_trade_packet(
    *,
    symbol: str,
    exchange: str,
    horizon: str,
    current_price: float | None,
    market_data: dict,
    reason: str,
    status: str = "no_trade",
) -> dict:
    return {
        "schema_version": "1.0",
        "symbol": symbol.upper(),
        "exchange": exchange,
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
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution": {
            "allowed": False,
            "note": "Decision-support output only; no broker order is generated or submitted.",
        },
    }


def _analysis_id(
    *,
    symbol: str,
    exchange: str,
    horizon: str,
    market_data: dict,
    snapshot: dict,
    regime: dict,
    derivation: dict,
    policy: Level1Policy,
    capital: float | None,
    risk_fraction: float,
    max_position_fraction: float,
) -> str:
    """Stable id for the decision inputs; repeated identical evidence/policy gets the same id."""
    basis = {
        "id_schema": "ita-level1-analysis-v1",
        "symbol": symbol,
        "exchange": exchange,
        "horizon": horizon,
        "history_start": market_data.get("history_start"),
        "history_end": market_data.get("history_end"),
        "source": market_data.get("source"),
        "snapshot": snapshot,
        "regime": regime,
        "derivation": derivation,
        "policy_fingerprint": policy.fingerprint,
        "capital": capital,
        "risk_fraction": risk_fraction,
        "max_position_fraction": max_position_fraction,
    }
    canonical = json.dumps(basis, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "ita1_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


def _policy_source_label(source: Level1Policy | dict[str, Any] | str | Path | None) -> str:
    if source is None:
        return "embedded_default"
    if isinstance(source, Level1Policy):
        return "Level1Policy_object"
    if isinstance(source, dict):
        return "inline_object"
    return str(Path(source).expanduser())


def analyze_symbol(
    symbol: str,
    *,
    exchange: str = "NSE",
    horizon: str = "swing",
    sessions: int | None = None,
    as_of: str | date | None = None,
    capital: float | None = None,
    risk_fraction: float | None = None,
    max_position_fraction: float | None = None,
    cache_dir: str | None = None,
    provider: BhavcopyHistoryProvider | None = None,
    policy: Level1Policy | dict[str, Any] | str | Path | None = None,
    record: bool = False,
    journal_path: str | Path | None = None,
) -> dict:
    """Run the complete Level 1 ticker-to-Trade-Packet path.

    Level 1 is daily EOD cash-equity decision support. It needs no IFMA, PP,
    broker login or runtime service. It deliberately rejects intraday horizons.
    The strategy/risk rules come from an explicit, fingerprinted Level1Policy.
    """
    p = load_level1_policy(policy)
    symbol = str(symbol).strip().upper()
    exchange = str(exchange).strip().upper()
    horizon = str(horizon).strip().lower()
    sessions = p.default_sessions if sessions is None else int(sessions)
    risk_fraction = p.default_risk_fraction if risk_fraction is None else float(risk_fraction)
    max_position_fraction = (
        p.default_max_position_fraction
        if max_position_fraction is None
        else float(max_position_fraction)
    )

    if not symbol:
        raise ValueError("symbol is required")
    if exchange not in {"NSE", "BSE"}:
        raise ValueError("exchange must be NSE or BSE")
    if horizon not in {"swing", "positional"}:
        raise ValueError("Level 1 supports only swing or positional EOD analysis")
    if sessions < p.min_sessions:
        raise ValueError(
            f"sessions must be at least {p.min_sessions} under policy {p.policy_id}"
        )

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
    snapshot = technical_snapshot(
        closes,
        highs,
        lows,
        volumes,
        fast_period=p.fast_period,
        slow_period=p.slow_period,
        rsi_period=p.rsi_period,
        atr_period=p.atr_period,
    )
    regime = classify_regime(snapshot)
    derivation = derive_long_swing_setup(snapshot, regime, p)
    eod_freshness = _eod_freshness(
        history.latest_trade_date, as_of_date, p.max_eod_age_days
    )
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
            exchange=exchange,
            horizon=horizon,
            current_price=current_price,
            market_data=market_data,
            reason=f"Level 1 EOD freshness check failed: {eod_freshness['status']}",
            status="invalid",
        )
    elif derivation.get("status") != "setup":
        packet = _no_trade_packet(
            symbol=symbol,
            exchange=exchange,
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
            min_reward_to_risk=p.min_reward_to_risk,
            data_timestamp=latest_timestamp,
            data_source=history.source_name,
            setup=str(derivation["setup"]),
            rationale=list(derivation.get("rationale") or []),
            risks=list(derivation.get("risks") or []),
        )
        packet["market_data"] = market_data
        packet["exchange"] = exchange

    policy_meta = p.metadata()
    policy_meta["source"] = _policy_source_label(policy)
    analysis_id = _analysis_id(
        symbol=symbol,
        exchange=exchange,
        horizon=horizon,
        market_data=market_data,
        snapshot=snapshot,
        regime=regime,
        derivation=derivation,
        policy=p,
        capital=capital,
        risk_fraction=risk_fraction,
        max_position_fraction=max_position_fraction,
    )
    packet["analysis_id"] = analysis_id
    packet["policy"] = policy_meta

    validation = validate_trade_packet(packet)
    if not validation["valid"]:
        raise RuntimeError(f"generated Trade Packet failed validation: {validation['errors']}")

    result: dict[str, Any] = {
        "level": 1,
        "analysis_id": analysis_id,
        "symbol": symbol,
        "exchange": exchange,
        "horizon": horizon,
        "policy": policy_meta,
        "market_data": market_data,
        "technical_snapshot": snapshot,
        "regime": regime,
        "setup_derivation": derivation,
        "trade_packet": packet,
    }
    if record:
        result["journal"] = DecisionJournal(journal_path).append(result)
    return result
