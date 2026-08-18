# Indian Trading Agent 🇮🇳

**An open-source, India-native trading decision-support agent for NSE/BSE markets.**

Indian Trading Agent (ITA) turns fresh market data, technical state, optional IFMA research and explicit risk constraints into a human-reviewable **Trade Packet**. It is designed for traders and trading agents that need disciplined setups, sizing, risk/reward and strategy checks — without hiding assumptions or quietly placing orders.

> **Status:** v0.1 alpha. The Claude Code agent/skill pack and deterministic Python tools are usable now. Broker execution is intentionally out of scope.

## Why this exists

Research and trading are different jobs.

The sibling **Indian Financial Market Analysis Agent (IFMA)** answers questions such as: what changed in earnings, valuation, governance, ownership, macro or the business? ITA answers: **is there a trade here, what has to happen before entry, where is the idea invalid, how much capital is at risk, and what would make us stay out?**

The projects are deliberately separate so that:

- IFMA stays an evidence-first analyst instead of becoming a trading bot;
- ITA can be useful to technical/systematic traders without requiring full fundamental research;
- RiskPilot or another control layer can independently approve/reject a trade intent;
- broker/execution integrations remain isolated from analysis and decision support.

## What v0.1 can do

| Workflow | What ITA does |
|---|---|
| **Technical state** | SMA structure, RSI, momentum, ATR, realised volatility, volume context and recent levels |
| **Market regime** | Trend / range / transition plus volatility state with explicit rationale |
| **Setup detection** | Breakout, pullback, trend reclaim, mean-reversion and event-gap frameworks with invalidation |
| **Trade planning** | Conditional trigger, entry zone, stop/invalidation, targets, R multiples and reasons not to trade |
| **Position sizing** | Stop-distance risk budget plus maximum notional exposure cap |
| **Portfolio risk** | Gross/net exposure, largest position and sector concentration warnings |
| **Strategy sanity tests** | A deliberately simple no-look-ahead MA baseline with transaction cost and slippage assumptions |
| **Freshness gating** | Prevent stale timestamped market data from being treated as actionable |
| **Trade review** | Separate process quality from outcome; preserve thesis, trigger and invalidation for review |
| **IFMA bridge** | Consume a loose JSON research packet without taking a runtime dependency on IFMA |

## The design

```text
Fresh market data                         Optional IFMA research packet
(NSE/BSE/licensed/user-supplied)          (fundamentals/earnings/macro/etc.)
           │                                           │
           └──────────────────┬────────────────────────┘
                              ↓
                       India Trader Agent
                              ↓
         market data → technicals → regime → setup
                              ↓
               trigger + invalidation + targets
                              ↓
          deterministic sizing / exposure / R:R tools
                              ↓
                       TRADE PACKET
                  ┌───────────┴───────────┐
                  ↓                       ↓
              Human review          RiskPilot / policy layer
                                          ↓
                                Separate execution engine
```

**ITA never sends the final arrow itself.** `execution.allowed` is hard-coded `false` in its deterministic Trade Packet.

## Trade Packet statuses

ITA treats *not trading* as a first-class outcome:

- `no_trade` — evidence does not justify a setup;
- `watch` — setup geometry is coherent but the trigger has not happened;
- `actionable_candidate` — trigger and deterministic gates pass; still requires human/control-layer review;
- `invalid` — geometry, freshness or another hard requirement fails.

A useful trading assistant should often say **wait**. An agent that always finds a trade is just a very articulate slot machine.

## Real validation: HDFCBANK

The repository includes a real 50-session HDFCBANK NSE dataset from **1 June–10 August 2026** sourced from StockAnalysis.com, which identifies S&P Global Market Intelligence as its historical-data source.

Running:

```bash
PYTHONPATH=src python -m ita.cli snapshot examples/hdfcbank_real_2026-08-10.json
```

produced:

