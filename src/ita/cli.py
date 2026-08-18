from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyze import analyze_symbol
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

    analyze = subs.add_parser("analyze", help="Level 1: ticker -> official EOD data -> Trade Packet")
    analyze.add_argument("symbol", help="NSE/BSE cash-equity symbol, e.g. RELIANCE")
    analyze.add_argument("--exchange", choices=("NSE", "BSE"), default="NSE")
    analyze.add_argument("--horizon", choices=("swing", "positional"), default="swing")
    analyze.add_argument("--sessions", type=int, default=80)
    analyze.add_argument("--as-of", dest="as_of", help="YYYY-MM-DD; defaults to today in Asia/Kolkata")
    analyze.add_argument("--capital", type=float)
    analyze.add_argument("--risk-percent", type=float, default=0.75)
    analyze.add_argument("--max-position-percent", type=float, default=20.0)
    analyze.add_argument("--cache-dir")

    for name in ("snapshot", "size", "plan", "portfolio", "backtest", "validate"):
        p = subs.add_parser(name)
        p.add_argument("input", help="JSON input file")
    args = parser.parse_args(argv)

    if args.command == "analyze":
        _print(
            analyze_symbol(
                args.symbol,
                exchange=args.exchange,
                horizon=args.horizon,
                sessions=args.sessions,
                as_of=args.as_of,
                capital=args.capital,
                risk_fraction=args.risk_percent / 100.0,
                max_position_fraction=args.max_position_percent / 100.0,
                cache_dir=args.cache_dir,
            )
        )
        return 0

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
