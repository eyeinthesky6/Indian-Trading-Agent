# Data and freshness standard

## Current means timestamped

Every current trading conclusion must expose source/provider and timestamp. “Latest” without a timestamp is not a data quality standard.

## Enough history

If a 50-session feature is cited, the input must contain at least 50 valid observations on a consistent basis. A current quote does not repair a stale multi-session history.

## Corporate actions

Split/bonus/rights and other actions can distort unadjusted price histories and share counts. State the adjustment basis and verify material discontinuities before reading them as market moves.

## Freshness gate

`assess_data_freshness()` is intentionally a clock-age gate. It cannot know exchange holidays, special sessions or whether the provider itself is delayed. The agent must add session/calendar/provider reasoning.

## No bundled scraper

ITA ships no unsupported NSE/BSE scraper. Users can supply data or add legitimate provider adapters. The core should fail visibly rather than silently degrade to stale data.
