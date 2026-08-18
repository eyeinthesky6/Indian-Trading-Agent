from __future__ import annotations

import csv
import io
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo
from zipfile import BadZipFile, ZipFile

IST = ZoneInfo("Asia/Kolkata")
NSE_BHAVCOPY_BASE_URL = "https://nsearchives.nseindia.com/content/cm"
NSE_REPORTS_REFERER_URL = "https://www.nseindia.com/all-reports"
BSE_BHAVCOPY_BASE_URL = "https://www.bseindia.com/download/BhavCopy/Equity"
BSE_REPORTS_REFERER_URL = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx?ln=en-us"


class MarketDataError(RuntimeError):
    pass


class MarketDataUnavailable(MarketDataError):
    pass


class InsufficientHistory(MarketDataError):
    pass


@dataclass(frozen=True, slots=True)
class DailyBar:
    timestamp: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    exchange: str
    symbol: str
    source: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HistoryResult:
    symbol: str
    exchange: str
    bars: list[DailyBar]
    source_name: str
    source_kind: str
    authoritative: bool
    as_of_date: str
    latest_trade_date: str
    attempted_calendar_days: int
    cache_dir: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "exchange": self.exchange,
            "bars": [bar.to_dict() for bar in self.bars],
            "source_name": self.source_name,
            "source_kind": self.source_kind,
            "authoritative": self.authoritative,
            "as_of_date": self.as_of_date,
            "latest_trade_date": self.latest_trade_date,
            "attempted_calendar_days": self.attempted_calendar_days,
            "cache_dir": self.cache_dir,
        }


Fetcher = Callable[[str, str, float], bytes | None]


def _default_cache_dir() -> Path:
    override = os.getenv("ITA_MARKET_DATA_CACHE", "").strip()
    return Path(override).expanduser() if override else Path.home() / ".cache" / "indian-trading-agent" / "bhavcopy"


def _http_fetch(url: str, referer: str, timeout: float) -> bytes | None:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; IndianTradingAgent/0.2; +https://github.com/eyeinthesky6/Indian-Trading-Agent)",
            "Accept": "text/csv,application/zip,application/octet-stream;q=0.9,*/*;q=0.8",
            "Referer": referer,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in {404, 410}:
            return None
        raise MarketDataUnavailable(f"market-data provider returned HTTP {exc.code} for {url}") from exc
    except urllib.error.URLError as exc:
        raise MarketDataUnavailable(f"could not reach market-data provider for {url}: {exc.reason}") from exc


def _safe_float(value: object, field: str, symbol: str) -> float:
    try:
        number = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError) as exc:
        raise MarketDataError(f"invalid {field} for {symbol}: {value!r}") from exc
    if number < 0:
        raise MarketDataError(f"negative {field} for {symbol}: {number}")
    return number


def _validate_bar(open_: float, high: float, low: float, close: float, symbol: str) -> None:
    if min(open_, high, low, close) <= 0:
        raise MarketDataError(f"non-positive OHLC for {symbol}")
    if high < max(open_, close, low):
        raise MarketDataError(f"high is inconsistent for {symbol}")
    if low > min(open_, close, high):
        raise MarketDataError(f"low is inconsistent for {symbol}")


def _extract_csv_bytes(payload: bytes, *, zipped: bool) -> bytes:
    if not zipped:
        return payload
    try:
        with ZipFile(io.BytesIO(payload)) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not names:
                raise MarketDataError("NSE bhavcopy ZIP contained no CSV")
            return archive.read(names[0])
    except BadZipFile as exc:
        raise MarketDataError("NSE bhavcopy response was not a valid ZIP") from exc


def _row_to_bar(row: dict[str, str], *, symbol: str, exchange: str, source: str) -> DailyBar | None:
    segment = str(row.get("Sgmt", "")).strip().upper()
    instrument_type = str(row.get("FinInstrmTp", "")).strip().upper()
    row_symbol = str(row.get("TckrSymb", "")).strip().upper()
    if row_symbol != symbol:
        return None
    if segment and segment != "CM":
        return None
    if instrument_type and instrument_type != "STK":
        return None
    series = str(row.get("SctySrs", "")).strip().upper()
    if exchange == "NSE" and series and series != "EQ":
        return None

    trade_date = str(row.get("TradDt", "")).strip()
    if not trade_date:
        return None
    try:
        parsed_date = date.fromisoformat(trade_date[:10])
    except ValueError as exc:
        raise MarketDataError(f"invalid trade date for {symbol}: {trade_date!r}") from exc

    open_ = _safe_float(row.get("OpnPric"), "open", symbol)
    high = _safe_float(row.get("HghPric"), "high", symbol)
    low = _safe_float(row.get("LwPric"), "low", symbol)
    close = _safe_float(row.get("ClsPric"), "close", symbol)
    volume = _safe_float(row.get("TtlTradgVol", 0), "volume", symbol)
    _validate_bar(open_, high, low, close, symbol)
    timestamp = datetime(parsed_date.year, parsed_date.month, parsed_date.day, 15, 30, tzinfo=IST).isoformat()
    return DailyBar(
        timestamp=timestamp,
        trade_date=parsed_date.isoformat(),
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
        exchange=exchange,
        symbol=symbol,
        source=source,
    )


