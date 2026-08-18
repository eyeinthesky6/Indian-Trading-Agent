"""Indian Trading Agent deterministic toolkit."""

from .analyze import analyze_symbol
from .backtest import backtest_ma_crossover
from .contracts import validate_trade_packet
from .freshness import assess_data_freshness
from .indicators import technical_snapshot
from .portfolio import portfolio_risk_summary
from .regime import classify_regime
from .risk import position_size, reward_to_risk
from .tradeplan import build_trade_plan

__all__ = [
    "analyze_symbol",
    "assess_data_freshness",
    "backtest_ma_crossover",
    "technical_snapshot",
    "validate_trade_packet",
    "portfolio_risk_summary",
    "classify_regime",
    "position_size",
    "reward_to_risk",
    "build_trade_plan",
]

__version__ = "0.2.0"
