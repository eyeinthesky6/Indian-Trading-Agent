---
name: strategy-testing-india
description: Design and interpret leakage-aware Indian trading strategy tests with explicit costs, signal timing, benchmark, walk-forward validation and failure analysis.
---

# Strategy Testing

Backtests are debugging tools before they are performance claims.

## Minimum standard

State:
- universe and period,
- data source/adjustment basis,
- signal time and execution time,
- costs/slippage,
- position sizing,
- benchmark,
- train/validation/test separation if parameters were tuned.

Avoid:
- same-bar look-ahead,
- survivorship bias,
- post-event information leakage,
- silently ignoring costs,
- optimising on the final test window,
- reporting only Sharpe or CAGR without drawdown/trade count.

Begin with a simple baseline. The bundled MA crossover is deliberately a sanity harness, not a claim of edge. TensorTrade/Qlib can be adapters later; they do not replace validation discipline.
