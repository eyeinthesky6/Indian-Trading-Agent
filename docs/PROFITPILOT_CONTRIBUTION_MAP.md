# ProfitPilot contribution map

ProfitPilot is a **donor/reference codebase**, not an ITA runtime dependency.

The useful architectural lesson is to extract small, independently understandable contracts from PP rather than importing its large application graph into ITA.

| ProfitPilot capability | Useful destination | ITA level | Posture |
|---|---|---:|---|
| NSE/BSE public bhavcopy ingestion | ITA market-data provider | 1 | **Extracted now** as a stdlib-only EOD provider |
| Canonical OHLCV/timestamp normalization | ITA market-data core | 1/2 | Reuse the contract/validation ideas; keep ITA implementation small |
| Historical interval/cadence validation | ITA provider validation | 2 | Extract when intraday adapters arrive |
| Instrument master / broker token mapping | ITA read-only provider layer | 2 | Extract a small symbol contract; do not import PP DB/runtime |
| Zerodha historical candle fetcher | ITA optional provider | 2 | Future read-only adapter |
| Upstox historical candle fetcher | ITA optional provider | 2 | Future read-only adapter |
| ICICI/Breeze historical candle fetcher | ITA optional provider | 2 | Future read-only adapter |
| Flattrade market-data adapter | ITA optional provider | 2 | Future read-only adapter if justified |
| Market-data source quality/authority metadata | ITA provenance model | 1/2 | Reuse concepts; keep fail-visible source labels |
| Opportunity screener/factor engine | IFMA + ITA idea generation | 3 | Extract only if it can be made data-provider neutral |
| Regime feature generation | ITA regime research | 3 | Compare/port useful features; do not duplicate blindly |
| Replay/backtesting infrastructure | ITA strategy lab | 3 | Mine for no-look-ahead, data lineage and replay contracts |
| Risk gates / unfamiliarity / symbol gates | RiskPilot | 3 | **Do not move into ITA**; RiskPilot owns independent control |
| Broker auth, order lifecycle and execution bridges | Separate execution layer | future | **Do not move into ITA** |
| Supabase/runtime/bootstrap/audit plumbing | ProfitPilot itself | — | Leave behind unless a tiny standalone contract is genuinely required |

## What Level 1 actually reused

The Level 1 provider follows the production lessons already learned in PP:
- prefer official exchange EOD reports for no-login daily history;
- preserve source and timestamp provenance;
- normalize a stable OHLCV shape;
- reject malformed price geometry;
- cache successful raw reports locally;
- fail visibly instead of fabricating missing data.

The implementation is independent and uses Python stdlib only. Installing or running ProfitPilot is not required.

## Extraction rule

When a PP component looks reusable, ask:

1. Can its useful contract be explained in one page?
2. Can it run without PP settings, Supabase, broker execution or global runtime state?
3. Does ITA truly need it at its current level?
4. Can it be tested with deterministic fixtures?
5. Would extracting it reduce duplication rather than create a second framework?

If the answer is no, leave it in ProfitPilot.

## Possible future shared package

Only if Level 2 creates real duplication across IFMA, ITA, RiskPilot and execution should we consider a tiny shared project such as an `india-market-data-core` containing **data contracts and normalization only**. Do not create that package pre-emptively.
