"""
Integration Tests for Response Processor, Validation API Endpoints, and Phase 4 RequestManager Integration.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from app.integrations.rg_ai.automation_service import AutomationService
from app.integrations.rg_ai.gpt_adapter import MockGPTAdapter
from app.integrations.rg_ai.prompt_manager import PreparedPrompt
from app.main import create_app
from app.schemas.rg_ai import RequestStatus
from app.services.request_manager import RequestManager
from app.services.response_processor import ResponseProcessor, get_response_processor


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture
def processor():
    return get_response_processor()


def test_process_markdown_fenced_stock_analysis(processor):
    raw_markdown = """
Here is the requested stock analysis:
```json
{
  "stock_name": "Tata Motors",
  "symbol": "TATAMOTORS",
  "exchange": "NSE",
  "currency": "INR",
  "current_price": 945.0,
  "market_trend": "bullish",
  "recommendation": "BUY",
  "target_price": 1050.0,
  "stop_loss": 910.0
}
```
"""
    result = processor.process(raw_markdown, request_id="req_proc_1")
    assert result.success is True
    assert result.type == "stock_analysis"
    assert result.data["symbol"] == "TATAMOTORS"
    assert result.data["target_price"] == 1050.0


def test_process_invalid_json_returns_error_envelope(processor):
    bad_json = "```json { this is clearly not json } ```"
    result = processor.process(bad_json, request_id="req_proc_2")
    assert result.success is False
    assert result.type == "validation_error"
    assert result.error.code == "INVALID_JSON"


def test_process_schema_mismatch_returns_error_envelope(processor):
    # Valid JSON but missing required fields for stock_analysis
    incomplete_json = '{"some_unrelated_key": 123}'
    result = processor.process(incomplete_json, request_id="req_proc_3", expected_type="stock_analysis")
    assert result.success is False
    assert result.type == "validation_error"
    assert result.error.code == "SCHEMA_VALIDATION_FAILED"


def test_api_validate_response_endpoint(client):
    payload = {
        "raw_response": '{"topic": "Price Action", "category": "Technical", "summary": "Study of raw price movement."}',
        "request_id": "req_api_val",
        "expected_type": "educational_content",
    }
    res = client.post("/api/v1/rg-ai/validate-response", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["type"] == "educational_content"
    assert data["data"]["topic"] == "Price Action"


def test_api_normalize_response_endpoint(client):
    payload = {
        "raw_response": {
            "stock_name": "Reliance",
            "symbol": "RELIANCE",
            "current_price": 2750.0,
        },
        "request_id": "req_api_norm",
        "expected_type": "stock_analysis",
    }
    res = client.post("/api/v1/rg-ai/normalize-response", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["type"] == "stock_analysis"
    assert data["data"]["symbol"] == "RELIANCE"


def test_api_schemas_list_and_spec(client):
    res_list = client.get("/api/v1/rg-ai/schemas")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert "stock_analysis" in list_data["supported_types"]
    assert "technical_analysis" in list_data["supported_types"]
    assert list_data["count"] >= 7

    res_spec = client.get("/api/v1/rg-ai/schemas/stock_analysis")
    assert res_spec.status_code == 200
    spec_data = res_spec.json()
    assert spec_data["title"] == "StockAnalysisSchema"
    assert "properties" in spec_data


def test_api_schemas_spec_not_found(client):
    res = client.get("/api/v1/rg-ai/schemas/nonexistent_schema")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_phase4_integration_with_valid_json_response():
    valid_json_response = """```json
{
  "stock_name": "Infosys",
  "symbol": "INFY",
  "exchange": "NSE",
  "currency": "INR",
  "current_price": 1820.0,
  "market_trend": "neutral",
  "recommendation": "HOLD",
  "target_price": 1950.0,
  "stop_loss": 1750.0
}
```"""
    mock_adapter = MockGPTAdapter(simulated_delay=0.02, default_response=valid_json_response)
    automation_svc = AutomationService(adapter=mock_adapter)
    manager = RequestManager(
        queue_size=5,
        request_timeout_seconds=2,
        concurrency=1,
        automation_service=automation_svc,
    )

    await manager.start()
    try:
        prompt = PreparedPrompt(
            original_prompt="Analyze Infosys",
            cleaned_prompt="Analyze Infosys",
            template_version="v1",
            metadata={"expected_schema_type": "stock_analysis"},
        )
        record = await manager.create_request(prompt)

        for _ in range(40):
            if record.status in {RequestStatus.COMPLETED, RequestStatus.FAILED}:
                break
            await asyncio.sleep(0.05)

        assert record.status == RequestStatus.COMPLETED
        assert record.result is not None
        assert record.result["success"] is True
        assert record.result["type"] == "stock_analysis"
        assert record.result["data"]["symbol"] == "INFY"
    finally:
        await manager.shutdown()


@pytest.mark.asyncio
async def test_phase4_integration_rejects_invalid_json():
    # Adapter returns broken JSON
    invalid_json_response = "```json { broken: json without quotes or values "
    mock_adapter = MockGPTAdapter(simulated_delay=0.02, default_response=invalid_json_response)
    automation_svc = AutomationService(adapter=mock_adapter)
    manager = RequestManager(
        queue_size=5,
        request_timeout_seconds=2,
        concurrency=1,
        automation_service=automation_svc,
    )

    await manager.start()
    try:
        prompt = PreparedPrompt(
            original_prompt="Analyze broken response",
            cleaned_prompt="Analyze broken response",
            template_version="v1",
        )
        record = await manager.create_request(prompt)

        for _ in range(40):
            if record.status in {RequestStatus.COMPLETED, RequestStatus.FAILED}:
                break
            await asyncio.sleep(0.05)

        # Must fail and not claim completed
        assert record.status == RequestStatus.FAILED
        assert record.error is not None
        assert record.error["code"] == "TRUNCATED_JSON" or record.error["code"] == "INVALID_JSON"
    finally:
        await manager.shutdown()