class BhavcopyHistoryProvider:
    """No-login daily EOD history from official NSE/BSE bhavcopy archives.

    The provider downloads one small daily market report at a time and caches it locally.
    It is intentionally EOD-only; it is not a live quote source.
    """

    def __init__(self, *, cache_dir: str | Path | None = None, fetcher: Fetcher | None = None, timeout: float = 30.0):
        self.cache_dir = Path(cache_dir).expanduser() if cache_dir else _default_cache_dir()
        self.fetcher = fetcher or _http_fetch
        self.timeout = float(timeout)

    @staticmethod
    def _source_config(exchange: str, trade_date: date) -> tuple[str, str, str, bool]:
        token = trade_date.strftime("%Y%m%d")
        if exchange == "NSE":
            filename = f"BhavCopy_NSE_CM_0_0_0_{token}_F_0000.csv.zip"
            return f"{NSE_BHAVCOPY_BASE_URL}/{filename}", NSE_REPORTS_REFERER_URL, "nse_udiff_bhavcopy", True
        if exchange == "BSE":
            filename = f"BhavCopy_BSE_CM_0_0_0_{token}_F_0000.CSV"
            return f"{BSE_BHAVCOPY_BASE_URL}/{filename}", BSE_REPORTS_REFERER_URL, "bse_udiff_bhavcopy", False
        raise ValueError("exchange must be NSE or BSE")

    def _payload_for_date(self, exchange: str, trade_date: date) -> tuple[bytes | None, str, bool]:
        url, referer, source_name, zipped = self._source_config(exchange, trade_date)
        suffix = ".zip" if zipped else ".csv"
        cache_path = self.cache_dir / exchange.lower() / f"{trade_date.isoformat()}{suffix}"
        if cache_path.exists() and cache_path.stat().st_size > 0:
            return cache_path.read_bytes(), source_name, zipped
        payload = self.fetcher(url, referer, self.timeout)
        if payload is None:
            return None, source_name, zipped
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(payload)
        return payload, source_name, zipped

    def _bar_for_date(self, symbol: str, exchange: str, trade_date: date) -> DailyBar | None:
        payload, source_name, zipped = self._payload_for_date(exchange, trade_date)
        if payload is None:
            return None
        csv_bytes = _extract_csv_bytes(payload, zipped=zipped)
        text = csv_bytes.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames or "TckrSymb" not in reader.fieldnames:
            raise MarketDataError(f"unexpected {exchange} bhavcopy schema for {trade_date.isoformat()}")
        for row in reader:
            bar = _row_to_bar(row, symbol=symbol, exchange=exchange, source=source_name)
            if bar is not None:
                return bar
        return None

    def fetch_symbol_history(
        self,
        symbol: str,
        *,
        exchange: str = "NSE",
        sessions: int = 80,
        as_of: str | date | None = None,
        max_calendar_days: int = 180,
    ) -> HistoryResult:
        symbol = str(symbol).strip().upper()
        exchange = str(exchange).strip().upper()
        if not symbol:
            raise ValueError("symbol is required")
        if sessions < 2:
            raise ValueError("sessions must be at least 2")
        if max_calendar_days < sessions:
            raise ValueError("max_calendar_days must be >= sessions")
        if isinstance(as_of, date):
            end_date = as_of
        elif isinstance(as_of, str) and as_of.strip():
            end_date = date.fromisoformat(as_of.strip()[:10])
        else:
            end_date = datetime.now(IST).date()

        bars_desc: list[DailyBar] = []
        attempted = 0
        source_name = "nse_udiff_bhavcopy" if exchange == "NSE" else "bse_udiff_bhavcopy"
        for offset in range(max_calendar_days):
            current = end_date - timedelta(days=offset)
            attempted += 1
            if current.weekday() >= 5:
                continue
            bar = self._bar_for_date(symbol, exchange, current)
            if bar is not None:
                bars_desc.append(bar)
                if len(bars_desc) >= sessions:
                    break

        if len(bars_desc) < sessions:
            raise InsufficientHistory(
                f"only {len(bars_desc)} {exchange} sessions found for {symbol}; requested {sessions} within {max_calendar_days} calendar days"
            )
        bars = list(reversed(bars_desc))
        return HistoryResult(
            symbol=symbol,
            exchange=exchange,
            bars=bars,
            source_name=source_name,
            source_kind="exchange_public_report",
            authoritative=True,
            as_of_date=end_date.isoformat(),
            latest_trade_date=bars[-1].trade_date,
            attempted_calendar_days=attempted,
            cache_dir=str(self.cache_dir),
        )
