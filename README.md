# Indian Trading Agent 🇮🇳

**An open-source, India-native trading decision-support agent for NSE/BSE cash equities.**

ITA turns market evidence and explicit risk constraints into a human-reviewable **Trade Packet**: technical state, regime, setup/no-setup, trigger, invalidation, targets, reward:risk and optional position sizing.

> **v0.2 alpha — Level 1 is standalone.** Give it an NSE/BSE cash-equity symbol and it can fetch official daily EOD exchange reports itself. No IFMA install, ProfitPilot install, broker login or API key is required.

## One ticker in, a decision packet out

```bash
pip install -e .
ita analyze RELIANCE --exchange NSE --horizon swing --capital 500000
```

Level 1 runs:

```text
RELIANCE
   ↓
official NSE/BSE daily bhavcopy
   ↓
technical snapshot
   ↓
market regime
   ↓
setup / watch / no-trade
   ↓
trigger + stop/invalidation + targets + R:R
   ↓
optional position sizing
   ↓
TRADE PACKET
```

`execution.allowed` is always `false`. ITA proposes; it does not place orders.

## Why this exists

Research and trading are different jobs.

The sibling **Indian Financial Market Analysis Agent (IFMA)** answers questions such as: what changed in earnings, valuation, governance, ownership, macro or the business?

ITA answers: **is there a trade here, what has to happen before entry, where is the idea invalid, how much capital is at risk, and what would make us stay out?**

IFMA is optional context, not a runtime requirement.

## Level 1 — current

Level 1 is deliberately narrow enough to be real:

| Capability | Level 1 |
|---|---|
| Input | NSE/BSE cash-equity symbol |
| Data | Official public daily EOD bhavcopy |
| Credentials | None |
| Horizons | Swing / positional |
| Technicals | SMA structure, RSI, momentum, ATR, realised volatility, volume and 20-session levels |
| Regime | Trend / range / transition + volatility |
| Automatic setup | Conservative long cash-equity setup, watch or no-trade |
| Risk | Trigger, invalidation, targets, R multiples, optional stop-based sizing |
| Output | Structured Trade Packet |
| Execution | **Never** |

The default automatic setup engine is **long-only at Level 1**. Daily cash-equity data does not justify assuming that an overnight short/product is actually available. Analytical bearishness can still be reported as a downtrend, but the deterministic Level 1 pipeline waits for a long reclaim or returns no trade.

### Data provenance

The bundled provider reads the exchange UDiFF-style daily reports and caches successful raw files under:

```text
~/.cache/indian-trading-agent/bhavcopy/
```

Override with `ITA_MARKET_DATA_CACHE` or `--cache-dir`.

Every result identifies source, exchange, data range, latest trade date, observation count and adjustment basis.

**EOD is not live.** Level 1 refuses intraday horizons.

## Trade Packet statuses

Not trading is a first-class result:

- `no_trade` — no coherent Level 1 setup now;
- `watch` — setup geometry is coherent but the trigger has not happened;
- `actionable_candidate` — EOD trigger/geometry pass, still pending human/control review;
- `invalid` — stale data, broken geometry or another hard failure.

A trading assistant that always finds a trade is just a slot machine with excellent prose.

## Quick examples

```bash
# Standalone Level 1
ita analyze RELIANCE
ita analyze TCS --capital 300000 --risk-percent 0.5 --max-position-percent 15
ita analyze SBIN --horizon positional --sessions 100

# Deterministic lower-level tools remain available
ita snapshot examples/hdfcbank_real_2026-08-10.json
ita plan examples/hdfcbank_real_trade_watch_2026-08-10.json
ita size examples/position_size_input.json
ita validate examples/hdfcbank_real_trade_watch_output_2026-08-10.json
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src
```

## Claude Code plugin

```bash
claude plugin marketplace add eyeinthesky6/Indian-Trading-Agent
claude plugin install india-trader@indian-trading-agent
```

Then try:

