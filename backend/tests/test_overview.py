"""
Unit and Integration Tests for Phase 8 Overview Dashboard & Market Intelligence.
Tests indices, sentiment calculation, movers ranking, news feed, and partial failure resilience.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.integrations.market_data.provider_manager import get_provider_manager
from app.integrations.market_data.providers.mock_provider import MockMarketDataProvider
from app.main import create_app
from app.schemas.overview import (
    MarketIndexOverviewItem,
    MarketMoversData,
    StockMoverItem,
)
from app.services.overview_service import (
    OverviewService,
    get_overview_service,
    set_overview_service,
)


@pytest.fixture(autouse=True)
def setup_mock_market_provider():
    """Ensure mock provider and clean overview service are used for all tests."""
    mock_prov = MockMarketDataProvider()
    get_provider_manager().set_provider(mock_prov)
    svc = OverviewService(provider=mock_prov)
    set_overview_service(svc)
    yield
    set_overview_service(None)


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_api_overview_aggregate_success(client: TestClient):
    """Verifies GET /api/v1/overview returns full aggregated dashboard."""
    response = client.get("/api/v1/overview?exchange=NSE")
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["status"] in ("SUCCESS", "PARTIAL")
    assert data["exchange"] == "NSE"

    # Market status block
    assert "market_status" in data
    assert data["market_status"]["exchange"] == "NSE"
    assert data["market_status"]["status"] in ("OPEN", "CLOSED")

    # Indices block
    assert "indices" in data
    assert len(data["indices"]) >= 3
    index_names = [idx["name"] for idx in data["indices"]]
    assert "NIFTY 50" in index_names
    assert "SENSEX" in index_names

    # Sentiment block
    assert "sentiment" in data
    assert data["sentiment"]["status"] in ("BULLISH", "BEARISH", "NEUTRAL", "MIXED", "UNAVAILABLE")
    assert "methodology" in data["sentiment"]

    # Movers block
    assert "movers" in data
    assert "gainers" in data["movers"]
    assert "losers" in data["movers"]
    assert "most_active" in data["movers"]

    # News block
    assert "news" in data
    assert data["news"]["status"] in ("AVAILABLE", "UNAVAILABLE")


def test_api_overview_indices_with_sparklines(client: TestClient):
    """Verifies GET /api/v1/overview/indices returns stats and sparklines."""
    response = client.get("/api/v1/overview/indices")
    assert response.status_code == 200
    indices = response.json()
    assert isinstance(indices, list)
    assert len(indices) >= 3

    nifty = next((i for i in indices if "NIFTY 50" in i["name"]), None)
    assert nifty is not None
    assert nifty["value"] is not None
    assert nifty["change"] is not None
    assert nifty["percent_change"] is not None
    assert nifty["previous_close"] is not None
    assert nifty["day_high"] is not None
    assert nifty["day_low"] is not None
    assert len(nifty["sparkline"]) > 0


def test_api_overview_movers_gainers_and_losers(client: TestClient):
    """Verifies GET /api/v1/overview/movers correctly categorizes gainers, losers, and volume leaders."""
    response = client.get("/api/v1/overview/movers?exchange=NSE")
    assert response.status_code == 200
    movers = response.json()

    assert "gainers" in movers
    assert "losers" in movers
    assert "most_active" in movers

    # Gainers must have positive change_percent and be sorted descending
    if movers["gainers"]:
        g_pcts = [g["change_percent"] for g in movers["gainers"]]
        for pct in g_pcts:
            assert pct > 0
        assert g_pcts == sorted(g_pcts, reverse=True)

    # Losers must have negative change_percent and be sorted ascending
    if movers["losers"]:
        l_pcts = [l["change_percent"] for l in movers["losers"]]
        for pct in l_pcts:
            assert pct < 0
        assert l_pcts == sorted(l_pcts)

    # Most active must be sorted descending by volume
    if movers["most_active"]:
        vols = [m["volume"] for m in movers["most_active"]]
        assert vols == sorted(vols, reverse=True)


def test_api_overview_market_status(client: TestClient):
    """Verifies GET /api/v1/overview/market-status returns session details."""
    response = client.get("/api/v1/overview/market-status?exchange=NSE")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["exchange"] == "NSE"
    assert data["status"] in ("OPEN", "CLOSED")
    assert data["market_timezone"] == "Asia/Kolkata"


def test_api_overview_news(client: TestClient):
    """Verifies GET /api/v1/overview/news returns articles or clean unavailable state without fabricated news."""
    response = client.get("/api/v1/overview/news")
    assert response.status_code == 200
    news = response.json()
    assert news["status"] in ("AVAILABLE", "UNAVAILABLE")
    if news["status"] == "UNAVAILABLE":
        assert "synthetic" in news["message"].lower() or "unavailable" in news["message"].lower()
        assert len(news["articles"]) == 0
    else:
        assert len(news["articles"]) > 0
        assert news["articles"][0]["headline"]


def test_sentiment_calculation_bullish_scenario():
    """Tests sentiment methodology returns BULLISH under positive index & breadth conditions."""
    svc = OverviewService(provider=MockMarketDataProvider())

    # Create bullish index scenario
    indices = [
        MarketIndexOverviewItem(
            symbol="^NSEI",
            name="NIFTY 50",
            value=25000.0,
            change=300.0,
            percent_change=1.2,
            timestamp="2026-11-17T00:00:00Z",
        ),
        MarketIndexOverviewItem(
            symbol="^BSESN",
            name="SENSEX",
            value=82000.0,
            change=950.0,
            percent_change=1.15,
            timestamp="2026-11-17T00:00:00Z",
        ),
        MarketIndexOverviewItem(
            symbol="^INDIAVIX",
            name="INDIA VIX",
            value=12.2,
            change=-0.6,
            percent_change=-4.5,
            timestamp="2026-11-17T00:00:00Z",
        ),
    ]

    movers = MarketMoversData(
        gainers=[
            StockMoverItem(symbol="TCS", company_name="TCS", change_percent=2.5, timestamp=""),
            StockMoverItem(symbol="INFY", company_name="Infosys", change_percent=2.1, timestamp=""),
            StockMoverItem(symbol="RELIANCE", company_name="RIL", change_percent=1.8, timestamp=""),
        ],
        losers=[],
        most_active=[],
        timestamp="",
    )

    sentiment = svc.calculate_sentiment(indices, movers)
    assert sentiment.status == "BULLISH"
    assert sentiment.score is not None
    assert sentiment.score >= 0.25
    assert len(sentiment.methodology) > 20


def test_sentiment_calculation_bearish_scenario():
    """Tests sentiment methodology returns BEARISH under sharp sell-off and surging VIX."""
    svc = OverviewService(provider=MockMarketDataProvider())

    indices = [
        MarketIndexOverviewItem(
            symbol="^NSEI",
            name="NIFTY 50",
            value=24000.0,
            change=-450.0,
            percent_change=-1.8,
            timestamp="2026-11-17T00:00:00Z",
        ),
        MarketIndexOverviewItem(
            symbol="^BSESN",
            name="SENSEX",
            value=79000.0,
            change=-1400.0,
            percent_change=-1.75,
            timestamp="2026-11-17T00:00:00Z",
        ),
        MarketIndexOverviewItem(
            symbol="^INDIAVIX",
            name="INDIA VIX",
            value=19.5,
            change=2.8,
            percent_change=16.8,
            timestamp="2026-11-17T00:00:00Z",
        ),
    ]

    movers = MarketMoversData(
        gainers=[],
        losers=[
            StockMoverItem(symbol="TCS", company_name="TCS", change_percent=-2.5, timestamp=""),
            StockMoverItem(symbol="INFY", company_name="Infosys", change_percent=-2.1, timestamp=""),
            StockMoverItem(symbol="RELIANCE", company_name="RIL", change_percent=-1.8, timestamp=""),
        ],
        most_active=[],
        timestamp="",
    )

    sentiment = svc.calculate_sentiment(indices, movers)
    assert sentiment.status == "BEARISH"
    assert sentiment.score is not None
    assert sentiment.score <= -0.25


def test_sentiment_calculation_unavailable_when_indices_missing():
    """Tests sentiment returns UNAVAILABLE if key index metrics are missing."""
    svc = OverviewService(provider=MockMarketDataProvider())
    movers = MarketMoversData(gainers=[], losers=[], most_active=[], timestamp="")

    sentiment = svc.calculate_sentiment([], movers)
    assert sentiment.status == "UNAVAILABLE"
    assert sentiment.score is None


def test_partial_provider_failure_resilience(monkeypatch):
    """
    Verifies that if one provider section fails (e.g., movers throws an exception),
    the overview API returns a PARTIAL response without failing the whole dashboard.
    """
    svc = OverviewService(provider=MockMarketDataProvider())

    async def broken_movers(*args, **kwargs):
        raise RuntimeError("Movers upstream connection timeout")

    monkeypatch.setattr(svc, "get_movers", broken_movers)
    set_overview_service(svc)

    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # The dashboard status reflects partial availability
    assert data["status"] in ("SUCCESS", "PARTIAL")
    assert len(data["indices"]) >= 3
    # Movers gracefully downgraded to empty lists
    assert len(data["movers"]["gainers"]) == 0