- close ₹731.00
- 20-session SMA ₹759.33
- 50-session SMA ₹773.44
- RSI 35.22
- 20-session momentum **-10.63%**
- ATR 1.73% of price
- regime: **trending_down**

The example trade is therefore **not a current long**. It is a conditional trend-reclaim watch: only a confirmed move through ₹758–762 activates the candidate. At the historical test timestamp, the tool returns `watch`, not `actionable_candidate`.

The same Aug 10 packet is also run through the freshness gate as of Aug 18. It becomes `invalid` because the market data is stale. See [`docs/VALIDATION.md`](docs/VALIDATION.md).

## Quick start — Claude Code plugin

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

The agent must fetch or receive current market data before presenting a setup as current.

## Quick start — deterministic Python tools

Core calculations have **no mandatory runtime dependencies beyond Python 3.10+**.

```bash
pip install -e .

ita snapshot examples/hdfcbank_real_2026-08-10.json
ita plan examples/hdfcbank_real_trade_watch_2026-08-10.json
ita size examples/position_size_input.json
ita validate examples/hdfcbank_real_trade_watch_output_2026-08-10.json
```

Run the test suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

### Optional MCP server

```bash
pip install -e '.[mcp]'
python -m ita.mcp_server
```

The MCP wrapper exposes technical snapshot/regime, position sizing, trade planning, portfolio exposure and the simple MA research baseline.

## Skills included

The first release contains **11 trading skills**:

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

Skills are Markdown under [`plugin/skills/`](plugin/skills/); the deterministic toolkit lives under [`src/ita/`](src/ita/).

## IFMA integration

ITA does **not** import IFMA. The boundary is a small research packet containing symbol, as-of timestamp, summary, catalysts, risks and optional valuation/fundamental views. That keeps both repos independently installable and prevents research code from quietly leaking into execution logic.

See [`docs/IFMA_INTEGRATION.md`](docs/IFMA_INTEGRATION.md) and [`schemas/ifma_research_packet.schema.json`](schemas/ifma_research_packet.schema.json).

## Data discipline

- Never call stale delayed data “live”.
- Every current Trade Packet needs provider/source and timestamp.
- Corporate actions must be understood before using long historical price series.
- Do not mix adjusted and unadjusted histories silently.
- Do not infer a full technical state from a single current quote.
- Current NSE/BSE rules, sessions, costs, product eligibility and broker behaviour must be checked from current authoritative sources when they matter.

ITA intentionally ships **no brittle exchange scraper** and **no fake live feed**.

## Project structure

```text
.claude-plugin/marketplace.json
plugin/
  .claude-plugin/plugin.json
  agents/india-trader.md
  commands/
  skills/
src/ita/
  indicators.py
  regime.py
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

**In scope:** decision support, technical state, setups, trade planning, sizing, portfolio exposure, strategy research and review.

**Out of scope in this repo:** brokerage login, order placement, unattended execution, custody, personalised compliance approval, guaranteed returns, production-grade tick backtesting, options pricing/Greeks and broker-specific margin engines.

Those can be separate adapters/projects when warranted. The repo should not become ProfitPilot-with-a-new-name.

## Open-source posture

Apache-2.0. Fork it, extend it, connect your own licensed data, add sector/setup packs, or use the deterministic tools from another agent.

## Roadmap

Highest-value next steps are adapters and better evidence, not fifty new indicators:

- current licensed/user-provided market-data adapters;
- Nifty/sector breadth and relative-strength packets;
- richer walk-forward evaluation and trade-ledger analytics;
- transaction-cost schedules supplied as versioned data, not magic constants;
- RiskPilot Trade Intent adapter;
- optional TensorTrade/Qlib strategy-lab adapters;
- derivatives pack only after cash-equity workflows are clean.

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Disclaimer

Decision-support and research software only. Not investment, legal, tax or personalised financial advice. No order execution. See [`DISCLAIMER.md`](DISCLAIMER.md).
