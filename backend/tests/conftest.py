"""
Pytest Fixtures and Test Client Configuration.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """
    Provides isolated test settings.
    """
    return Settings(
        APP_NAME="RG AI",
        APP_ENV="test",
        APP_HOST="127.0.0.1",
        APP_PORT=8000,
        CORS_ORIGINS=["http://localhost:3000", "http://testserver"],
        MONGODB_URI="",
        MONGODB_DATABASE="rg_ai_test",
        LOG_LEVEL="ERROR",
    )


@pytest.fixture
def app(test_settings: Settings):
    """
    Creates an application instance configured for tests.
    """
    application = create_app(settings=test_settings)
    application.dependency_overrides[get_settings] = lambda: test_settings
    return application


@pytest.fixture
def client(app) -> TestClient:
    """
    Provides a synchronous TestClient for testing HTTP endpoints.
    """
    with TestClient(app) as test_client:
        yield test_client
