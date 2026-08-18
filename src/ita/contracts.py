from __future__ import annotations

TRADE_STATUSES = {"no_trade", "watch", "actionable_candidate", "invalid"}


def validate_trade_packet(packet: dict) -> dict:
    errors: list[str] = []
    required = [
        "schema_version", "symbol", "status", "horizon", "reasons_not_to_trade",
        "market_data", "execution",
    ]
    for key in required:
        if key not in packet:
            errors.append(f"missing required field: {key}")
    status = packet.get("status")
    if status is not None and status not in TRADE_STATUSES:
        errors.append(f"unsupported status: {status}")
    execution = packet.get("execution")
    if isinstance(execution, dict) and execution.get("allowed") is not False:
        errors.append("execution.allowed must be false in this repository")
    market_data = packet.get("market_data")
    if status == "actionable_candidate":
        if not isinstance(market_data, dict) or not market_data.get("timestamp") or not market_data.get("source"):
            errors.append("actionable candidates require market-data timestamp and source")
        freshness = market_data.get("freshness") if isinstance(market_data, dict) else None
        if freshness is not None and freshness.get("actionable") is not True:
            errors.append("actionable candidate has failed freshness gate")
    if status == "no_trade" and not packet.get("reasons_not_to_trade"):
        errors.append("no_trade packets must explain why")
    return {"valid": not errors, "errors": errors}


def validate_ifma_research_packet(packet: dict) -> dict:
    errors: list[str] = []
    for key in ("symbol", "as_of", "summary", "risks"):
        if key not in packet:
            errors.append(f"missing IFMA field: {key}")
    return {"valid": not errors, "errors": errors}