```text
/trade HDFCBANK swing
/technicals RELIANCE daily
/regime NIFTY 50
/size capital 500000, entry 1500, stop 1455, risk 0.75%, max position 20%
/backtest a 20/50 trend filter on this price history, include costs
```

For a cash-equity swing/positional `/trade` request, the agent should use the standalone Level 1 path first. IFMA is only additional research context when relevant/requested.

## Optional MCP server

```bash
pip install -e '.[mcp]'
python -m ita.mcp_server
```

MCP exposes `analyze_eod_symbol` as well as technicals, sizing, trade planning, portfolio risk and the simple MA research baseline.

## Deterministic toolkit

Core Python has **no mandatory third-party runtime dependencies**.

- `analyze_symbol()` — full Level 1 ticker pipeline
- `BhavcopyHistoryProvider` — official no-login daily history
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

## Skills included

The agent has 11 specialist skills:

1. India market data and freshness
2. technical analysis
3. market regime
4. India market microstructure
5. setup detection
6. trade planning
7. position sizing and per-trade risk
8. portfolio risk
9. strategy testing
10. trade review
11. IFMA research bridge

Skills are Markdown under [`plugin/skills/`](plugin/skills/); deterministic code lives under [`src/ita/`](src/ita/).

## IFMA integration

ITA does **not** import IFMA. IFMA can optionally provide a small timestamped research packet with fundamentals, earnings, catalysts, governance, valuation or macro context.

A good company can have a poor short-term setup and a weak company can rally. The two systems are deliberately not forced into one bullish/bearish vote.

See [`docs/IFMA_INTEGRATION.md`](docs/IFMA_INTEGRATION.md).

## What comes later

The levels are intentionally separated:

- **Level 1 (current):** no-login official EOD cash-equity analysis.
- **Level 2 (future):** authenticated **read-only** broker/provider data for intraday/fresher evidence; still no execution.
- **Level 3 (future):** optional IFMA, RiskPilot, TensorTrade/Qlib strategy-lab and other ecosystem integrations.

See [`docs/LEVELS.md`](docs/LEVELS.md).

## What ProfitPilot contributes

ProfitPilot already contains years of useful infrastructure lessons: bhavcopy ingestion, canonical OHLCV, instrument mapping, broker historical data, replay/backtest machinery, source-authority ideas and risk/control logic.

ITA does **not** import ProfitPilot. Small useful contracts may be independently extracted when justified; PP risk controls belong in RiskPilot and PP broker execution stays behind a separate execution boundary.

See [`docs/PROFITPILOT_CONTRIBUTION_MAP.md`](docs/PROFITPILOT_CONTRIBUTION_MAP.md).

## Historical validation fixture

The repo still includes the earlier real HDFCBANK 50-session fixture through 10 August 2026. It remains useful as a reproducible frozen regression example, but it is no longer the only way to feed ITA: Level 1 can now fetch EOD history from a ticker itself.

## Project structure

```text
plugin/
  agents/india-trader.md
  commands/
  skills/
src/ita/
  marketdata/
    bhavcopy.py
  analyze.py
  indicators.py
  regime.py
  setups.py
  freshness.py
  risk.py
  portfolio.py
  tradeplan.py
  backtest.py
  contracts.py
  cli.py
  mcp_server.py
schemas/
examples/
tests/
docs/
```

## Product boundary

**In scope:** decision support, official EOD data, technical state, setups, trade planning, sizing, portfolio exposure, strategy research and review.

**Out of scope:** brokerage login, order placement, unattended execution, custody, personalised compliance approval, guaranteed returns, production-grade tick backtesting and derivatives until the cash-equity workflows are mature.

This repo should not become ProfitPilot-with-a-new-name.

## Licence

Apache-2.0. Fork it, extend it, add legitimate provider adapters, build tools on top or use the deterministic functions from another agent.

## Disclaimer

Decision-support and research software only. Not investment, legal, tax or personalised financial advice. No order execution. See [`DISCLAIMER.md`](DISCLAIMER.md).
