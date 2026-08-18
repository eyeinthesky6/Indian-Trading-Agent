---
name: market-data-freshness-india
description: Establish source, timestamp, interval, adjustment basis and sufficiency of Indian market data before any current trading conclusion.
---

# India Market Data & Freshness

A trade decision is only as current as the bars behind it.

## Before analysis

State:
- exchange/instrument,
- source/provider,
- source timestamp and timezone,
- bar timeframe,
- date range / observation count,
- adjusted vs unadjusted price basis.

For current facts prefer official exchange data or a legitimate licensed/provider feed. Secondary delayed sites can be used for research/testing only when labelled accurately.

## Hard failures

Do not present an actionable setup when:
- timestamp is missing,
- history is too short for the indicator,
- a current quote has been appended to stale history without the missing bars,
- corporate action adjustment basis is unknown and materially affects the lookback,
- the user asks intraday questions using daily-close data.

Use the deterministic freshness gate for clock age, but remember that exchange holidays/session boundaries require market-calendar reasoning too.

## Output

Return a small provenance block: provider, as-of, timeframe, observations, adjustment basis, freshness status and any gaps.
