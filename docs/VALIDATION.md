# Real-world validation — HDFCBANK

Validation date: 18 August 2026.

## Input

`examples/hdfcbank_real_2026-08-10.json` contains 50 NSE HDFCBANK daily observations from 1 June through 10 August 2026. Values were transcribed from the historical-data table at StockAnalysis.com; that page identifies S&P Global Market Intelligence as the underlying historical-data source and labels the quote as delayed.

This is a **real historical fixture**, not a generated price series.

## Technical output

`ita snapshot` returned:

| Metric | Result |
|---|---:|
| Close | ₹731.00 |
| SMA 20 | ₹759.3275 |
| SMA 50 | ₹773.4370 |
| RSI 14 | 35.22 |
| 5-session momentum | -2.92% |
| 20-session momentum | -10.63% |
| Realised volatility 20 | 22.29% annualised |
| ATR 14 | ₹12.6471 / 1.73% |
| Regime | trending_down |

The output is consistent with the visible price history: the stock had fallen sharply from the July highs and remained below both moving averages.

## Trade usability test

Instead of issuing a current long, the example creates a **conditional trend-reclaim watch**:

- current historical close: ₹731
- trigger/entry zone: ₹758–762, `cross_above_zone`
- invalidation: ₹744
- targets: ₹790 / ₹820
- midpoint R:R: 1.88R / 3.75R
- sample capital: ₹5,00,000
- risk budget: 0.75%
- max position: 20%

Result: `status = watch` because price had not reached the trigger. Sizing returns 131 shares; the 20% notional cap binds before the 0.75% stop-risk budget, leaving modelled stop risk at about 0.419% of capital.

The purpose of this fixture is **not** to claim this historical idea made money. It tests whether the software represents a conditional setup correctly.

## Stale-data test

The identical Aug 10 packet is evaluated as-of Aug 18 with a 24-hour clock-age limit. The deterministic result becomes `invalid` with `market data freshness check failed: stale`.

That matters because a separate current source reported HDFC Bank at ₹723.20 on 18 August 2026. ITA correctly refuses to recompute the Aug 10 20/50-session state from that lone new quote; a complete refreshed bar history is needed.

## Test suite

The initial release runs 17 stdlib unit tests covering indicators/regime, risk sizing, R:R, portfolio concentration, trade geometry, freshness, output contract, plugin alignment and no-look-ahead baseline mechanics.
