"""
Unit and Integration Tests for Market Data Integration (Phase 7).
Tests provider abstraction, quote normalization, search, history, freshness, caching, and watchlist operations.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.integrations.market_data.exceptions import (
    StockNotFoundError,
    InvalidTimeframeError,
    RateLimitExceededError,
    ProviderUnavailableError,
)
from app.integrations.market_data.provider_config import DataFreshness
from app.integrations.market_data.providers.mock_provider import MockMarketDataProvider
from app.integrations.market_data.provider_manager import get_provider_manager
from app.services.market_data_service import MarketDataService


@pytest.fixture(autouse=True)
def setup_mock_provider():
    """Ensure tests run against MockMarketDataProvider deterministically."""
    mock_prov = MockMarketDataProvider()
    get_provider_manager().set_provider(mock_prov)
    yield mock_prov


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


# 1. Provider Interface & Configuration
@pytest.mark.asyncio
async def test_mock_provider_implements_interface(setup_mock_provider):
    prov = setup_mock_provider
    assert prov.provider_name == "RG AI Mock Market Data"
    healthy = await prov.check_health()
    assert healthy is True


# 2. Stock Search
@pytest.mark.asyncio
async def test_search_stocks_service(setup_mock_provider):
    service = MarketDataService(provider=setup_mock_provider)
    res = await service.search_stocks("TATA")
    assert res.success is True
    assert len(res.results) > 0
    symbols = [r.symbol for r in res.results]
    assert "TATAMOTORS" in symbols


# 3. Stock Search API Endpoint
def test_api_stock_search(client):
    resp = client.get("/api/v1/stocks/search?q=TCS")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["total"] >= 1
    assert data["results"][0]["symbol"] == "TCS"
    assert data["results"][0]["exchange"] == "NSE"


# 4. Stock Quote Normalization & Section 6 Schema
def test_api_stock_quote_valid(client):
    resp = client.get("/api/v1/stocks/RELIANCE/quote")
    assert resp.status_code == 200
    res = resp.json()
    assert res["success"] is True
    q = res["data"]
    assert q["symbol"] == "RELIANCE"
    assert q["exchange"] == "NSE"
    assert q["currency"] == "INR"
    assert q["last_price"] == 2740.10
    assert q["previous_close"] == 2687.70
    assert q["change"] == 52.40
    assert q["change_percent"] == 1.95
    assert q["data_status"] == DataFreshness.DELAYED.value
    assert q["source_name"] == "RG AI Mock Market Data"
    assert q["market_timestamp"] is not None
    assert q["fetched_at"] is not None


# 5. Invalid Symbol Error Handling (404)
def test_api_stock_quote_not_found(client):
    resp = client.get("/api/v1/stocks/NONEXISTENT_XYZ/quote")
    assert resp.status_code == 404
    err = resp.json()["error"]
    assert err["code"] == "STOCK_NOT_FOUND"


# 6. Historical Data Endpoint & Candlestick Normalization
def test_api_stock_history_valid(client):
    resp = client.get("/api/v1/stocks/INFY/history?range=1M&interval=1d")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["symbol"] == "INFY"
    assert data["range"] == "1M"
    assert data["interval"] == "1d"
    assert len(data["candles"]) > 0
    candle = data["candles"][0]
    assert "timestamp" in candle
    assert candle["open"] > 0
    assert candle["high"] >= candle["low"]
    assert candle["close"] > 0
    assert "volume" in candle


# 7. Invalid Range or Interval Timeframe Rejection
def test_api_stock_history_invalid_timeframe(client):
    resp = client.get("/api/v1/stocks/INFY/history?range=INVALID_RANGE")
    assert resp.status_code == 400
    err = resp.json()["error"]
    assert err["code"] == "INVALID_TIMEFRAME"


def test_api_stock_history_unsupported_interval_for_range(client):
    # 1D range does not support 1wk interval
    resp = client.get("/api/v1/stocks/INFY/history?range=1D&interval=1wk")
    assert resp.status_code == 400
    err = resp.json()["error"]
    assert err["code"] == "INVALID_TIMEFRAME"


# 8. Company Profile Endpoint
def test_api_company_profile_valid(client):
    resp = client.get("/api/v1/stocks/HDFCBANK/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    p = data["data"]
    assert p["symbol"] == "HDFCBANK"
    assert p["sector"] == "Financial Services"
    assert p["currency"] == "INR"
    assert p["market_cap"] > 0
    assert p["pe_ratio"] == 18.9


# 9. Market Status Endpoint
def test_api_market_status(client):
    resp = client.get("/api/v1/market/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["exchange"] == "NSE"
    assert data["status"] in {"OPEN", "CLOSED"}
    assert data["market_timezone"] == "Asia/Kolkata"


# 10. Market Indices Endpoint
def test_api_market_indices(client):
    resp = client.get("/api/v1/market/indices")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["indices"]) == 4
    symbols = [idx["symbol"] for idx in data["indices"]]
    assert "^NSEI" in symbols
    assert "^BSESN" in symbols
    assert "^NSEBANK" in symbols
    assert "^INDIAVIX" in symbols


# 11. Watchlist Operations (List, Add, Prevent Duplicate, Remove)
def test_api_watchlist_lifecycle(client):
    # 1. Get initial watchlist
    r1 = client.get("/api/v1/stocks/watchlist")
    assert r1.status_code == 200
    init_total = r1.json()["total"]

    # 2. Add TATAMOTORS to watchlist
    r2 = client.post("/api/v1/stocks/watchlist/TATAMOTORS?exchange=NSE")
    assert r2.status_code == 201
    items = r2.json()["items"]
    symbols = [i["symbol"] for i in items]
    assert "TATAMOTORS" in symbols

    # 3. Add duplicate (should not duplicate)
    r3 = client.post("/api/v1/stocks/watchlist/TATAMOTORS")
    assert r3.status_code == 201
    assert r3.json()["total"] == len(symbols)

    # 4. Remove TATAMOTORS
    r4 = client.delete("/api/v1/stocks/watchlist/TATAMOTORS")
    assert r4.status_code == 200
    rem_symbols = [i["symbol"] for i in r4.json()["items"]]
    assert "TATAMOTORS" not in rem_symbols


# 12. Watchlist Sorting and Search
def test_api_watchlist_search_and_sorting(client):
    # Search by query
    r_search = client.get("/api/v1/stocks/watchlist?q=TCS")
    assert r_search.status_code == 200
    assert r_search.json()["total"] == 1
    assert r_search.json()["items"][0]["symbol"] == "TCS"

    # Sort by name
    r_sort = client.get("/api/v1/stocks/watchlist?sort_by=name")
    assert r_sort.status_code == 200
    names = [i["company_name"] for i in r_sort.json()["items"]]
    assert names == sorted(names, key=str.lower)


# 13. Cache Deduplication and TTL
@pytest.mark.asyncio
async def test_market_data_cache_deduplication(setup_mock_provider):
    service = MarketDataService(provider=setup_mock_provider)
    # First fetch (populates cache)
    q1 = await service.get_quote("TCS")
    # Second fetch (serves from cache)
    q2 = await service.get_quote("TCS")
    assert q1.data.fetched_at == q2.data.fetched_at
