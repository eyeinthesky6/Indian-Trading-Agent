---
description: Build a fresh, conditional India-native Trade Packet
argument-hint: "[NSE/BSE symbol] [swing|positional]"
---

# Trade

For an NSE/BSE **cash-equity swing or positional** request, use the standalone Level 1 ticker path first:

1. fetch official daily EOD bhavcopy history;
2. compute technical state;
3. classify regime;
4. derive setup/watch/no-trade;
5. build trigger, invalidation, targets and R:R;
6. size only if capital/risk budget is supplied;
7. return the Trade Packet with `execution.allowed=false`.

Do **not** require IFMA, ProfitPilot or a broker account for Level 1.

Use IFMA only when fundamental/event/macro context is relevant or explicitly requested. Keep its timestamp separate from market-data timestamps.

Level 1 is EOD only. If the request is intraday, do not stretch daily bhavcopy into an intraday answer; explain that Level 2 read-only market-data adapters are future scope.

The deterministic Level 1 auto-setup is long-only for cash equity. A bearish regime can produce a conditional reclaim watch or no-trade; do not invent overnight short eligibility.

Return `no_trade`, `watch`, `actionable_candidate` or `invalid` freely. Never manufacture a candidate merely to be helpful.
