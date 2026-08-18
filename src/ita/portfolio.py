from __future__ import annotations

from collections import defaultdict


def portfolio_risk_summary(capital: float, positions: list[dict]) -> dict:
    """Summarise notional exposure and concentration without pretending to model VaR."""
    capital = float(capital)
    if capital <= 0:
        raise ValueError("capital must be positive")
    gross = 0.0
    net = 0.0
    sectors: dict[str, float] = defaultdict(float)
    symbols: list[tuple[str, float]] = []
    for p in positions:
        symbol = str(p["symbol"])
        value = abs(float(p["market_value"]))
        side = str(p.get("side", "long")).lower()
        sector = str(p.get("sector", "Unclassified"))
        if side not in {"long", "short"}:
            raise ValueError(f"invalid side for {symbol}")
        gross += value
        net += value if side == "long" else -value
        sectors[sector] += value
        symbols.append((symbol, value))

    largest_symbol, largest_value = max(symbols, key=lambda x: x[1], default=(None, 0.0))
    sector_pct = {k: round(v / capital * 100.0, 2) for k, v in sorted(sectors.items())}
    largest_sector = max(sectors.items(), key=lambda x: x[1], default=(None, 0.0))
    warnings: list[str] = []
    if gross / capital > 1.0:
        warnings.append("gross exposure exceeds capital")
    if largest_value / capital > 0.25:
        warnings.append(f"largest position {largest_symbol} exceeds 25% of capital")
    if largest_sector[1] / capital > 0.40:
        warnings.append(f"sector concentration in {largest_sector[0]} exceeds 40% of capital")

    return {
        "gross_exposure": round(gross, 2),
        "gross_exposure_pct": round(gross / capital * 100.0, 2),
        "net_exposure": round(net, 2),
        "net_exposure_pct": round(net / capital * 100.0, 2),
        "largest_position": largest_symbol,
        "largest_position_pct": round(largest_value / capital * 100.0, 2),
        "sector_exposure_pct": sector_pct,
        "warnings": warnings,
    }
