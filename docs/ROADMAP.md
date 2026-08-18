# Roadmap

## v0.1 — current

- one India Trader agent + skills, not an agent swarm;
- deterministic technical/risk/portfolio/trade-plan tools;
- freshness gate and Trade Packet contract;
- IFMA JSON bridge;
- simple cost-aware no-look-ahead MA sanity baseline;
- real HDFCBANK fixture and validation.

## v0.2 — data and breadth

- provider adapter interface with explicit licences/terms;
- Nifty/sector benchmark packets;
- breadth and relative strength;
- corporate-action metadata contract;
- trade ledger + MFE/MAE review utilities.

## v0.3 — strategy lab

- walk-forward harness;
- parameter stability reports;
- benchmark/bootstrapping helpers;
- optional TensorTrade adapter;
- optional Qlib adapter.

## v0.4 — control integration

- RiskPilot Trade Intent schema/adapter;
- portfolio/account policy inputs;
- dry-run integration examples.

## Later

Derivatives only after cash-equity workflows are robust: futures/options instrument metadata, Greeks/margin adapters and India-specific expiry/microstructure. Broker execution remains a separate project/layer.
