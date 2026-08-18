# Roadmap

## v0.2 — current: standalone Level 1

- one India Trader agent + skills, not an agent swarm;
- deterministic technical/risk/portfolio/trade-plan tools;
- **ticker -> official NSE/BSE EOD bhavcopy -> technicals -> regime -> setup/no-setup -> Trade Packet**;
- no IFMA, ProfitPilot or broker login required for Level 1;
- swing/positional cash-equity scope only;
- conservative long-only automatic setup derivation at Level 1;
- freshness/provenance gate and Trade Packet contract;
- local raw-report cache;
- simple cost-aware no-look-ahead MA sanity baseline;
- generic tests proving the path is not HDFCBANK-specific.

See [`LEVELS.md`](LEVELS.md) for the product boundaries.

## Level 2 — authenticated read-only market data

- provider adapter interface with explicit licences/terms;
- instrument master / canonical symbol resolution;
- Zerodha, Upstox and selected broker historical/read-only quote adapters;
- intraday intervals where provider rules permit;
- session-aware freshness and stronger microstructure context;
- Nifty/sector benchmark packets, breadth and relative strength.

**No broker execution.** Level 2 adds evidence, not trading authority.

## Level 3 — intelligence, strategy lab and independent control

- optional IFMA research context;
- trade ledger + MFE/MAE review utilities;
- walk-forward harness and parameter stability reports;
- optional TensorTrade adapter;
- optional Qlib adapter;
- RiskPilot Trade Intent schema/adapter;
- portfolio/account policy inputs and dry-run integration examples.

## Later

Derivatives only after cash-equity workflows are robust: futures/options instrument metadata, Greeks/margin adapters and India-specific expiry/microstructure.

Broker execution remains a separate project/layer behind independent control. ITA must not become ProfitPilot-with-a-new-name.

See [`PROFITPILOT_CONTRIBUTION_MAP.md`](PROFITPILOT_CONTRIBUTION_MAP.md) for which PP components may be extracted and which deliberately stay elsewhere.
