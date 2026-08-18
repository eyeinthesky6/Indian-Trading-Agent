---
name: setup-detection-india
description: Turn technical/regime evidence into explicit conditional setups while allowing no-trade when trigger and invalidation are not coherent.
---

# Setup Detection

A setup is a falsifiable hypothesis.

Supported starting frameworks include:
- breakout / breakdown,
- pullback in established trend,
- trend/MA reclaim after correction,
- range mean reversion,
- relative-strength continuation,
- event gap/level reaction.

For each candidate specify:
- why this setup fits the regime,
- exact trigger condition,
- invalidation condition,
- likely holding horizon,
- evidence against it.

Avoid indicator voting (“4 of 5 bullish”). Confluence only matters when each feature measures a distinct thing.

If price is extended, trigger is already missed, R:R is poor, data is stale or regime conflicts strongly, return `no_trade` or `watch`.
