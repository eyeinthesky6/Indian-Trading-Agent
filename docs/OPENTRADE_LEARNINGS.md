# What ITA learns from OpenTrade

Reference reviewed: `OpenTradeOSS/OpenTrade` (August 2026).

OpenTrade and ITA solve different layers of the problem. OpenTrade is an agent **harness/runtime** around persistent Claude Code/Codex sessions and a brokerage MCP; ITA is a market-analysis/trade-decision toolkit. The useful move is to learn from its boundaries rather than turn ITA into an Electron trading terminal.

## License boundary

OpenTrade is distributed under the **Elastic License 2.0**, not an Apache/MIT-style open-source licence. ITA is Apache-2.0.

Therefore:
- do not copy OpenTrade source files into ITA;
- do not transliterate its implementations line-for-line;
- preserve this document as architecture research, not code provenance;
- independently implement only general engineering/product patterns that are useful to ITA.

## Patterns worth adopting now in Level 1

### 1. Strategy belongs outside the harness

OpenTrade tells each agent to maintain an explicit `STRATEGY.md` rather than freelancing beyond the user's agreed system. The corresponding ITA lesson is that setup/risk thresholds should not be scattered magic constants.

**ITA implementation:** `Level1Policy` + `policies/level1-conservative.json`.

The policy contains indicator periods, freshness limits, setup thresholds/geometry, target R multiples and default risk/exposure limits. Unknown policy fields fail instead of being silently ignored. Every policy is fingerprinted.

### 2. Decisions need durable provenance

OpenTrade keeps an append-only audit ledger for intents, approvals and outcomes. ITA does not execute, but the same principle is valuable for analysis: a trader should be able to answer *what did the system say, under which rules, using which evidence?*

**ITA implementation:** stable `analysis_id`, policy fingerprint in every Level 1 packet, and optional append-only JSONL `DecisionJournal`.

The journal is decision support only. It contains no broker credentials and grants no execution authority.

### 3. Read-only and action boundaries should be structural

OpenTrade explicitly separates read-only market-data tools from order tools and gates the latter. ITA Level 1 goes further: it exposes no execution tool at all and stamps `execution.allowed=false` in Trade Packets.

**ITA implementation:** keep Level 1 MCP/CLI read-only. Do not add order tools merely because an agent harness can support them.

### 4. Re-check evidence after a wake/event

OpenTrade's agent instructions distinguish a monitor trigger from authoritative fresh market evidence: when a monitor wakes the agent, the agent fetches a fresh quote before acting.

**ITA implication for future Level 2:** monitor/schedule events must be treated as *reasons to re-analyse*, never as trade authority. A wake should trigger fresh market-data retrieval and a new Trade Packet/analysis id.

## Valuable OpenTrade patterns for later layers — not Level 1

| OpenTrade pattern | ITA/RiskPilot destination | Why not Level 1 |
|---|---|---|
| Durable cron / signal monitors | Future external harness or Level 2 companion | EOD Level 1 is request/analysis, not an always-on runtime |
| Background agent wake coordinator | External harness / Codex Coordinator-style layer | Agent lifecycle is not trading logic |
| Manual/auto approval gate | RiskPilot + execution boundary | Approval matters only when an action can touch money |
| Timeout = auto-deny | RiskPilot/execution | Correct fail-safe pattern, but Level 1 cannot submit orders anyway |
| Idempotent duplicate order joining | Execution layer | Order lifecycle concern |
| Append-only order/activity audit | RiskPilot/execution; Level 1 adopts analysis-only journal | Different event types/authority |
| Per-agent order accounting | Execution/portfolio layer | Level 1 has no account or orders |
| Persistent agent folders and strategy files | Optional future workspace UX | Core Level 1 remains portable CLI/Python/MCP |
| Desktop terminal / Electron UI | Separate product shell if ever useful | UI should not become a core dependency |

## What not to copy

- Robinhood-specific MCP assumptions.
- Brokerage order parsing/gating implementation.
- Electron/PTY/desktop lifecycle code.
- Scheduler process supervision code.
- Database schema or telemetry stack.
- Any Elastic-licensed code into the Apache-2.0 ITA core.

Those components may be excellent in OpenTrade and still be wrong dependencies for ITA.

## Architectural read-through

The clean combined picture is:

```text
IFMA (optional research)
          │
          ▼
ITA Level 1/2  ── market evidence → Trade Packet
          │
          ▼
RiskPilot      ── approve/reject/policy/limits
          │
          ▼
Execution      ── broker/order lifecycle

Optional harness around the stack:
Codex/Claude sessions + schedules + monitors + UI
```

OpenTrade is strongest as evidence that the **harness** can and should be separate from the **trading intelligence and risk authority**. ITA should stay on the intelligence side of that boundary.
