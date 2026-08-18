from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_journal_path() -> Path:
    override = os.getenv("ITA_DECISION_JOURNAL", "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".local" / "share" / "indian-trading-agent" / "decisions.jsonl"


class DecisionJournal:
    """Small append-only JSONL ledger for Level 1 analysis decisions.

    This records decision-support output, not orders. Nothing here grants execution
    authority and no broker credentials belong in the journal.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path).expanduser() if path else default_journal_path()

    def append(self, result: dict[str, Any]) -> dict[str, Any]:
        packet = result.get("trade_packet") if isinstance(result, dict) else None
        if not isinstance(packet, dict):
            raise ValueError("journal result must contain a trade_packet")
        analysis_id = str(result.get("analysis_id") or "").strip()
        if not analysis_id:
            raise ValueError("journal result must contain analysis_id")

        record = {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "analysis_id": analysis_id,
            "symbol": result.get("symbol"),
            "exchange": result.get("exchange"),
            "horizon": result.get("horizon"),
            "status": packet.get("status"),
            "setup": packet.get("setup"),
            "policy_id": (result.get("policy") or {}).get("id") if isinstance(result.get("policy"), dict) else None,
            "market_data_as_of": (result.get("market_data") or {}).get("history_end") if isinstance(result.get("market_data"), dict) else None,
            "result": result,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n")
        return {
            "recorded": True,
            "path": str(self.path),
            "analysis_id": analysis_id,
            "recorded_at_utc": record["recorded_at_utc"],
        }

    def list(self, *, limit: int = 20, symbol: str | None = None) -> list[dict[str, Any]]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        if not self.path.exists():
            return []
        wanted = symbol.strip().upper() if symbol else None
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                text = line.strip()
                if not text:
                    continue
                try:
                    record = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                if wanted and str(record.get("symbol") or "").upper() != wanted:
                    continue
                records.append(record)
        return records[-limit:][::-1]
