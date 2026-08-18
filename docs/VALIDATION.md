# Validation

Validation date: 18 August 2026.

## Level 1 standalone validation

v0.2 adds a real ticker-driven path:

```text
symbol -> official NSE/BSE EOD report -> technicals -> regime
       -> deterministic setup/watch/no-trade -> Trade Packet
```

The deterministic test suite now verifies that:
- the market-data parser accepts representative NSE zipped UDiFF and BSE CSV layouts;
- the same provider works for arbitrary symbols (`RELIANCE`, `TCS`) rather than a hard-coded stock;
- a ticker-only `analyze_symbol("RELIANCE")` path works without IFMA or ProfitPilot;
- a downtrend does not become an immediate long merely because a trade was requested;
- an extreme uptrend can return `no_trade` rather than chase an RSI-100 move;
- Level 1 rejects an intraday horizon;
- breakout references use the **prior** 20-session range so a breakout can genuinely trigger;
- generated packets preserve `execution.allowed=false`.

### Official NSE source check

NSE's public All Reports page lists `CM-UDiFF Common Bhavcopy Final (zip)` and, for 13 July 2026, the exact file `BhavCopy_NSE_CM_0_0_0_20260713_F_0000.csv.zip` (shown as 189.15 KB). The manual smoke test is pinned to that archived file.

An attempted smoke from a GitHub-hosted Azure runner timed out while reading `nsearchives.nseindia.com` after 45 seconds. Installation and all deterministic tests had succeeded; the failure was a network read timeout, not a parser/schema assertion. The provider now converts such timeouts into `MarketDataUnavailable` and the external-network smoke is manual rather than a required CI gate.

This distinction is intentional: deterministic correctness should not depend on whether an exchange archive accepts traffic from a particular cloud IP range.

## Original real-world validation — HDFCBANK

`examples/hdfcbank_real_2026-08-10.json` contains 50 NSE HDFCBANK daily observations from 1 June through 10 August 2026. Values were transcribed from the historical-data table at StockAnalysis.com; that page identifies S&P Global Market Intelligence as the underlying historical-data source and labels the quote as delayed.

This remains a **real historical fixture**, not a generated price series. It is a regression example, not the only input path anymore.

### Technical output

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

### Trade usability test

Instead of issuing a current long, the historical example creates a **conditional trend-reclaim watch**:

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

### Stale-data test

The identical Aug 10 packet is evaluated as-of Aug 18 with a 24-hour clock-age limit. The deterministic result becomes `invalid` with `market data freshness check failed: stale`.

ITA refuses to recompute a stale 20/50-session state from one new quote; a complete refreshed bar history is needed.

## CI policy

- Normal `tests` workflow: deterministic/offline, Python 3.10 and 3.12, required for every PR.
- `level1-network-smoke`: manual external connectivity diagnostic, not a correctness gate.
- `python -m compileall -q src` is included in normal CI.
