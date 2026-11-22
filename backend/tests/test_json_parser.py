"""
Unit and Integration Tests for RG AI Robust JSON Parser.
Covers raw JSON, Markdown code fences, conversational boundaries, size limits, and multi-object rejection.
"""

import pytest
from app.services.json_parser import JsonParseError, JsonParser


@pytest.fixture
def parser():
    return JsonParser(max_size=1024 * 50, max_depth=5)


def test_parse_valid_raw_json(parser):
    raw = '{"stock_name": "Tata Motors", "symbol": "TATAMOTORS", "current_price": 945.50}'
    result = parser.parse(raw)
    assert result["stock_name"] == "Tata Motors"
    assert result["symbol"] == "TATAMOTORS"
    assert result["current_price"] == 945.50


def test_parse_markdown_code_fenced_json(parser):
    raw = """
Here is the requested stock data:
```json
{
  "stock_name": "Reliance Industries",
  "symbol": "RELIANCE",
  "exchange": "NSE"
}
```
Let me know if you need further details.
"""
    result = parser.parse(raw)
    assert result["stock_name"] == "Reliance Industries"
    assert result["symbol"] == "RELIANCE"
    assert result["exchange"] == "NSE"


def test_parse_generic_code_fence(parser):
    raw = """```
{"symbol": "INFY", "recommendation": "BUY"}
```"""
    result = parser.parse(raw)
    assert result["symbol"] == "INFY"
    assert result["recommendation"] == "BUY"


def test_parse_conversational_wrapper_without_fences(parser):
    raw = 'Certainly! Based on latest NSE session data, {"symbol": "HDFCBANK", "current_price": 1720.0}. Please review.'
    result = parser.parse(raw)
    assert result["symbol"] == "HDFCBANK"
    assert result["current_price"] == 1720.0


def test_parse_empty_and_whitespace_rejection(parser):
    with pytest.raises(JsonParseError) as exc:
        parser.parse("   ")
    assert exc.value.code == "EMPTY_RESPONSE"


def test_parse_invalid_json_rejection(parser):
    with pytest.raises(JsonParseError) as exc:
        parser.parse("{ invalid json string }")
    assert exc.value.code == "INVALID_JSON"


def test_parse_truncated_json_rejection(parser):
    with pytest.raises(JsonParseError) as exc:
        parser.parse('{"symbol": "TCS", "price": 4200.0')
    assert exc.value.code == "TRUNCATED_JSON"


def test_parse_multiple_ambiguous_objects_rejection(parser):
    raw = 'First object: {"stock": "TCS"}. Second object: {"stock": "INFY"}.'
    with pytest.raises(JsonParseError) as exc:
        parser.parse(raw)
    assert exc.value.code == "AMBIGUOUS_MULTIPLE_OBJECTS"


def test_parse_multiple_code_blocks_rejection(parser):
    raw = """
```json
{"symbol": "TCS"}
```
And also:
```json
{"symbol": "INFY"}
```
"""
    with pytest.raises(JsonParseError) as exc:
        parser.parse(raw)
    assert exc.value.code == "AMBIGUOUS_JSON_BLOCKS"


def test_parse_payload_size_limit():
    tiny_parser = JsonParser(max_size=50)
    huge_text = '{"stock_name": "' + ("A" * 100) + '"}'
    with pytest.raises(JsonParseError) as exc:
        tiny_parser.parse(huge_text)
    assert exc.value.code == "PAYLOAD_TOO_LARGE"


def test_parse_nesting_depth_limit():
    shallow_parser = JsonParser(max_depth=3)
    deep_json = '{"a": {"b": {"c": {"d": "too deep"}}}}'
    with pytest.raises(JsonParseError) as exc:
        shallow_parser.parse(deep_json)
    assert exc.value.code == "EXCESSIVE_NESTING_DEPTH"
