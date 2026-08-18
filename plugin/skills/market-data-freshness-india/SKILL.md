---
name: market-data-freshness-india
description: Establish source, timestamp, interval, adjustment basis and sufficiency of Indian market data before any trading conclusion; includes ITA Level 1 official EOD bhavcopy.
---

# India Market Data & Freshness

A trade decision is only as current as the bars behind it.

## Level 1 bundled source

For NSE/BSE cash-equity **swing/positional** analysis, ITA Level 1 can fetch official public daily bhavcopy itself using `BhavcopyHistoryProvider` / `analyze_symbol()`.

This path requires:
- no IFMA;
- no ProfitPilot;
- no broker account/API key.

Provenance must expose:
- exchange and symbol,
- source (`nse_udiff_bhavcopy` / `bse_udiff_bhavcopy`),
- source kind (`exchange_public_report`),
- latest trade date/timestamp,
- daily EOD mode,
- observation count + history range,
- unadjusted basis.

Successful raw reports may be cached locally. Missing dates may reflect weekends/holidays/not-yet-published reports; malformed payloads must fail visibly.

## EOD is not live

Level 1 data is daily EOD. Never use it to answer an intraday setup question. Never label it real-time merely because it is the latest available daily report.

## Before any other data analysis

State:
- exchange/instrument,
- source/provider,
- timestamp and timezone,
- bar timeframe,
- date range / observation count,
- adjusted vs unadjusted price basis.

For future Level 2 current/intraday facts, prefer legitimate authenticated/licensed provider data with explicit authority and timestamp.

## Hard failures

Do not present an actionable setup when:
- timestamp/source is missing,
- history is too short for the indicator,
- a current quote has been appended to stale history without missing bars,
- a corporate action materially distorts the unadjusted lookback,
- the user asks intraday questions using Level 1 daily-close data,
- the latest EOD report is beyond the conservative freshness bound.

## Corporate actions

Bhavcopy is treated as unadjusted official observation data. Splits, bonuses, rights and similar events can create artificial chart discontinuities. Flag material discontinuities for verification rather than interpreting them as ordinary price moves.

## Output

Return a compact provenance block: provider, exchange, as-of, mode/timeframe, observations, adjustment basis, freshness status and any gaps.
