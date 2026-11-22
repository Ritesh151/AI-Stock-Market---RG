"""
Centralized Application Settings and Environment Management.
Uses Pydantic Settings for type validation and automatic .env parsing.
"""

from functools import lru_cache
from typing import List, Literal, Optional, Union
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Metadata
    APP_NAME: str = Field(default="RG AI", description="Name of the application")
    APP_ENV: Literal["development", "test", "staging", "production"] = Field(
        default="development", description="Application runtime environment"
    )
    APP_HOST: str = Field(default="127.0.0.1", description="Host address to bind to")
    APP_PORT: int = Field(default=8000, description="Port number to listen on")
    LOG_LEVEL: str = Field(default="INFO", description="Logging verbosity level")

    # Security & CORS
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default="http://localhost:3000",
        description="Allowed CORS origins (comma-separated or list)",
    )

    # Database Architecture (MongoDB Phase 10)
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI (local or MongoDB Atlas connection string)",
    )
    MONGODB_DATABASE: str = Field(
        default="rg_ai", description="Primary MongoDB database name"
    )
    MONGODB_MAX_POOL_SIZE: int = Field(
        default=50, description="Maximum MongoDB connection pool size"
    )
    MONGODB_MIN_POOL_SIZE: int = Field(
        default=5, description="Minimum MongoDB connection pool size"
    )
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = Field(
        default=3000, description="Server selection timeout in milliseconds"
    )
    MONGODB_CONNECT_TIMEOUT_MS: int = Field(
        default=3000, description="Socket connect timeout in milliseconds"
    )

    # Browser & Playwright Architecture (Phase 3)
    TARGET_GPT_URL: str = Field(
        default="https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market",
        description="Fixed centralized target Custom GPT URL",
    )
    CHROME_PROFILE_DIR: str = Field(
        default="data/chrome-profile",
        description="Path to persistent Chrome user-data profile directory",
    )
    CHROME_EXECUTABLE_PATH: Optional[str] = Field(
        default=None,
        description="Explicit Chrome/Chromium executable path (auto-detects if None)",
    )
    BROWSER_HEADLESS: bool = Field(
        default=False,
        description="Headless mode for managed browser (default headful for manual login)",
    )
    BROWSER_STARTUP_TIMEOUT_SECONDS: int = Field(
        default=30,
        description="Timeout for browser startup and initial page load in seconds",
    )

    # Market Data Integration (Phase 7)
    MARKET_DATA_PROVIDER: Literal["yahoo", "mock", "alphavantage"] = Field(
        default="yahoo",
        description="Active market data provider ('yahoo', 'mock', or 'alphavantage')",
    )
    MARKET_DATA_CACHE_TTL_SECONDS: int = Field(
        default=60,
        description="TTL for in-memory market data caching in seconds",
    )
    MARKET_DATA_REQUEST_TIMEOUT_SECONDS: int = Field(
        default=10,
        description="HTTP request timeout for market data provider calls in seconds",
    )
    MARKET_DATA_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum retry attempts for market data provider calls",
    )
    ALPHAVANTAGE_API_KEY: Optional[str] = Field(
        default=None,
        description="Optional API key for Alpha Vantage provider",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v.strip():
                return ["http://localhost:3000"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return ["http://localhost:3000"]

    @model_validator(mode="after")
    def validate_production_invariants(self) -> "Settings":
        """
        Enforce strict validation for production environments.
        """
        if self.APP_ENV == "production":
            # Wildcard CORS origins are forbidden in production
            if "*" in self.CORS_ORIGINS:
                raise ValueError("Wildcard '*' CORS origins are forbidden in production environment.")
            # Ensure MongoDB connection is defined when deploying to production
            if not self.MONGODB_URI or not self.MONGODB_URI.strip():
                raise ValueError("MONGODB_URI must be configured for production deployment.")
        return self

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_test(self) -> bool:
        return self.APP_ENV == "test"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached Settings instance.
    """
    return Settings()
