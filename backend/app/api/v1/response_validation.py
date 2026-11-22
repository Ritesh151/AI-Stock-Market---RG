"""
RG AI Response Validation and Normalization API Endpoints (API v1).
Provides validation, normalization, and JSON schema introspection endpoints.
"""

from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from app.api.v1.browser import verify_local_access_policy
from app.core.schema_registry import SchemaRegistry, get_schema_registry
from app.schemas.response_envelope import ResponseEnvelope, ValidationErrorEnvelope
from app.services.response_processor import ResponseProcessor, get_response_processor
from app.core.logging import get_logger

logger = get_logger("api.v1.response_validation")

router = APIRouter(prefix="/rg-ai", tags=["RG AI Response Validation"])


class RawResponsePayload(BaseModel):
    """Incoming request payload containing raw response string or structured dictionary."""

    raw_response: Union[str, Dict[str, Any]] = Field(
        ..., description="Raw unstructured text or JSON dictionary to parse and validate"
    )
    request_id: Optional[str] = Field(
        default="api_validation_req", description="Optional request tracking ID"
    )
    expected_type: Optional[str] = Field(
        default=None, description="Optional target schema type (auto-detects if None)"
    )


class SchemaListResponse(BaseModel):
    """Response model listing all registered schema types."""

    supported_types: List[str]
    count: int


@router.post(
    "/validate-response",
    summary="Validate raw integration response against strict schemas",
    dependencies=[Depends(verify_local_access_policy)],
)
async def validate_response(
    payload: RawResponsePayload,
    processor: ResponseProcessor = Depends(get_response_processor),
) -> Union[ResponseEnvelope, ValidationErrorEnvelope]:
    """
    Parses raw response content, validates against target Pydantic schema and financial consistency checks,
    and returns either a normalized ResponseEnvelope or a structured ValidationErrorEnvelope.
    """
    req_id = payload.request_id or "val_req"
    return processor.process(
        raw_content=payload.raw_response,
        request_id=req_id,
        expected_type=payload.expected_type,
    )


@router.post(
    "/normalize-response",
    summary="Validate and normalize payload into standard response envelope",
    dependencies=[Depends(verify_local_access_policy)],
)
async def normalize_response(
    payload: RawResponsePayload,
    processor: ResponseProcessor = Depends(get_response_processor),
) -> Union[ResponseEnvelope, ValidationErrorEnvelope]:
    """
    Normalizes a validated payload into canonical ResponseEnvelope format with ISO 8601 timestamps.
    """
    req_id = payload.request_id or "norm_req"
    return processor.process(
        raw_content=payload.raw_response,
        request_id=req_id,
        expected_type=payload.expected_type,
    )


@router.get(
    "/schemas",
    response_model=SchemaListResponse,
    summary="List all supported analysis schema types",
    dependencies=[Depends(verify_local_access_policy)],
)
async def list_schemas(
    registry: SchemaRegistry = Depends(get_schema_registry),
) -> SchemaListResponse:
    """Returns list of all registered response types supported by the JSON engine."""
    types = registry.list_supported_types()
    return SchemaListResponse(supported_types=types, count=len(types))


@router.get(
    "/schemas/{response_type}",
    summary="Get JSON Schema specification for a specific response type",
    dependencies=[Depends(verify_local_access_policy)],
)
async def get_schema_spec(
    response_type: str,
    registry: SchemaRegistry = Depends(get_schema_registry),
) -> Dict[str, Any]:
    """Returns standard JSON Schema definition for schema introspection and client validation."""
    schema = registry.get_json_schema(response_type)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema for type '{response_type}' not found.",
        )
    return schema
