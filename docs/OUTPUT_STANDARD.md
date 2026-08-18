# Trade Packet output standard

A normal trade request should be readable in under a minute.

## Decision block

- **Status:** NO TRADE / WATCH / ACTIONABLE CANDIDATE / INVALID
- **Instrument / exchange**
- **Market data:** provider + timestamp + timeframe
- **Horizon**
- **Regime**
- **Setup**
- **Trigger / entry**
- **Invalidation / stop**
- **Targets:** include R multiples
- **Size:** only if capital/risk budget supplied
- **Why it may work**
- **Why not to trade / key risks**
- **What changes status**

## Supporting detail

Only then expand into indicator calculations, IFMA context, portfolio impact or test evidence.

## Language

Use conditional trading language. “Breakout above ₹X would activate the setup” is better than “Buy at ₹X” when the trigger has not happened.
