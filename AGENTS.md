# AGENTS.md — Indian Trading Agent

## Mission

Build a disciplined, India-native trading decision-support agent. Prefer fresh data, explicit triggers, invalidation, reproducible risk calculations and `NO TRADE` over confident-looking guesses.

## Product boundary

- Technical analysis, regime, setup detection and trade planning: yes.
- Position sizing, portfolio exposure and strategy research: yes.
- Optional IFMA research packet consumption: yes.
- Broker login, order placement, unattended execution or custody: no.
- Guaranteed returns or fabricated current market data: no.

## Core rule

A Trade Packet is a **proposal for review**, never an order. `execution.allowed` must remain `false` in this repository.

## Data rules

- Current prices/bars require source/provider and timestamp.
- Never call delayed/stale data live.
- Do not recompute indicators from a lone current quote when the underlying bar history is stale.
- State adjusted vs unadjusted basis when corporate actions could matter.
- Verify current exchange/broker/regulatory facts from authoritative current sources rather than memory.

## Decision rules

- `no_trade` is a successful result.
- A setup requires a trigger and invalidation condition.
- Entry/stop/target geometry must be coherent before sizing.
- Risk budget and notional cap are separate constraints.
- Do not optimise strategy parameters on the same window used to claim performance.
- Backtests must include stated costs/slippage and avoid look-ahead.

## Coding rules

- Python 3.10+.
- Keep core deterministic tools dependency-light; stdlib-only by default.
- Tests for financial/trading arithmetic and output contracts.
- No credentials, broker tokens or API secrets in the repository.
- Do not add a broker SDK to core.

## Interop

IFMA is a sibling research source, not a runtime dependency. Exchange research via versioned JSON contracts under `schemas/`.
