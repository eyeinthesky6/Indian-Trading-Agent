# ITA capability levels

The levels are product boundaries, not maturity theatre. A later level may add context or data, but Level 1 must remain independently useful.

## Level 1 — standalone EOD cash-equity analysis (current)

**Goal:** Give the agent only an NSE/BSE cash-equity symbol and receive a reproducible EOD trading decision packet.

```text
SYMBOL
  ↓
official NSE/BSE daily bhavcopy
  ↓
technical snapshot
  ↓
market regime
  ↓
long cash-equity setup / watch / no-trade
  ↓
entry + invalidation + targets + R:R
  ↓
optional position sizing
  ↓
TRADE PACKET
```

Level 1:
- needs no IFMA installation;
- needs no ProfitPilot installation;
- needs no broker account or API key;
- uses public official daily exchange reports;
- supports `swing` and `positional` horizons only;
- is EOD decision support, not a live quote feed;
- derives long-only cash-equity candidates rather than assuming overnight short-selling/product eligibility;
- never places an order (`execution.allowed=false`).

CLI example:

```bash
ita analyze RELIANCE --exchange NSE --horizon swing --capital 500000
```

Raw successful bhavcopy downloads are cached locally so repeated analyses do not redownload the same day.

### Level 1 limitations

- Official bhavcopy is unadjusted EOD data. Splits, bonuses, rights and exceptional corporate actions must be investigated when they distort the lookback.
- It cannot answer intraday questions from daily bars.
- It cannot know the next session's opening gap or fill quality.
- Setup thresholds are conservative defaults, not universal alpha claims.
- A Trade Packet is a reviewable candidate, not investment advice or execution authority.

## Level 2 — authenticated read-only market data (future)

**Goal:** Add fresher/intraday evidence while preserving the Level 1 decision contract.

Possible adapters:
- Zerodha Kite historical candles/current quotes;
- Upstox market-data/history APIs;
- ICICI Direct/Breeze history;
- Flattrade or other legitimate user-authorised providers.

Likely additions:
- canonical instrument master / symbol resolution;
- 1m/5m/15m/1h bars where provider terms permit;
- market-session aware freshness;
- read-only quotes and depth/microstructure packets;
- stronger source-authority metadata and provider fallback rules.

**Still out of scope:** order placement. Level 2 is data access, not execution.

## Level 3 — optional intelligence and control ecosystem (future)

Level 3 connects independent systems through explicit packets rather than turning ITA into another monolith.

Possible integrations:
- **IFMA** — earnings, fundamentals, governance, valuation and macro context;
- **RiskPilot** — independent account/policy/risk approval of Trade Intents;
- **TensorTrade** — optional reinforcement-learning experiments in the strategy lab;
- **Qlib** — optional ML/research experiments;
- breadth/relative-strength and portfolio context services;
- a separate broker execution project after control approval.

None of those systems should become a mandatory dependency for Level 1.

## Non-goal

There is deliberately no "Level 4 autonomous trader" in this repository. If unattended execution is ever built, it belongs behind an independent control layer and a separate execution boundary.
