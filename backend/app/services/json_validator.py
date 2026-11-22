"""
JSON Validator for RG AI Strict JSON Engine.
Applies Pydantic schema validation, domain financial rules, and consistency checks.
Distinguishes fatal schema errors from contextual financial warnings.
"""

from typing import Any, Dict, List, Optional, Tuple, Type
from pydantic import BaseModel, ValidationError
from app.core.exceptions import AppException
from app.core.schema_registry import SchemaRegistry, get_schema_registry
from app.schemas.response_envelope import ValidationErrorDetail, ValidationErrorPayload
from app.core.logging import get_logger

logger = get_logger("services.json_validator")


class ValidationResult:
    """Outcome of JSON schema and financial consistency validation."""

    def __init__(
        self,
        is_valid: bool,
        schema_type: str,
        validated_data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
        error: Optional[ValidationErrorPayload] = None,
    ) -> None:
        self.is_valid = is_valid
        self.schema_type = schema_type
        self.validated_data = validated_data
        self.warnings = warnings or []
        self.error = error


class JsonValidator:
    """Validates parsed JSON against registered Pydantic schemas and applies financial consistency rules."""

    def __init__(self, registry: Optional[SchemaRegistry] = None) -> None:
        self.registry = registry or get_schema_registry()

    def validate(
        self,
        data: Dict[str, Any],
        expected_type: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validates a parsed JSON dictionary.
        If expected_type is None, automatically detects type from data structure.
        """
        if not isinstance(data, dict):
            return ValidationResult(
                is_valid=False,
                schema_type="unknown",
                error=ValidationErrorPayload(
                    code="INVALID_DATA_TYPE",
                    message="Parsed JSON root must be an object dictionary.",
                ),
            )

        # 1. Determine target schema type
        target_type = expected_type or self.registry.detect_type(data)
        if not target_type:
            return ValidationResult(
                is_valid=False,
                schema_type="unknown",
                error=ValidationErrorPayload(
                    code="UNSUPPORTED_RESPONSE_TYPE",
                    message="Could not match response structure to any supported analysis schema.",
                ),
            )

        model_cls: Optional[Type[BaseModel]] = self.registry.get_schema(target_type)
        if not model_cls:
            return ValidationResult(
                is_valid=False,
                schema_type=target_type,
                error=ValidationErrorPayload(
                    code="UNSUPPORTED_RESPONSE_TYPE",
                    message=f"Response type '{target_type}' is not supported.",
                ),
            )

        # 2. Execute Pydantic Model Validation
        try:
            instance = model_cls.model_validate(data)
            validated_dict = instance.model_dump(mode="json")
        except ValidationError as val_err:
            details: List[ValidationErrorDetail] = []
            for err in val_err.errors():
                loc_str = " -> ".join(str(loc) for loc in err["loc"])
                details.append(
                    ValidationErrorDetail(
                        field=loc_str if loc_str else None,
                        issue=err["msg"],
                    )
                )
            return ValidationResult(
                is_valid=False,
                schema_type=target_type,
                error=ValidationErrorPayload(
                    code="SCHEMA_VALIDATION_FAILED",
                    message=f"The response does not match the expected '{target_type}' schema.",
                    details=details,
                ),
            )

        # 3. Financial Consistency & Sanity Rules (generate warnings or reject invalid relationships)
        warnings: List[str] = []
        consistency_error = self._apply_financial_consistency(target_type, validated_dict, warnings)
        if consistency_error:
            return ValidationResult(
                is_valid=False,
                schema_type=target_type,
                error=consistency_error,
            )

        return ValidationResult(
            is_valid=True,
            schema_type=target_type,
            validated_data=validated_dict,
            warnings=warnings,
        )

    def _apply_financial_consistency(
        self,
        schema_type: str,
        data: Dict[str, Any],
        warnings: List[str],
    ) -> Optional[ValidationErrorPayload]:
        """
        Executes domain financial consistency checks.
        Returns ValidationErrorPayload if fatal contradiction found, else appends contextual warnings.
        """
        if schema_type == "stock_analysis":
            rec = data.get("recommendation", "")
            price = data.get("current_price")
            target = data.get("target_price")
            sl = data.get("stop_loss")
            entry_zone = data.get("entry_zone") or {}
            entry_min = entry_zone.get("min")
            entry_max = entry_zone.get("max")

            # Check entry zone sanity if both provided
            if entry_min is not None and entry_max is not None and entry_min > entry_max:
                return ValidationErrorPayload(
                    code="INVALID_ENTRY_ZONE",
                    message=f"Entry zone min ({entry_min}) cannot exceed max ({entry_max}).",
                    details=[
                        ValidationErrorDetail(
                            field="entry_zone",
                            issue=f"Minimum entry ({entry_min}) > maximum entry ({entry_max})",
                        )
                    ],
                )

            # Check recommendation vs target/stop-loss context
            benchmark_price = entry_max if entry_max is not None else price

            if rec in {"BUY", "STRONG_BUY", "ACCUMULATE"}:
                if target is not None and benchmark_price is not None and target < benchmark_price:
                    warnings.append(
                        f"Recommendation is {rec} but target price ({target}) is below current/entry price ({benchmark_price})."
                    )
                if sl is not None and benchmark_price is not None and sl > benchmark_price:
                    warnings.append(
                        f"Recommendation is {rec} but stop loss ({sl}) is above current/entry price ({benchmark_price})."
                    )

            elif rec in {"SELL", "STRONG_SELL", "REDUCE"}:
                if target is not None and benchmark_price is not None and target > benchmark_price:
                    warnings.append(
                        f"Recommendation is {rec} but target price ({target}) is above current price ({benchmark_price})."
                    )

            # Check missing timestamps or sources
            if not data.get("data_timestamp"):
                warnings.append("Analysis lacks explicit quote timestamp metadata.")
            if not data.get("data_source"):
                warnings.append("Analysis source is unverified or unspecified.")

        return None


_json_validator_instance: Optional[JsonValidator] = None


def get_json_validator() -> JsonValidator:
    """Returns singleton instance of JsonValidator."""
    global _json_validator_instance
    if _json_validator_instance is None:
        _json_validator_instance = JsonValidator()
    return _json_validator_instance
