"""
Response Processor for RG AI.
End-to-end orchestration of JSON extraction, schema validation, financial sanity checks, and envelope normalization.
"""

from typing import Any, Dict, Optional, Tuple, Union
from app.core.exceptions import AppException
from app.schemas.response_envelope import ResponseEnvelope, ValidationErrorEnvelope
from app.services.json_parser import JsonParseError, JsonParser, get_json_parser
from app.services.json_validator import JsonValidator, ValidationResult, get_json_validator
from app.services.response_normalizer import ResponseNormalizer, get_response_normalizer
from app.core.logging import get_logger

logger = get_logger("services.response_processor")


class ResponseProcessingError(AppException):
    """Raised when processing or validation fails in strict mode."""

    def __init__(
        self,
        message: str,
        code: str = "VALIDATION_FAILED",
        status_code: int = 422,
        envelope: Optional[ValidationErrorEnvelope] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code)
        self.envelope = envelope


class ResponseProcessor:
    """Coordinates parsing, schema matching, validation checks, and envelope packaging."""

    def __init__(
        self,
        parser: Optional[JsonParser] = None,
        validator: Optional[JsonValidator] = None,
        normalizer: Optional[ResponseNormalizer] = None,
    ) -> None:
        self.parser = parser or get_json_parser()
        self.validator = validator or get_json_validator()
        self.normalizer = normalizer or get_response_normalizer()

    def process(
        self,
        raw_content: Union[str, Dict[str, Any]],
        request_id: str,
        expected_type: Optional[str] = None,
    ) -> Union[ResponseEnvelope, ValidationErrorEnvelope]:
        """
        Executes end-to-end processing pipeline on raw response content.
        Never raises exceptions; returns either ResponseEnvelope or ValidationErrorEnvelope.
        """
        # 1. Parse JSON content
        if isinstance(raw_content, str):
            try:
                parsed_data = self.parser.parse(raw_content)
            except JsonParseError as parse_err:
                logger.warning(f"Request {request_id}: JSON parse failure: {parse_err.message}")
                return self.normalizer.normalize_error(
                    code=parse_err.code,
                    message=parse_err.message,
                    request_id=request_id,
                )
            except Exception as exc:
                logger.error(f"Request {request_id}: Unexpected parse error: {exc}")
                return self.normalizer.normalize_error(
                    code="INVALID_JSON",
                    message="The response is not valid JSON.",
                    request_id=request_id,
                )
        elif isinstance(raw_content, dict):
            parsed_data = raw_content
        else:
            return self.normalizer.normalize_error(
                code="INVALID_DATA_TYPE",
                message="Expected string or dictionary response content.",
                request_id=request_id,
            )

        # 2. Validate against schema & financial rules
        validation_result: ValidationResult = self.validator.validate(
            data=parsed_data,
            expected_type=expected_type,
        )

        if not validation_result.is_valid:
            err = validation_result.error
            logger.warning(f"Request {request_id}: Schema validation failed: {err.message if err else 'Unknown'}")
            return self.normalizer.normalize_error(
                code=err.code if err else "SCHEMA_VALIDATION_FAILED",
                message=err.message if err else "The response does not match the expected schema.",
                request_id=request_id,
                details=err.details if err else None,
            )

        # 3. Construct canonical ResponseEnvelope
        envelope = self.normalizer.normalize_success(
            schema_type=validation_result.schema_type,
            validated_data=validation_result.validated_data or {},
            request_id=request_id,
            warnings=validation_result.warnings,
        )
        logger.info(f"Request {request_id}: Successfully processed {validation_result.schema_type} response.")
        return envelope

    def process_or_raise(
        self,
        raw_content: Union[str, Dict[str, Any]],
        request_id: str,
        expected_type: Optional[str] = None,
    ) -> ResponseEnvelope:
        """
        Processes content and raises ResponseProcessingError if validation fails.
        Useful for internal validation checkpoints (e.g. RequestManager pipeline).
        """
        result = self.process(raw_content=raw_content, request_id=request_id, expected_type=expected_type)
        if isinstance(result, ValidationErrorEnvelope):
            raise ResponseProcessingError(
                message=result.error.message,
                code=result.error.code,
                envelope=result,
            )
        return result


_response_processor_instance: Optional[ResponseProcessor] = None


def get_response_processor() -> ResponseProcessor:
    """Returns singleton instance of ResponseProcessor."""
    global _response_processor_instance
    if _response_processor_instance is None:
        _response_processor_instance = ResponseProcessor()
    return _response_processor_instance
