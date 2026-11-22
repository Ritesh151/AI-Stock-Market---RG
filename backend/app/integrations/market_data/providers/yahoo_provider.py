"""
Yahoo Finance Market Data Provider.
Asynchronous HTTP market data provider for NSE and BSE equities with source attribution.
Classifies live market data as DELAYED (~15 min delay) in strict adherence to data transparency rules.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import zoneinfo
import httpx

from app.core.logging import get_logger
from app.integrations.market_data.base import MarketDataProvider
from app.integrations.market_data.exceptions import (
    StockNotFoundError,
    ProviderUnavailableError,
    RateLimitExceededError,
    InvalidTimeframeError,
)
from app.integrations.market_data.provider_config import (
    DataFreshness,
    SUPPORTED_CHART_RANGES,
    SUPPORTED_CHART_INTERVALS,
    ALLOWED_INTERVALS_BY_RANGE,
    EXCHANGE_SUFFIX_MAP,
    MARKET_TIMEZONE,
    MARKET_OPEN_HOUR,
    MARKET_OPEN_MINUTE,
    MARKET_CLOSE_HOUR,
    MARKET_CLOSE_MINUTE,
)

logger = get_logger("integrations.market_data.yahoo")

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 RG-AI/1.0"
)

# Standard range parameter conversion for Yahoo API
_YAHOO_RANGE_MAP = {
    "1D": "1d",
    "5D": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y",
}

_YAHOO_INTERVAL_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "60m",
    "1d": "1d",
    "1wk": "1wk",
}


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance API adapter with rate-limit protection and retries."""

    def __init__(
        self,
        timeout_seconds: int = 10,
        max_retries: int = 3,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @property
    def provider_name(self) -> str:
        return "Yahoo Finance (Delayed ~15m)"

    def _get_ticker_symbol(self, symbol: str, exchange: Optional[str] = "NSE") -> str:
        """Appends appropriate .NS or .BO exchange suffix."""
        cleaned = symbol.strip().upper()
        if cleaned.endswith(".NS") or cleaned.endswith(".BO") or cleaned.startswith("^"):
            return cleaned

        suffix = EXCHANGE_SUFFIX_MAP.get((exchange or "NSE").upper(), ".NS")
        return f"{cleaned}{suffix}"

    def _strip_ticker_suffix(self, ticker: str) -> str:
        """Removes .NS or .BO suffix from ticker for clean display."""
        if ticker.endswith(".NS"):
            return ticker[:-3]
        if ticker.endswith(".BO"):
            return ticker[:-3]
        return ticker

    async def _execute_http(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes GET request with exponential backoff retry and status mapping."""
        headers = {"User-Agent": _USER_AGENT, "Accept": "application/json"}
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=float(self.timeout_seconds)) as client:
                    resp = await client.get(url, params=params, headers=headers)

                if resp.status_code == 200:
                    return resp.json()

                if resp.status_code == 404:
                    raise StockNotFoundError(symbol=params.get("q", "unknown") if params else "symbol")

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 2))
                    if attempt < self.max_retries:
                        await asyncio.sleep(retry_after * attempt)
                        continue
                    raise RateLimitExceededError(provider_name=self.provider_name, retry_after=retry_after)

                # 5xx or transient 4xx
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * attempt)
                    continue

                raise ProviderUnavailableError(
                    provider_name=self.provider_name,
                    message=f"Yahoo Finance returned HTTP {resp.status_code}",
                )

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * attempt)
                    continue
                raise ProviderUnavailableError(
                    provider_name=self.provider_name,
                    message=f"Request to Yahoo Finance timed out: {exc}",
                )

        raise ProviderUnavailableError(provider_name=self.provider_name, message=str(last_error))

    async def search_stocks(
        self,
        query: str,
        exchange: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        q = query.strip()
        if not q:
            return []

        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {"q": q, "quotesCount": 15, "newsCount": 0}

        try:
            data = await self._execute_http(url, params=params)
        except Exception as e:
            logger.warning(f"Yahoo search error for '{q}': {e}")
            return []

        quotes = data.get("quotes", [])
        results: List[Dict[str, Any]] = []

        target_exchange = exchange.upper() if exchange else None

        for item in quotes:
            symbol = item.get("symbol", "")
            # Filter for Indian equities
            is_nse = symbol.endswith(".NS") or item.get("exchange") in {"NSI", "NSE"}
            is_bse = symbol.endswith(".BO") or item.get("exchange") in {"BSE", "BOM"}

            if not (is_nse or is_bse):
                continue

            item_exch = "NSE" if is_nse else "BSE"
            if target_exchange and item_exch != target_exchange:
                continue

            clean_sym = self._strip_ticker_suffix(symbol)
            company_name = (
                item.get("longname")
                or item.get("shortname")
                or clean_sym
            )

            results.append({
                "symbol": clean_sym,
                "company_name": company_name,
                "exchange": item_exch,
                "currency": "INR",
                "type": item.get("quoteType", "EQUITY"),
            })

        return results

    async def get_quote(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        ticker = self._get_ticker_symbol(symbol, exchange)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {"range": "1d", "interval": "1d"}

        try:
            data = await self._execute_http(url, params=params)
        except StockNotFoundError:
            raise StockNotFoundError(symbol=symbol, exchange=exchange)

        chart = data.get("chart", {})
        result_list = chart.get("result", [])
        if not result_list:
            error = chart.get("error", {})
            err_desc = error.get("description", "Symbol not found")
            raise StockNotFoundError(symbol=symbol, exchange=exchange, message=err_desc)

        meta = result_list[0].get("meta", {})
        indicators = result_list[0].get("indicators", {}).get("quote", [{}])[0]

        last_price = meta.get("regularMarketPrice")
        previous_close = meta.get("chartPreviousClose") or meta.get("previousClose")

        change = None
        change_percent = None
        if last_price is not None and previous_close is not None and previous_close > 0:
            change = round(last_price - previous_close, 2)
            change_percent = round((change / previous_close) * 100, 2)

        open_val = indicators.get("open", [None])
        open_price = open_val[0] if open_val and open_val[0] is not None else meta.get("regularMarketDayOpen")

        high_val = indicators.get("high", [None])
        day_high = high_val[0] if high_val and high_val[0] is not None else meta.get("regularMarketDayHigh")

        low_val = indicators.get("low", [None])
        day_low = low_val[0] if low_val and low_val[0] is not None else meta.get("regularMarketDayLow")

        vol_val = indicators.get("volume", [None])
        volume = vol_val[0] if vol_val and vol_val[0] is not None else meta.get("regularMarketVolume")

        market_time = meta.get("regularMarketTime")
        market_ts = (
            datetime.fromtimestamp(market_time, tz=timezone.utc).isoformat()
            if market_time
            else None
        )
        now_ts = datetime.now(timezone.utc).isoformat()

        exch_name = "NSE" if ticker.endswith(".NS") else "BSE" if ticker.endswith(".BO") else exchange or "NSE"

        return {
            "symbol": self._strip_ticker_suffix(symbol),
            "company_name": meta.get("longName") or meta.get("shortName") or self._strip_ticker_suffix(symbol),
            "exchange": exch_name,
            "currency": meta.get("currency", "INR"),
            "last_price": round(float(last_price), 2) if last_price is not None else None,
            "previous_close": round(float(previous_close), 2) if previous_close is not None else None,
            "change": change,
            "change_percent": change_percent,
            "open": round(float(open_price), 2) if open_price is not None else None,
            "day_high": round(float(day_high), 2) if day_high is not None else None,
            "day_low": round(float(day_low), 2) if day_low is not None else None,
            "volume": int(volume) if volume is not None else None,
            "market_cap": None,  # Not provided in chart API
            "data_status": DataFreshness.DELAYED.value,
            "source_name": self.provider_name,
            "market_timestamp": market_ts,
            "fetched_at": now_ts,
        }

    async def get_historical_data(
        self,
        symbol: str,
        range_str: str = "1M",
        interval: str = "1d",
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        if range_str not in SUPPORTED_CHART_RANGES or interval not in SUPPORTED_CHART_INTERVALS:
            raise InvalidTimeframeError(range_str, interval, list(SUPPORTED_CHART_RANGES), list(SUPPORTED_CHART_INTERVALS))

        allowed = ALLOWED_INTERVALS_BY_RANGE.get(range_str, set())
        if interval not in allowed:
            raise InvalidTimeframeError(range_str, interval, list(SUPPORTED_CHART_RANGES), list(allowed))

        ticker = self._get_ticker_symbol(symbol, exchange)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

        y_range = _YAHOO_RANGE_MAP.get(range_str, "1mo")
        y_interval = _YAHOO_INTERVAL_MAP.get(interval, "1d")

        data = await self._execute_http(url, params={"range": y_range, "interval": y_interval})

        chart = data.get("chart", {})
        result_list = chart.get("result", [])
        if not result_list:
            raise StockNotFoundError(symbol=symbol, exchange=exchange)

        res = result_list[0]
        meta = res.get("meta", {})
        timestamps = res.get("timestamp", [])
        quote_indicators = res.get("indicators", {}).get("quote", [{}])[0]

        opens = quote_indicators.get("open", [])
        highs = quote_indicators.get("high", [])
        lows = quote_indicators.get("low", [])
        closes = quote_indicators.get("close", [])
        volumes = quote_indicators.get("volume", [])

        candles = []
        for i, ts in enumerate(timestamps):
            if i >= len(closes):
                break
            c_val = closes[i]
            # Skip invalid or empty candles
            if c_val is None:
                continue

            o_val = opens[i] if i < len(opens) and opens[i] is not None else c_val
            h_val = highs[i] if i < len(highs) and highs[i] is not None else max(o_val, c_val)
            l_val = lows[i] if i < len(lows) and lows[i] is not None else min(o_val, c_val)
            v_val = volumes[i] if i < len(volumes) and volumes[i] is not None else 0

            candle_time = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            candles.append({
                "timestamp": candle_time,
                "open": round(float(o_val), 2),
                "high": round(float(h_val), 2),
                "low": round(float(l_val), 2),
                "close": round(float(c_val), 2),
                "volume": int(v_val),
            })

        now_ts = datetime.now(timezone.utc).isoformat()
        exch_name = "NSE" if ticker.endswith(".NS") else "BSE" if ticker.endswith(".BO") else exchange or "NSE"

        return {
            "symbol": self._strip_ticker_suffix(symbol),
            "exchange": exch_name,
            "currency": meta.get("currency", "INR"),
            "range": range_str,
            "interval": interval,
            "data_status": DataFreshness.HISTORICAL.value if range_str != "1D" else DataFreshness.DELAYED.value,
            "source_name": self.provider_name,
            "fetched_at": now_ts,
            "candles": candles,
        }

    async def get_market_status(
        self,
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        try:
            tz = zoneinfo.ZoneInfo(MARKET_TIMEZONE)
        except Exception:
            tz = timezone(timedelta(hours=5, minutes=30))

        now_ist = datetime.now(tz)
        weekday = now_ist.weekday()

        is_trading_day = weekday < 5
        curr_minutes = now_ist.hour * 60 + now_ist.minute
        open_minutes = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE
        close_minutes = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MINUTE

        is_open = is_trading_day and (open_minutes <= curr_minutes <= close_minutes)

        return {
            "exchange": exchange or "NSE",
            "status": "OPEN" if is_open else "CLOSED",
            "current_time": datetime.now(timezone.utc).isoformat(),
            "session": "Regular Trading" if is_open else "Closed",
            "market_timezone": MARKET_TIMEZONE,
        }

    async def get_company_profile(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        # Fetch quote to get base details
        quote = await self.get_quote(symbol, exchange)
        clean_sym = self._strip_ticker_suffix(symbol)

        return {
            "symbol": clean_sym,
            "company_name": quote["company_name"],
            "exchange": quote["exchange"],
            "sector": "Indian Equities",
            "industry": "Public Listed Entity",
            "description": f"{quote['company_name']} is an active equity listed on {quote['exchange']}.",
            "website": f"https://www.nseindia.com/get-quotes/equity?symbol={clean_sym}",
            "market_cap": quote["market_cap"],
            "pe_ratio": None,
            "high_52w": quote["day_high"],
            "low_52w": quote["day_low"],
            "currency": quote["currency"],
            "data_status": DataFreshness.DELAYED.value,
            "source_name": self.provider_name,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_market_indices(self) -> List[Dict[str, Any]]:
        # Fetch key Indian benchmark indices
        indices = [
            {"symbol": "^NSEI", "name": "NIFTY 50"},
            {"symbol": "^BSESN", "name": "SENSEX"},
            {"symbol": "^NSEBANK", "name": "BANK NIFTY"},
            {"symbol": "^INDIAVIX", "name": "INDIA VIX"},
        ]

        results = []
        now_ts = datetime.now(timezone.utc).isoformat()

        for idx in indices:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{idx['symbol']}"
                data = await self._execute_http(url, params={"range": "1d", "interval": "1d"})
                meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                prev = meta.get("chartPreviousClose")
                change = round(price - prev, 2) if price and prev else None
                pct = round((change / prev) * 100, 2) if change and prev else None

                results.append({
                    "symbol": idx["symbol"],
                    "name": idx["name"],
                    "value": price,
                    "change": change,
                    "percent_change": pct,
                    "data_status": DataFreshness.DELAYED.value,
                    "timestamp": now_ts,
                })
            except Exception as e:
                logger.warning(f"Failed to fetch index {idx['symbol']}: {e}")
                results.append({
                    "symbol": idx["symbol"],
                    "name": idx["name"],
                    "value": None,
                    "change": None,
                    "percent_change": None,
                    "data_status": DataFreshness.UNAVAILABLE.value,
                    "timestamp": now_ts,
                })

        return results

    async def check_health(self) -> bool:
        try:
            res = await self.search_stocks("TCS", "NSE")
            return len(res) > 0
        except Exception:
            return False
