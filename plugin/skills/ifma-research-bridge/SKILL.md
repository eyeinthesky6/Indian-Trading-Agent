---
name: ifma-research-bridge
description: Consume optional Indian Financial Market Analysis Agent research as timestamped context for a trade without duplicating IFMA or making it a runtime dependency.
---

# IFMA Research Bridge

IFMA answers research questions; ITA answers trade-structure questions.

Accept a small research packet containing:
- symbol/entity,
- as-of timestamp,
- short summary,
- catalysts,
- risks,
- optional valuation/fundamental/governance/macro views,
- evidence/source references when available.

Do not import IFMA core into ITA. Keep the boundary JSON-based so either repo can evolve independently.

Use IFMA context to identify event risk, catalyst alignment or thesis conflicts. Do not let a positive fundamental view automatically override a bearish technical setup, or vice versa; explain the time-horizon difference.

Never make stale IFMA research fresh merely because the chart data is current.
