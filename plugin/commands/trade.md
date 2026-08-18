---
description: Build a fresh, policy-grounded India-native Trade Packet
argument-hint: "[NSE/BSE symbol] [swing|positional]"
---

# Trade

For an NSE/BSE **cash-equity swing or positional** request, use the standalone Level 1 ticker path first:

1. load the selected `Level1Policy` (reviewed default unless the user supplies another policy);
2. fetch official daily EOD bhavcopy history;
3. compute the policy's technical state;
4. classify regime;
5. derive setup/watch/no-trade under that policy;
6. build trigger, invalidation, targets and policy minimum R:R;
7. size only if capital/risk budget is supplied;
8. return the Trade Packet with `analysis_id`, policy id/fingerprint and `execution.allowed=false`;
9. journal only when the user requests persistent decision history.

Do **not** require IFMA, ProfitPilot or a broker account for Level 1.

Do not improvise or relax thresholds merely because the user asked for a trade. If they want a different system, change/select an explicit policy and make that change visible in the output.

Use IFMA only when fundamental/event/macro context is relevant or explicitly requested. Keep its timestamp separate from market-data timestamps.

Level 1 is EOD only. If the request is intraday, do not stretch daily bhavcopy into an intraday answer; explain that Level 2 read-only market-data adapters are future scope.

The deterministic Level 1 auto-setup is long-only for cash equity. A bearish regime can produce a conditional reclaim watch or no-trade; do not invent overnight short eligibility.

A future timer/monitor/wake is only a reason to fetch fresh evidence and rerun Level 1/2. It is never trade authority by itself.

Return `no_trade`, `watch`, `actionable_candidate` or `invalid` freely. Never manufacture a candidate merely to be helpful.
