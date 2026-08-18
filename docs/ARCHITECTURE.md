# Architecture

## Four-layer boundary

1. **IFMA / research** — company, earnings, valuation, governance, macro. Optional to ITA.
2. **ITA / trade decision support** — market evidence, technical state, regime, setup, trade plan, sizing and research evaluation.
3. **Risk/control layer** — account limits, loss limits, policy, permissions, kill switches.
4. **Execution layer** — broker connectivity and order lifecycle.

ITA owns layer 2 only.

## Level 1 standalone path

Level 1 deliberately works without layers 1, 3 or 4:

```text
NSE/BSE SYMBOL
      ↓
BhavcopyHistoryProvider
(official public daily reports)
      ↓
canonical DailyBar history
      ↓
technical_snapshot()
      ↓
classify_regime()
      ↓
derive_long_swing_setup()
      ↓
build_trade_plan()
      ↓
validate_trade_packet()
      ↓
TRADE PACKET
execution.allowed = false
```

The market-data provider is stdlib-only and caches successful raw reports locally. It provides EOD evidence, not live quotes.

## Why not one repo

Trading state changes faster than fundamental research, requires different data, and creates dangerous coupling when broker/execution code lives beside analysis. The split also lets users install ITA without IFMA and vice versa.

ProfitPilot is treated as a donor/reference codebase rather than an import. See [`PROFITPILOT_CONTRIBUTION_MAP.md`](PROFITPILOT_CONTRIBUTION_MAP.md).

## Deterministic core

The Markdown agent/skills decide *which problem to solve*. Python functions perform arithmetic and state transitions that should be reproducible:

- `analyze_symbol()`
- `technical_snapshot()`
- `classify_regime()`
- `derive_long_swing_setup()`
- `assess_data_freshness()`
- `reward_to_risk()`
- `position_size()`
- `portfolio_risk_summary()`
- `build_trade_plan()`
- `backtest_ma_crossover()`
- `validate_trade_packet()`

## Future adapter boundary

Level 2 may add read-only broker/provider adapters behind the same market-data contract. Their job is to supply canonical, timestamped evidence; they do not gain execution authority.

Level 3 can consume optional IFMA research and send a Trade Intent to RiskPilot. RiskPilot may reject it. ITA must not interpret RiskPilot approval as authority to execute; a separate execution system owns the final action.
