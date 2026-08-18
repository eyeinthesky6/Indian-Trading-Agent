# IFMA integration

ITA and IFMA are sibling repositories with **loose coupling**.

## Contract

IFMA can export or a user can construct a packet matching `schemas/ifma_research_packet.schema.json`:

```json
{
  "symbol": "HDFCBANK",
  "as_of": "2026-08-18T18:00:00+05:30",
  "summary": "Short research summary",
  "catalysts": ["..."],
  "risks": ["..."],
  "fundamental_view": "...",
  "valuation_view": "..."
}
```

ITA may attach that context to the trading analysis. It must preserve the IFMA timestamp and source basis.

## No hard import

Do not add `indian-financial-market-analysis-agent` as an ITA Python dependency. Advantages:
- independent install/versioning,
- no analyst code in the execution path,
- easier interoperability with other research agents,
- clearer provenance when research is absent or stale.

## Time-horizon disagreement

A strong company can have a poor short-term setup; a weak company can rally. Report the disagreement rather than forcing the two agents to vote on a single bullish/bearish label.
