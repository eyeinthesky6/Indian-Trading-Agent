from __future__ import annotations


def _sma_at(values: list[float], end: int, period: int) -> float:
    start = end - period + 1
    return sum(values[start : end + 1]) / period


def _max_drawdown(equity_curve: list[float]) -> float:
    peak = equity_curve[0]
    worst = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        dd = value / peak - 1.0
        worst = min(worst, dd)
    return worst * 100.0


def backtest_ma_crossover(
    closes: list[float],
    *,
    fast_period: int = 20,
    slow_period: int = 50,
    initial_capital: float = 100000.0,
    transaction_cost_bps: float = 10.0,
    slippage_bps: float = 2.0,
) -> dict:
    """Long/cash MA crossover sanity backtest.

    Signals use data through bar t and are applied to the return from t to t+1,
    preventing same-bar look-ahead. It is intentionally simple and is a research
    baseline, not a production backtester.
    """
    prices = [float(x) for x in closes]
    if any(x <= 0 for x in prices):
        raise ValueError("closes must be positive")
    if fast_period <= 0 or slow_period <= 0 or fast_period >= slow_period:
        raise ValueError("require 0 < fast_period < slow_period")
    if len(prices) <= slow_period + 1:
        raise ValueError("not enough observations for selected periods")
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")

    round_trip_leg_cost = (float(transaction_cost_bps) + float(slippage_bps)) / 10000.0
    equity = float(initial_capital)
    curve = [equity]
    position = 0
    trades = 0
    entry_price: float | None = None
    trade_returns: list[float] = []

    start = slow_period - 1
    benchmark_start = prices[start]
    for t in range(start, len(prices) - 1):
        fast = _sma_at(prices, t, fast_period)
        slow = _sma_at(prices, t, slow_period)
        desired = 1 if fast > slow else 0
        if desired != position:
            equity *= 1.0 - round_trip_leg_cost
            if desired == 1:
                trades += 1
                entry_price = prices[t]
            elif entry_price is not None:
                trade_returns.append(prices[t] / entry_price - 1.0)
                entry_price = None
            position = desired
        market_return = prices[t + 1] / prices[t] - 1.0
        equity *= 1.0 + position * market_return
        curve.append(equity)

    if position == 1:
        equity *= 1.0 - round_trip_leg_cost
        curve[-1] = equity
        if entry_price is not None:
            trade_returns.append(prices[-1] / entry_price - 1.0)

    total_return = equity / initial_capital - 1.0
    benchmark = prices[-1] / benchmark_start - 1.0
    win_rate = None if not trade_returns else sum(r > 0 for r in trade_returns) / len(trade_returns) * 100.0
    return {
        "strategy": "long_cash_ma_crossover",
        "fast_period": fast_period,
        "slow_period": slow_period,
        "observations": len(prices),
        "trades": trades,
        "final_equity": round(equity, 2),
        "total_return_pct": round(total_return * 100.0, 2),
        "buy_hold_return_pct": round(benchmark * 100.0, 2),
        "excess_vs_buy_hold_pct": round((total_return - benchmark) * 100.0, 2),
        "max_drawdown_pct": round(_max_drawdown(curve), 2),
        "closed_trade_win_rate_pct": round(win_rate, 2) if win_rate is not None else None,
        "assumptions": {
            "transaction_cost_bps_per_turnover_leg": float(transaction_cost_bps),
            "slippage_bps_per_turnover_leg": float(slippage_bps),
            "execution_model": "signal at bar t close; exposure applies to t->t+1 return",
        },
    }
