from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backtest import backtest_ma_crossover
from .contracts import validate_trade_packet
from .indicators import technical_snapshot
from .portfolio import portfolio_risk_summary
from .regime import classify_regime
from .risk import position_size
from .tradeplan import build_trade_plan


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _print(value: dict) -> None:
    print(json.dumps(value, indent=2, sort_keys=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ita", description="Indian Trading Agent deterministic tools")
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("snapshot", "size", "plan", "portfolio", "backtest", "validate"):
        p = subs.add_parser(name)
        p.add_argument("input", help="JSON input file")
    args = parser.parse_args(argv)
    data = _load(args.input)

    if args.command == "snapshot":
        snap = technical_snapshot(
            data["closes"], data.get("highs"), data.get("lows"), data.get("volumes"),
            data.get("fast_period", 20), data.get("slow_period", 50),
            data.get("rsi_period", 14), data.get("atr_period", 14),
        )
        _print({"technical_snapshot": snap, "regime": classify_regime(snap)})
    elif args.command == "size":
        _print(position_size(**data))
    elif args.command == "plan":
        _print(build_trade_plan(**data))
    elif args.command == "portfolio":
        _print(portfolio_risk_summary(data["capital"], data["positions"]))
    elif args.command == "backtest":
        closes = data.pop("closes")
        _print(backtest_ma_crossover(closes, **data))
    elif args.command == "validate":
        _print(validate_trade_packet(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
