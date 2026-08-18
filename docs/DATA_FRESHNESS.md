# Data and freshness standard

## Current means timestamped

Every trading conclusion must expose source/provider and timestamp. “Latest” without a timestamp is not a data quality standard.

## Level 1 source

ITA Level 1 includes a no-login daily EOD provider for official NSE/BSE bhavcopy reports.

It records:
- exchange and symbol;
- source name (`nse_udiff_bhavcopy` / `bse_udiff_bhavcopy`);
- source kind (`exchange_public_report`);
- latest trade date and EOD timestamp;
- observation count and history range;
- requested as-of date;
- adjustment basis.

Raw successful reports are cached locally. Missing exchange reports (for example weekends/holidays or not-yet-published dates) are skipped; malformed reports fail visibly.

**EOD is not live.** Level 1 only supports swing/positional analysis. An EOD Trade Packet must not be repackaged as an intraday signal.

## Enough history

If a 50-session feature is cited, the input must contain at least 50 valid observations on a consistent basis. Level 1 requests at least 55 sessions and defaults to 80. A current quote does not repair a stale multi-session history.

## Corporate actions

Bhavcopy prices are treated as unadjusted official EOD observations. Split/bonus/rights and other actions can distort historical chart comparisons. The output therefore marks the adjustment basis and requires material discontinuities to be investigated instead of silently interpreted as market moves.

## Two different freshness questions

`assess_data_freshness()` remains a generic clock-age gate for timestamped feeds.

Level 1 uses a separate EOD freshness label:
- `latest_available_eod` — latest report is within a conservative five calendar days of the requested as-of date;
- `stale_eod` — older than that;
- `future_eod` — timestamp contradiction.

The five-day rule is intentionally conservative and is not a full exchange-calendar engine. A future Level 2 session calendar can replace this coarse bound.

## Provider failures

The core must fail visibly rather than silently switch to an unlabeled/stale source. Level 1 does not scrape HTML pages or fabricate bars. Future provider fallbacks must preserve source authority and timestamps explicitly.
