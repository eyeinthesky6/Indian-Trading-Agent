# AGENTS.md — Indian Trading Agent

## Mission

Build a disciplined, India-native trading decision-support agent. Prefer fresh data, explicit strategy rules, reproducible calculations, falsifiable triggers/invalidation and `NO TRADE` over confident-looking guesses.

## Product boundary

- Technical analysis, regime, setup detection and trade planning: yes.
- Position sizing, portfolio exposure and strategy research: yes.
- Explicit Level 1 strategy/risk policy and decision journaling: yes.
- Optional IFMA research packet consumption: yes.
- Broker login, order placement, unattended execution or custody: no.
- Guaranteed returns or fabricated current market data: no.

## Core rule

A Trade Packet is a **proposal for review**, never an order. `execution.allowed` must remain `false` in this repository.

## Level 1 strategy ownership

Level 1 must not freelance trading thresholds.

- `Level1Policy` is the deterministic strategy/risk contract.
- The reviewed default is represented by `policies/level1-conservative.json` and the embedded `DEFAULT_LEVEL1_POLICY`; tests require them to match.
- If the user supplies a policy, use that policy rather than quietly mixing it with remembered/default thresholds.
- Unknown policy fields must fail visibly instead of being ignored.
- Every Level 1 result must expose the policy id/fingerprint and stable `analysis_id` that produced it.
- If rules change, the policy fingerprint/analysis id must change.

Do not optimize or mutate the policy merely to turn a `no_trade`/`watch` into an actionable candidate.

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
- A schedule, monitor, notification or other wake event is only a **reason to re-analyse**; it is never evidence or execution authority.

## Decision provenance

A trader must be able to recover what ITA said under which rules and evidence.

- `analysis_id` identifies the Level 1 decision inputs/policy deterministically.
- `DecisionJournal` is an optional append-only JSONL analysis ledger.
- Journal records are analysis history, not orders, approvals or broker outcomes.
- Never write credentials or secrets into a journal.

## Coding rules

- Python 3.10+.
- Keep core deterministic tools dependency-light; stdlib-only by default.
- Tests for financial/trading arithmetic, policy behavior and output contracts.
- No credentials, broker tokens or API secrets in the repository.
- Do not add a broker SDK to core.
- Keep Apache-2.0 compatibility; do not copy source from incompatible/source-available projects such as Elastic License 2.0 repositories.

## Interop

IFMA is a sibling research source, not a runtime dependency. Exchange research via versioned JSON contracts under `schemas/`.

RiskPilot/execution remain separate downstream authorities. Optional future agent harnesses may manage sessions, schedules and monitors around ITA, but must not become a Level 1 core dependency.
