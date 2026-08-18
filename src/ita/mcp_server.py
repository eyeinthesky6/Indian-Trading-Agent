"""Optional MCP wrapper around deterministic Indian Trading Agent tools."""

from .analyze import analyze_symbol
from .backtest import backtest_ma_crossover
from .indicators import technical_snapshot
from .portfolio import portfolio_risk_summary
from .regime import classify_regime
from .risk import position_size
from .tradeplan import build_trade_plan


def create_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install the optional MCP dependency: pip install -e '.[mcp]'") from exc

    mcp = FastMCP("Indian Trading Agent")

    @mcp.tool()
    def analyze_eod_symbol(
        symbol: str,
        exchange: str = "NSE",
        horizon: str = "swing",
        sessions: int = 80,
        capital: float | None = None,
        risk_fraction: float = 0.0075,
        max_position_fraction: float = 0.20,
    ) -> dict:
        """Level 1 standalone EOD analysis; no IFMA or broker login required."""
        return analyze_symbol(
            symbol,
            exchange=exchange,
            horizon=horizon,
            sessions=sessions,
            capital=capital,
            risk_fraction=risk_fraction,
            max_position_fraction=max_position_fraction,
        )

    @mcp.tool()
    def technicals(closes: list[float], highs: list[float] | None = None, lows: list[float] | None = None) -> dict:
        snap = technical_snapshot(closes, highs, lows)
        return {"snapshot": snap, "regime": classify_regime(snap)}

    @mcp.tool()
    def size_position(capital: float, entry: float, stop: float, risk_fraction: float = 0.01, max_position_fraction: float = 0.25) -> dict:
        return position_size(capital, entry, stop, risk_fraction, max_position_fraction)

    @mcp.tool()
    def trade_plan(symbol: str, side: str, current_price: float, entry_low: float, entry_high: float, stop: float, targets: list[float], capital: float | None = None) -> dict:
        return build_trade_plan(symbol=symbol, side=side, current_price=current_price, entry_low=entry_low, entry_high=entry_high, stop=stop, targets=targets, capital=capital)

    @mcp.tool()
    def portfolio_risk(capital: float, positions: list[dict]) -> dict:
        return portfolio_risk_summary(capital, positions)

    @mcp.tool()
    def ma_backtest(closes: list[float], fast_period: int = 20, slow_period: int = 50, initial_capital: float = 100000.0, transaction_cost_bps: float = 10.0, slippage_bps: float = 2.0) -> dict:
        return backtest_ma_crossover(closes, fast_period=fast_period, slow_period=slow_period, initial_capital=initial_capital, transaction_cost_bps=transaction_cost_bps, slippage_bps=slippage_bps)

    return mcp


def main() -> None:  # pragma: no cover - optional dependency
    create_server().run()


if __name__ == "__main__":
    main()
