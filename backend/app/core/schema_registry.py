"""
Schema Registry for RG AI Strict JSON Engine.
Maps response type identifiers to Pydantic models and provides JSON schema introspection.
"""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from app.schemas.educational_content import EducationalContentSchema
from app.schemas.fundamental_analysis import FundamentalAnalysisSchema
from app.schemas.market_overview import MarketOverviewSchema
from app.schemas.portfolio_analysis import PortfolioAnalysisSchema
from app.schemas.response_envelope import SupportedResponseType
from app.schemas.stock_analysis import StockAnalysisSchema
from app.schemas.stock_comparison import StockComparisonSchema
from app.schemas.technical_analysis import TechnicalAnalysisSchema
from app.core.logging import get_logger

logger = get_logger("core.schema_registry")


class SchemaRegistry:
    """Registry maintaining authoritative Pydantic models for all supported response types."""

    def __init__(self) -> None:
        self._schemas: Dict[str, Type[BaseModel]] = {}
        self._register_default_schemas()

    def _register_default_schemas(self) -> None:
        """Populates registry with the 7 core RG AI response models."""
        self.register(SupportedResponseType.STOCK_ANALYSIS.value, StockAnalysisSchema)
        self.register(SupportedResponseType.TECHNICAL_ANALYSIS.value, TechnicalAnalysisSchema)
        self.register(SupportedResponseType.FUNDAMENTAL_ANALYSIS.value, FundamentalAnalysisSchema)
        self.register(SupportedResponseType.PORTFOLIO_ANALYSIS.value, PortfolioAnalysisSchema)
        self.register(SupportedResponseType.STOCK_COMPARISON.value, StockComparisonSchema)
        self.register(SupportedResponseType.MARKED_OVERVIEW.value, MarketOverviewSchema)
        self.register(SupportedResponseType.EDUCATIONAL_CONTENT.value, EducationalContentSchema)

    def register(self, type_name: str, model_cls: Type[BaseModel]) -> None:
        """Registers a response type identifier with its corresponding Pydantic class."""
        self._schemas[type_name] = model_cls
        logger.debug(f"Registered schema for type '{type_name}' -> {model_cls.__name__}")

    def get_schema(self, type_name: str) -> Optional[Type[BaseModel]]:
        """Retrieves Pydantic model class for given type identifier."""
        return self._schemas.get(type_name)

    def list_supported_types(self) -> List[str]:
        """Returns list of all currently supported response type strings."""
        return list(self._schemas.keys())

    def get_json_schema(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Generates standard JSON Schema specification for introspection API."""
        model_cls = self.get_schema(type_name)
        if model_cls:
            return model_cls.model_json_schema()
        return None

    def detect_type(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Infers response type based on signature fields present in the dictionary.
        Returns None if ambiguous.
        """
        if not isinstance(data, dict):
            return None

        # Check explicit type tag if present
        if "type" in data and isinstance(data["type"], str) and data["type"] in self._schemas:
            return data["type"]

        # Signature heuristics
        if "stocks_compared" in data:
            return SupportedResponseType.STOCK_COMPARISON.value
        if "holdings" in data or "portfolio_value" in data:
            return SupportedResponseType.PORTFOLIO_ANALYSIS.value
        if "nifty_50" in data or "bank_nifty" in data:
            return SupportedResponseType.MARKED_OVERVIEW.value
        if "topic" in data and "category" in data and "key_concepts" in data:
            return SupportedResponseType.EDUCATIONAL_CONTENT.value
        if "stock_name" in data and "symbol" in data:
            return SupportedResponseType.STOCK_ANALYSIS.value
        if "rsi" in data or "moving_averages" in data or "support_levels" in data:
            return SupportedResponseType.TECHNICAL_ANALYSIS.value
        if "pe_ratio" in data or "market_capitalization" in data or "net_profit" in data:
            return SupportedResponseType.FUNDAMENTAL_ANALYSIS.value

        return None


_schema_registry_instance: Optional[SchemaRegistry] = None


def get_schema_registry() -> SchemaRegistry:
    """Returns singleton instance of SchemaRegistry."""
    global _schema_registry_instance
    if _schema_registry_instance is None:
        _schema_registry_instance = SchemaRegistry()
    return _schema_registry_instance
