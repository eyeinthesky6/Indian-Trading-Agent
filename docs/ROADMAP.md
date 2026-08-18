# Roadmap

## v0.2.1 — current: Level 1 complete within EOD scope

- one India Trader agent + skills, not an agent swarm;
- deterministic technical/risk/portfolio/trade-plan tools;
- **ticker -> official NSE/BSE EOD bhavcopy -> technicals -> regime -> policy -> setup/no-setup -> Trade Packet**;
- no IFMA, ProfitPilot or broker login required for Level 1;
- swing/positional cash-equity scope only;
- conservative long-only automatic setup derivation at Level 1;
- explicit versioned `Level1Policy` instead of scattered strategy magic constants;
- reviewed policy JSON + schema + strict unknown-field rejection;
- stable `analysis_id` + policy fingerprint for decision provenance;
- optional append-only JSONL decision journal;
- freshness/provenance gate and Trade Packet contract;
- local raw-report cache;
- simple cost-aware no-look-ahead MA sanity baseline;
- generic tests proving the path is not HDFCBANK-specific and that policy changes can change decisions;
- agent/CLI/MCP behavior aligned to the same policy/provenance boundary.

Level 1 is now feature-complete for the deliberately narrow **EOD decision-support** product. Further work on Level 1 should be bug/data-quality fixes or evidence-backed policy improvements, not feature creep.

This does **not** claim the bundled policy has demonstrated alpha. Strategy validation remains research work.

See [`LEVELS.md`](LEVELS.md) for the product boundaries and [`OPENTRADE_LEARNINGS.md`](OPENTRADE_LEARNINGS.md) for the agent-harness review.

## Level 2 — authenticated read-only market data

- provider adapter interface with explicit licences/terms;
- instrument master / canonical symbol resolution;
- Zerodha, Upstox and selected broker historical/read-only quote adapters;
- intraday intervals where provider rules permit;
- session-aware freshness and stronger microstructure context;
- Nifty/sector benchmark packets, breadth and relative strength;
- optional external scheduling/monitor harness that can request a fresh re-analysis.

A timer/monitor/event is never market evidence or trade authority. After a wake, Level 2 must fetch fresh data and create a new analysis id/Trade Packet.

**No broker execution.** Level 2 adds evidence, not trading authority.

## Level 3 — intelligence, strategy lab and independent control

- optional IFMA research context;
- richer trade journal / MFE-MAE and thesis-review utilities;
- walk-forward harness and parameter stability reports;
- optional TensorTrade adapter;
- optional Qlib adapter;
- RiskPilot Trade Intent schema/adapter;
- portfolio/account policy inputs and dry-run integration examples;
- external agent-harness integration patterns (persistent sessions, schedules, monitors) without importing those runtimes into ITA core.

## Separate control/execution layer

Patterns such as manual/auto approval, timeout-to-deny, duplicate-order idempotency, per-agent order accounting and broker outcome audit belong **after ITA**, primarily in RiskPilot/execution. OpenTrade demonstrates why those controls are valuable, but they should not be pulled into Level 1 merely because they exist in another trading product.

## Later

Derivatives only after cash-equity workflows are robust: futures/options instrument metadata, Greeks/margin adapters and India-specific expiry/microstructure.

Broker execution remains a separate project/layer behind independent control. ITA must not become ProfitPilot-with-a-new-name or an OpenTrade clone.

See [`PROFITPILOT_CONTRIBUTION_MAP.md`](PROFITPILOT_CONTRIBUTION_MAP.md) for which PP components may be extracted and which deliberately stay elsewhere.
