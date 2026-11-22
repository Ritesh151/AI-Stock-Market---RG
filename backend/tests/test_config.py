"""
Unit tests for Settings and Environment Configuration.
"""

import pytest
from app.core.config import Settings


def test_default_settings():
    """
    Verify default development settings.
    """
    settings = Settings(APP_ENV="development")
    assert settings.APP_NAME == "RG AI"
    assert settings.APP_PORT == 8000
    assert settings.is_development is True
    assert settings.is_production is False
    assert settings.is_test is False


def test_cors_origins_parsing():
    """
    Verify parsing of comma-separated string origins into a clean list.
    """
    settings = Settings(
        CORS_ORIGINS="http://localhost:3000, https://app.example.com "
    )
    assert settings.CORS_ORIGINS == [
        "http://localhost:3000",
        "https://app.example.com",
    ]


def test_production_rejects_wildcard_cors():
    """
    Verify production mode rejects wildcard '*' CORS origin.
    """
    with pytest.raises(ValueError, match="Wildcard '\\*' CORS origins are forbidden"):
        Settings(
            APP_ENV="production",
            CORS_ORIGINS="*",
            MONGODB_URI="mongodb://localhost:27017",
        )


def test_production_requires_mongodb_uri():
    """
    Verify production mode requires MONGODB_URI.
    """
    with pytest.raises(ValueError, match="MONGODB_URI must be configured"):
        Settings(
            APP_ENV="production",
            CORS_ORIGINS="https://rgai.example.com",
            MONGODB_URI="",
        )


def test_production_valid_configuration():
    """
    Verify a valid production configuration passes validation.
    """
    settings = Settings(
        APP_ENV="production",
        CORS_ORIGINS="https://rgai.example.com",
        MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/rg_ai",
    )
    assert settings.is_production is True
    assert settings.CORS_ORIGINS == ["https://rgai.example.com"]
