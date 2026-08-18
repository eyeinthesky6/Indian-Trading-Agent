---
name: trade-planning-india
description: Convert a valid setup into a structured Trade Packet with status, trigger, entry zone, invalidation, targets, R multiples and reasons not to trade.
---

# Trade Planning

Never confuse a watch condition with a current entry.

## Required fields

- status,
- symbol/exchange,
- data as-of,
- horizon,
- side,
- setup,
- trigger/entry condition,
- entry zone,
- invalidation/stop,
- targets or exit framework,
- R multiples,
- reasons for,
- reasons not to trade,
- what changes status.

Use representative entry consistently for R calculations. A stop belongs where the setup thesis fails; size adapts to it.

`actionable_candidate` still means review required. The packet must preserve `execution.allowed=false`.
