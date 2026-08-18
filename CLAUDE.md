# Claude Code guidance

Use `plugin/agents/india-trader.md` as the product behaviour contract and `AGENTS.md` as the repository boundary.

Before changing trade logic:
1. keep execution disabled,
2. preserve data provenance/freshness,
3. add or update deterministic tests,
4. keep IFMA integration loose through schemas rather than importing the sibling repo.
