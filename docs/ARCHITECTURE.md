# Architecture

## Four-layer boundary

1. **IFMA / research** — company, earnings, valuation, governance, macro.
2. **ITA / trade decision support** — technical state, regime, setup, trade plan, sizing and research evaluation.
3. **Risk/control layer** — account limits, loss limits, policy, permissions, kill switches.
4. **Execution layer** — broker connectivity and order lifecycle.

ITA owns layer 2 only.

## Why not one repo

Trading state changes faster than fundamental research, requires different data, and creates dangerous coupling when broker/execution code lives beside analysis. The split also lets users install ITA without IFMA and vice versa.

## Deterministic core

The Markdown agent/skills decide *which problem to solve*. Python functions perform arithmetic that should be reproducible:

- `technical_snapshot()`
- `classify_regime()`
- `assess_data_freshness()`
- `reward_to_risk()`
- `position_size()`
- `portfolio_risk_summary()`
- `build_trade_plan()`
- `backtest_ma_crossover()`
- `validate_trade_packet()`

## Trade Intent boundary

A future RiskPilot adapter should receive a Trade Packet/Trade Intent and may reject it. ITA must not interpret RiskPilot approval as authority to execute; a separate execution system owns that final action.
