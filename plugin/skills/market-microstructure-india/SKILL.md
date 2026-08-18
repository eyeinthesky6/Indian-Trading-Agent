---
name: market-microstructure-india
description: Check current NSE/BSE session, product, settlement, circuit, tick/lot and short-selling constraints that affect whether an analytical setup is executable.
---

# India Market Microstructure

Analytical direction and executable trade are different questions.

When relevant verify **current** authoritative rules for:
- exchange/session/auction timings,
- product eligibility and settlement,
- cash-equity short-selling constraints,
- circuit/filter bands,
- tick and lot size,
- corporate-action/ex-date effects,
- transaction taxes/fees/charges,
- broker margin/product rules.

Do not hard-code changing statutory/broker rates into prose from memory. Costs supplied to deterministic backtests must be timestamped assumptions or user/provider inputs.

If a setup cannot be expressed in the requested product/horizon, mark it invalid or propose an analytical alternative without pretending execution is available.
