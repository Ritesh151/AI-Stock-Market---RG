"""
Mock Market Data Provider.
Provides deterministic, fast, offline market data for unit testing and local development.
Never pretends to be live production data.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import zoneinfo

from app.integrations.market_data.base import MarketDataProvider
from app.integrations.market_data.exceptions import StockNotFoundError, InvalidTimeframeError
from app.integrations.market_data.provider_config import (
    DataFreshness,
    SUPPORTED_CHART_RANGES,
    SUPPORTED_CHART_INTERVALS,
    ALLOWED_INTERVALS_BY_RANGE,
    MARKET_TIMEZONE,
    MARKET_OPEN_HOUR,
    MARKET_OPEN_MINUTE,
    MARKET_CLOSE_HOUR,
    MARKET_CLOSE_MINUTE,
)

_MOCK_STOCKS = {
    "RELIANCE": {
        "company_name": "Reliance Industries Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 2740.10,
        "previous_close": 2687.70,
        "change": 52.40,
        "change_percent": 1.95,
        "open": 2705.00,
        "day_high": 2755.00,
        "day_low": 2698.00,
        "volume": 8420000,
        "market_cap": 18542000000000,
        "sector": "Energy & Retail",
        "industry": "Oil, Gas & Consumables",
        "description": "Reliance Industries Limited operates across hydrocarbons, retail, digital services, and green energy.",
        "pe_ratio": 26.8,
        "high_52w": 3024.90,
        "low_52w": 2220.30,
    },
    "TCS": {
        "company_name": "Tata Consultancy Services Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 4120.00,
        "previous_close": 4072.00,
        "change": 48.00,
        "change_percent": 1.18,
        "open": 4085.00,
        "day_high": 4145.00,
        "day_low": 4070.00,
        "volume": 3200000,
        "market_cap": 14900000000000,
        "sector": "Information Technology",
        "industry": "IT Services & Consulting",
        "description": "Tata Consultancy Services provides IT services, consulting, and business solutions worldwide.",
        "pe_ratio": 31.2,
        "high_52w": 4585.90,
        "low_52w": 3313.00,
    },
    "INFY": {
        "company_name": "Infosys Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 1892.30,
        "previous_close": 1839.90,
        "change": 52.40,
        "change_percent": 2.85,
        "open": 1850.00,
        "day_high": 1905.00,
        "day_low": 1845.00,
        "volume": 6800000,
        "market_cap": 7853000000000,
        "sector": "Information Technology",
        "industry": "IT Services & Consulting",
        "description": "Infosys is a global leader in next-generation digital services and consulting.",
        "pe_ratio": 29.4,
        "high_52w": 1975.00,
        "low_52w": 1358.35,
    },
    "HDFCBANK": {
        "company_name": "HDFC Bank Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 1642.00,
        "previous_close": 1666.10,
        "change": -24.10,
        "change_percent": -1.45,
        "open": 1660.00,
        "day_high": 1670.00,
        "day_low": 1635.00,
        "volume": 11100000,
        "market_cap": 12510000000000,
        "sector": "Financial Services",
        "industry": "Private Sector Bank",
        "description": "HDFC Bank provides a wide suite of banking and financial services across India.",
        "pe_ratio": 18.9,
        "high_52w": 1794.00,
        "low_52w": 1363.55,
    },
    "TATAMOTORS": {
        "company_name": "Tata Motors Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 984.50,
        "previous_close": 945.60,
        "change": 38.90,
        "change_percent": 4.12,
        "open": 955.00,
        "day_high": 995.00,
        "day_low": 950.00,
        "volume": 14200000,
        "market_cap": 3624000000000,
        "sector": "Automobile",
        "industry": "Passenger Cars & Commercial Vehicles",
        "description": "Tata Motors is a multinational automotive company and manufacturer of cars, trucks, and buses.",
        "pe_ratio": 16.2,
        "high_52w": 1179.00,
        "low_52w": 671.15,
    },
    "ICICIBANK": {
        "company_name": "ICICI Bank Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 1285.40,
        "previous_close": 1261.20,
        "change": 24.20,
        "change_percent": 1.92,
        "open": 1265.00,
        "day_high": 1290.00,
        "day_low": 1260.00,
        "volume": 9850000,
        "market_cap": 9045000000000,
        "sector": "Financial Services",
        "industry": "Private Sector Bank",
        "description": "ICICI Bank offers a wide range of banking products and financial services.",
        "pe_ratio": 18.2,
        "high_52w": 1330.00,
        "low_52w": 915.00,
    },
    "SBIN": {
        "company_name": "State Bank of India",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 815.60,
        "previous_close": 828.10,
        "change": -12.50,
        "change_percent": -1.51,
        "open": 825.00,
        "day_high": 830.00,
        "day_low": 810.00,
        "volume": 18500000,
        "market_cap": 7280000000000,
        "sector": "Financial Services",
        "industry": "Public Sector Bank",
        "description": "State Bank of India is a Fortune 500 public sector bank and financial services statutory body.",
        "pe_ratio": 11.5,
        "high_52w": 912.00,
        "low_52w": 555.00,
    },
    "BHARTIARTL": {
        "company_name": "Bharti Airtel Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 1640.80,
        "previous_close": 1595.00,
        "change": 45.80,
        "change_percent": 2.87,
        "open": 1600.00,
        "day_high": 1655.00,
        "day_low": 1590.00,
        "volume": 7200000,
        "market_cap": 9480000000000,
        "sector": "Telecommunication",
        "industry": "Telecom Services",
        "description": "Bharti Airtel is a leading telecommunications company with operations in Asia and Africa.",
        "pe_ratio": 42.1,
        "high_52w": 1720.00,
        "low_52w": 930.00,
    },
    "ITC": {
        "company_name": "ITC Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 472.30,
        "previous_close": 481.50,
        "change": -9.20,
        "change_percent": -1.91,
        "open": 480.00,
        "day_high": 483.00,
        "day_low": 470.00,
        "volume": 12400000,
        "market_cap": 5910000000000,
        "sector": "Fast Moving Consumer Goods",
        "industry": "Diversified FMCG",
        "description": "ITC is a diversified conglomerate with presence in FMCG, Hotels, Packaging, and Agri-Business.",
        "pe_ratio": 28.5,
        "high_52w": 528.00,
        "low_52w": 399.00,
    },
    "LT": {
        "company_name": "Larsen & Toubro Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 3610.00,
        "previous_close": 3695.00,
        "change": -85.00,
        "change_percent": -2.30,
        "open": 3680.00,
        "day_high": 3690.00,
        "day_low": 3590.00,
        "volume": 3100000,
        "market_cap": 4960000000000,
        "sector": "Construction & Engineering",
        "industry": "Heavy Civil Infrastructure",
        "description": "Larsen & Toubro is a multinational conglomerate engaged in EPC projects, manufacturing, and services.",
        "pe_ratio": 33.8,
        "high_52w": 3948.00,
        "low_52w": 2870.00,
    },
}

_MOCK_INDICES = {
    "^NSEI": {
        "name": "NIFTY 50",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 24850.30,
        "previous_close": 24708.20,
        "change": 142.10,
        "change_percent": 0.58,
        "open": 24750.00,
        "day_high": 24900.00,
        "day_low": 24720.00,
        "volume": 412000000,
    },
    "^BSESN": {
        "name": "SENSEX",
        "exchange": "BSE",
        "currency": "INR",
        "last_price": 81380.50,
        "previous_close": 80960.20,
        "change": 420.30,
        "change_percent": 0.52,
        "open": 81100.00,
        "day_high": 81500.00,
        "day_low": 81050.00,
        "volume": 25000000,
    },
    "^NSEBANK": {
        "name": "BANK NIFTY",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 52140.80,
        "previous_close": 52226.00,
        "change": -85.20,
        "change_percent": -0.16,
        "open": 52300.00,
        "day_high": 52450.00,
        "day_low": 52050.00,
        "volume": 120000000,
    },
    "^INDIAVIX": {
        "name": "INDIA VIX",
        "exchange": "NSE",
        "currency": "INR",
        "last_price": 12.85,
        "previous_close": 13.30,
        "change": -0.45,
        "change_percent": -3.38,
        "open": 13.20,
        "day_high": 13.50,
        "day_low": 12.60,
        "volume": 0,
    },
}


class MockMarketDataProvider(MarketDataProvider):
    """Deterministic mock provider implementation."""

    @property
    def provider_name(self) -> str:
        return "RG AI Mock Market Data"

    async def search_stocks(
        self,
        query: str,
        exchange: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        q = query.strip().upper()
        results = []
        for sym, d in _MOCK_STOCKS.items():
            if q in sym or q in d["company_name"].upper():
                results.append({
                    "symbol": sym,
                    "company_name": d["company_name"],
                    "exchange": d["exchange"],
                    "currency": d["currency"],
                    "type": "EQUITY",
                })
        return results

    async def get_quote(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        sym = symbol.strip().upper()
        if sym not in _MOCK_STOCKS:
            raise StockNotFoundError(symbol=sym, exchange=exchange)

        stock = _MOCK_STOCKS[sym]
        now = datetime.now(timezone.utc)

        return {
            "symbol": sym,
            "company_name": stock["company_name"],
            "exchange": stock["exchange"],
            "currency": stock["currency"],
            "last_price": stock["last_price"],
            "previous_close": stock["previous_close"],
            "change": stock["change"],
            "change_percent": stock["change_percent"],
            "open": stock["open"],
            "day_high": stock["day_high"],
            "day_low": stock["day_low"],
            "volume": stock["volume"],
            "market_cap": stock["market_cap"],
            "data_status": DataFreshness.DELAYED.value,
            "source_name": self.provider_name,
            "market_timestamp": now.isoformat(),
            "fetched_at": now.isoformat(),
        }

    async def get_historical_data(
        self,
        symbol: str,
        range_str: str = "1M",
        interval: str = "1d",
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        sym = symbol.strip().upper()
        if sym in _MOCK_STOCKS:
            stock = _MOCK_STOCKS[sym]
        elif sym in _MOCK_INDICES:
            stock = _MOCK_INDICES[sym]
        else:
            raise StockNotFoundError(symbol=sym, exchange=exchange)

        if range_str not in SUPPORTED_CHART_RANGES or interval not in SUPPORTED_CHART_INTERVALS:
            raise InvalidTimeframeError(range_str, interval)

        allowed = ALLOWED_INTERVALS_BY_RANGE.get(range_str, set())
        if interval not in allowed:
            raise InvalidTimeframeError(range_str, interval, list(SUPPORTED_CHART_RANGES), list(allowed))

        base_price = stock["last_price"]

        # Generate deterministic synthetic candles
        points_count = {
            "1D": 7,
            "5D": 10,
            "1M": 20,
            "3M": 30,
            "6M": 40,
            "1Y": 52,
            "5Y": 60,
        }.get(range_str, 20)

        now = datetime.now(timezone.utc)
        step_minutes = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "1d": 1440,
            "1wk": 10080,
        }.get(interval, 1440)

        candles = []
        for i in range(points_count):
            t = now - timedelta(minutes=(points_count - i) * step_minutes)
            # deterministic oscillation
            delta = ((i % 5) - 2) * (base_price * 0.005)
            open_p = round(base_price + delta, 2)
            high_p = round(open_p + (base_price * 0.008), 2)
            low_p = round(open_p - (base_price * 0.006), 2)
            close_p = round(open_p + (delta * 0.5), 2)
            vol = int(50000 + (i * 2000))

            candles.append({
                "timestamp": t.isoformat(),
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "close": close_p,
                "volume": vol,
            })

        return {
            "symbol": sym,
            "exchange": stock["exchange"],
            "currency": stock["currency"],
            "range": range_str,
            "interval": interval,
            "data_status": DataFreshness.HISTORICAL.value,
            "source_name": self.provider_name,
            "fetched_at": now.isoformat(),
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
        weekday = now_ist.weekday()  # 0 is Monday, 6 is Sunday

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
        sym = symbol.strip().upper()
        if sym not in _MOCK_STOCKS:
            raise StockNotFoundError(symbol=sym, exchange=exchange)

        s = _MOCK_STOCKS[sym]
        now = datetime.now(timezone.utc)

        return {
            "symbol": sym,
            "company_name": s["company_name"],
            "exchange": s["exchange"],
            "sector": s["sector"],
            "industry": s["industry"],
            "description": s["description"],
            "website": f"https://www.{sym.lower()}.com",
            "market_cap": s["market_cap"],
            "pe_ratio": s["pe_ratio"],
            "high_52w": s["high_52w"],
            "low_52w": s["low_52w"],
            "currency": s["currency"],
            "data_status": DataFreshness.DELAYED.value,
            "source_name": self.provider_name,
            "fetched_at": now.isoformat(),
        }

    async def get_market_indices(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        return [
            {
                "symbol": "^NSEI",
                "name": "NIFTY 50",
                "value": 24850.30,
                "change": 142.10,
                "percent_change": 0.58,
                "data_status": DataFreshness.DELAYED.value,
                "timestamp": now,
            },
            {
                "symbol": "^BSESN",
                "name": "SENSEX",
                "value": 81380.50,
                "change": 420.30,
                "percent_change": 0.52,
                "data_status": DataFreshness.DELAYED.value,
                "timestamp": now,
            },
            {
                "symbol": "^NSEBANK",
                "name": "BANK NIFTY",
                "value": 52140.80,
                "change": -85.20,
                "percent_change": -0.16,
                "data_status": DataFreshness.DELAYED.value,
                "timestamp": now,
            },
            {
                "symbol": "^INDIAVIX",
                "name": "INDIA VIX",
                "value": 12.85,
                "change": -0.45,
                "percent_change": -3.38,
                "data_status": DataFreshness.DELAYED.value,
                "timestamp": now,
            },
        ]

    async def check_health(self) -> bool:
        return True
