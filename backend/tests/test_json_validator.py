"""
Unit Tests for JSON Schema Validator and Financial Consistency Rules.
Covers strict field validation, type safety, enum restrictions, null preservation, and consistency warnings.
"""

import pytest
from app.services.json_validator import JsonValidator


@pytest.fixture
def validator():
    return JsonValidator()


def test_validate_valid_stock_analysis(validator):
    valid_payload = {
        "stock_name": "Tata Consultancy Services",
        "symbol": "TCS",
        "exchange": "NSE",
        "currency": "INR",
        "current_price": 4250.0,
        "price_change": 35.5,
        "price_change_percent": 0.84,
        "market_trend": "bullish",
        "recommendation": "BUY",
        "entry_zone": {"min": 4200.0, "max": 4260.0},
        "target_price": 4500.0,
        "stop_loss": 4120.0,
        "risk_level": "medium",
        "time_horizon": "1-3 months",
        "reasoning": ["Consolidating above 50-DMA", "Strong institutional cash flow"],
        "technical_analysis": {"rsi": 58.5},
        "fundamental_analysis": {"pe_ratio": 31.2},
        "data_timestamp": "2026-11-17T06:00:00Z",
        "data_source": "NSE",
    }
    result = validator.validate(valid_payload, expected_type="stock_analysis")
    assert result.is_valid is True
    assert result.schema_type == "stock_analysis"
    assert result.validated_data["symbol"] == "TCS"
    assert result.validated_data["recommendation"] == "BUY"
    assert len(result.warnings) == 0


def test_validate_missing_required_fields(validator):
    missing_symbol = {
        "stock_name": "TCS",
        "exchange": "NSE",
    }
    result = validator.validate(missing_symbol, expected_type="stock_analysis")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"
    issues = [d.field for d in result.error.details]
    assert "symbol" in issues


def test_validate_invalid_exchange_enum(validator):
    invalid_exchange = {
        "stock_name": "Apple Inc",
        "symbol": "AAPL",
        "exchange": "NASDAQ",  # RG AI strictly requires Indian exchanges (NSE, BSE, MCX)
    }
    result = validator.validate(invalid_exchange, expected_type="stock_analysis")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"


def test_validate_invalid_recommendation_enum(validator):
    invalid_rec = {
        "stock_name": "Infosys",
        "symbol": "INFY",
        "recommendation": "MAYBE_BUY",
    }
    result = validator.validate(invalid_rec, expected_type="stock_analysis")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"


def test_validate_negative_price_rejection(validator):
    neg_price = {
        "stock_name": "State Bank of India",
        "symbol": "SBIN",
        "current_price": -820.0,
    }
    result = validator.validate(neg_price, expected_type="stock_analysis")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"


def test_validate_entry_zone_min_exceeds_max(validator):
    inverted_entry = {
        "stock_name": "State Bank of India",
        "symbol": "SBIN",
        "entry_zone": {"min": 850.0, "max": 800.0},
    }
    result = validator.validate(inverted_entry, expected_type="stock_analysis")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED" or result.error.code == "INVALID_ENTRY_ZONE"


def test_validate_null_preservation(validator):
    # Null values must be preserved and never converted to 0
    null_payload = {
        "stock_name": "Zomato",
        "symbol": "ZOMATO",
        "current_price": None,
        "target_price": None,
        "stop_loss": None,
        "price_change": None,
        "technical_analysis": None,
    }
    result = validator.validate(null_payload, expected_type="stock_analysis")
    assert result.is_valid is True
    assert result.validated_data["current_price"] is None
    assert result.validated_data["target_price"] is None
    assert result.validated_data["technical_analysis"] is None


def test_validate_technical_analysis_rsi_bounds(validator):
    invalid_rsi = {
        "rsi": 105.0,  # Max 100
    }
    result = validator.validate(invalid_rsi, expected_type="technical_analysis")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"


def test_validate_fundamental_analysis_non_negative_cap(validator):
    invalid_cap = {
        "market_capitalization": -5000.0,
    }
    result = validator.validate(invalid_cap, expected_type="fundamental_analysis")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"


def test_validate_stock_comparison_distinct_symbols(validator):
    same_symbols = {
        "stocks_compared": ["TCS", "TCS"],
    }
    result = validator.validate(same_symbols, expected_type="stock_comparison")
    assert result.is_valid is False
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"


def test_validate_financial_consistency_warnings(validator):
    inconsistent_payload = {
        "stock_name": "Bajaj Auto",
        "symbol": "BAJAJ-AUTO",
        "current_price": 9500.0,
        "recommendation": "BUY",
        "target_price": 9000.0,  # BUY recommendation but target < current price!
        "stop_loss": 9700.0,     # BUY recommendation but stop_loss > current price!
    }
    result = validator.validate(inconsistent_payload, expected_type="stock_analysis")
    assert result.is_valid is True  # Context-dependent: does not fail schema, but emits warnings
    assert len(result.warnings) >= 2
    assert any("target price" in w for w in result.warnings)
    assert any("stop loss" in w for w in result.warnings)
