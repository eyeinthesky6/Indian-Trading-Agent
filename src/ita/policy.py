from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Level1Policy:
    """Versioned, user-overridable policy for the deterministic Level 1 engine.

    Strategy thresholds live here rather than being scattered through setup code.
    A policy is data: it can be saved, reviewed, fingerprinted and replayed.
    """

    name: str = "conservative_eod"
    version: str = "1.0"

    # Data / indicator requirements.
    default_sessions: int = 80
    min_sessions: int = 55
    max_eod_age_days: int = 5
    fast_period: int = 20
    slow_period: int = 50
    rsi_period: int = 14
    atr_period: int = 14

    # Setup eligibility.
    max_atr_pct: float = 6.0
    max_rsi_new_long: float = 82.0
    min_volume_ratio: float = 0.25
    breakout_near_high_ratio: float = 0.98

    # Setup geometry, expressed mostly in ATR units.
    breakout_buffer_atr: float = 0.25
    breakout_buffer_pct: float = 0.002
    breakout_stop_atr: float = 1.25
    breakout_sma_stop_atr: float = 0.50
    pullback_band_atr: float = 0.35
    pullback_stop_atr: float = 1.50
    pullback_low_stop_atr: float = 0.25
    reclaim_band_atr: float = 0.25
    reclaim_stop_atr: float = 1.25
    range_stop_atr: float = 1.50
    chase_limit_atr: float = 0.75

    # Targets / risk.
    target_r_multiples: tuple[float, ...] = (2.0, 3.0)
    min_reward_to_risk: float = 1.5
    default_risk_fraction: float = 0.0075
    default_max_position_fraction: float = 0.20

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.version.strip():
            raise ValueError("policy name and version are required")
        if self.min_sessions < self.slow_period:
            raise ValueError("min_sessions must be >= slow_period")
        if self.default_sessions < self.min_sessions:
            raise ValueError("default_sessions must be >= min_sessions")
        if not 0 < self.fast_period < self.slow_period:
            raise ValueError("require 0 < fast_period < slow_period")
        if self.rsi_period <= 0 or self.atr_period <= 0:
            raise ValueError("indicator periods must be positive")
        if self.max_eod_age_days < 0:
            raise ValueError("max_eod_age_days must be non-negative")
        if not 0 < self.breakout_near_high_ratio <= 1:
            raise ValueError("breakout_near_high_ratio must be in (0, 1]")
        if not 0 <= self.max_rsi_new_long <= 100:
            raise ValueError("max_rsi_new_long must be between 0 and 100")
        if self.max_atr_pct <= 0 or self.min_volume_ratio < 0:
            raise ValueError("volatility/volume thresholds are invalid")
        for name in (
            "breakout_buffer_atr",
            "breakout_buffer_pct",
            "breakout_stop_atr",
            "breakout_sma_stop_atr",
            "pullback_band_atr",
            "pullback_stop_atr",
            "pullback_low_stop_atr",
            "reclaim_band_atr",
            "reclaim_stop_atr",
            "range_stop_atr",
            "chase_limit_atr",
            "min_reward_to_risk",
        ):
            if float(getattr(self, name)) < 0:
                raise ValueError(f"{name} must be non-negative")
        if not self.target_r_multiples or any(float(x) <= 0 for x in self.target_r_multiples):
            raise ValueError("target_r_multiples must contain positive values")
        if not 0 < self.default_risk_fraction <= 1:
            raise ValueError("default_risk_fraction must be in (0, 1]")
        if not 0 < self.default_max_position_fraction <= 1:
            raise ValueError("default_max_position_fraction must be in (0, 1]")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["target_r_multiples"] = list(self.target_r_multiples)
        return data

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @property
    def policy_id(self) -> str:
        return f"{self.name}@{self.version}:{self.fingerprint[:12]}"

    def metadata(self) -> dict[str, Any]:
        return {
            "id": self.policy_id,
            "name": self.name,
            "version": self.version,
            "fingerprint": self.fingerprint,
            "parameters": self.to_dict(),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Level1Policy":
        if not isinstance(raw, dict):
            raise ValueError("policy must be a JSON object")
        allowed = {field.name for field in fields(cls)}
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise ValueError(f"unknown Level 1 policy fields: {', '.join(unknown)}")
        values = dict(raw)
        if "target_r_multiples" in values:
            raw_targets = values["target_r_multiples"]
            if not isinstance(raw_targets, (list, tuple)):
                raise ValueError("target_r_multiples must be an array")
            values["target_r_multiples"] = tuple(float(x) for x in raw_targets)
        return cls(**values)


DEFAULT_LEVEL1_POLICY = Level1Policy()


def load_level1_policy(source: Level1Policy | dict[str, Any] | str | Path | None = None) -> Level1Policy:
    """Load a policy from an object, dict or JSON path; None means the reviewed default."""
    if source is None:
        return DEFAULT_LEVEL1_POLICY
    if isinstance(source, Level1Policy):
        return source
    if isinstance(source, dict):
        return Level1Policy.from_dict(source)
    path = Path(source).expanduser()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"could not read Level 1 policy: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in Level 1 policy: {path}") from exc
    return Level1Policy.from_dict(raw)
