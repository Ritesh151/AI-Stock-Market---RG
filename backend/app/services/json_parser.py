"""
Robust JSON Parser for RG AI.
Safely extracts and parses JSON from raw text, Markdown fences, and conversational boundaries.
Strictly avoids eval() or arbitrary code execution.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from app.core.exceptions import AppException
from app.core.validation_config import MAX_JSON_DEPTH, MAX_JSON_PAYLOAD_SIZE
from app.core.logging import get_logger

logger = get_logger("services.json_parser")

# Regex to detect code fences
_CODE_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*([\s\S]*?)\s*```",
    re.IGNORECASE,
)


class JsonParseError(AppException):
    """Raised when JSON parsing fails or payload violates security constraints."""

    def __init__(self, message: str, code: str = "INVALID_JSON", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=422, details=details)


class JsonParser:
    """Safe, bounded JSON parser for unstructured AI responses."""

    def __init__(self, max_size: int = MAX_JSON_PAYLOAD_SIZE, max_depth: int = MAX_JSON_DEPTH) -> None:
        self.max_size = max_size
        self.max_depth = max_depth

    def parse(self, raw_text: str) -> Dict[str, Any]:
        """
        Parses raw text into a Python dictionary.
        Handles Markdown fences, leading conversational filler, and trailing commentary.
        Rejects multiple ambiguous root objects.
        """
        if not isinstance(raw_text, str):
            raise JsonParseError("Input must be a string.", code="INVALID_INPUT_TYPE")

        # 1. Check size bounds
        if len(raw_text.encode("utf-8")) > self.max_size:
            raise JsonParseError(
                f"Payload size exceeds maximum allowed limit of {self.max_size} bytes.",
                code="PAYLOAD_TOO_LARGE",
            )

        trimmed = raw_text.strip()
        if not trimmed:
            raise JsonParseError("Response content is empty.", code="EMPTY_RESPONSE")

        # 2. Check for Markdown code block first
        extracted_from_fence = self._extract_code_fence(trimmed)
        candidate_text = extracted_from_fence if extracted_from_fence is not None else trimmed

        # 3. Direct parse attempt
        try:
            parsed = json.loads(candidate_text)
            if isinstance(parsed, dict):
                self._verify_depth(parsed)
                return parsed
            raise JsonParseError(
                f"Expected JSON object at root, got {type(parsed).__name__}.",
                code="INVALID_ROOT_TYPE",
            )
        except json.JSONDecodeError:
            pass  # Fall through to conversational wrapper extraction

        # 4. Extract single unambiguous JSON object boundary from conversational wrapper
        json_obj_str = self._extract_balanced_json_object(candidate_text)
        if json_obj_str is None:
            raise JsonParseError(
                "The response is not valid JSON and contains no recognizable JSON object.",
                code="INVALID_JSON",
            )

        try:
            parsed = json.loads(json_obj_str)
            if not isinstance(parsed, dict):
                raise JsonParseError(
                    f"Expected JSON object at root, got {type(parsed).__name__}.",
                    code="INVALID_ROOT_TYPE",
                )
            self._verify_depth(parsed)
            return parsed
        except json.JSONDecodeError as err:
            raise JsonParseError(
                f"The response is not valid JSON: {err.msg} at line {err.lineno}, column {err.colno}.",
                code="INVALID_JSON",
            )

    def _extract_code_fence(self, text: str) -> Optional[str]:
        """Extracts content inside markdown code fences if present."""
        matches = _CODE_FENCE_PATTERN.findall(text)
        if len(matches) == 1:
            return matches[0].strip()
        if len(matches) > 1:
            raise JsonParseError(
                "Multiple markdown code blocks detected. Ambiguous response rejected.",
                code="AMBIGUOUS_JSON_BLOCKS",
            )
        return None

    def _extract_balanced_json_object(self, text: str) -> Optional[str]:
        """
        Locates the first '{' and matches its closing '}'.
        Verifies there is no second conflicting root object in the remaining text.
        """
        start_idx = text.find("{")
        if start_idx == -1:
            return None

        depth = 0
        in_string = False
        escape = False
        end_idx = -1

        for i in range(start_idx, len(text)):
            char = text[i]

            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break

        if depth != 0 or end_idx == -1:
            raise JsonParseError("Truncated or unbalanced JSON object detected.", code="TRUNCATED_JSON")

        candidate = text[start_idx : end_idx + 1]

        # Check remainder of text for a second conflicting object
        remainder = text[end_idx + 1 :]
        second_start = remainder.find("{")
        if second_start != -1:
            # Check if second start is genuinely another balanced object
            second_depth = 0
            second_in_str = False
            second_escape = False
            for j in range(second_start, len(remainder)):
                c = remainder[j]
                if second_in_str:
                    if second_escape:
                        second_escape = False
                    elif c == "\\":
                        second_escape = True
                    elif c == '"':
                        second_in_str = False
                else:
                    if c == '"':
                        second_in_str = True
                    elif c == "{":
                        second_depth += 1
                    elif c == "}":
                        second_depth -= 1
                        if second_depth == 0:
                            raise JsonParseError(
                                "Multiple distinct JSON objects detected in response text. Ambiguous response rejected.",
                                code="AMBIGUOUS_MULTIPLE_OBJECTS",
                            )

        return candidate

    def _verify_depth(self, item: Any, current_depth: int = 1) -> None:
        """Recursively validates that JSON object does not exceed max recursion depth."""
        if current_depth > self.max_depth:
            raise JsonParseError(
                f"JSON nesting depth exceeds maximum allowed limit of {self.max_depth}.",
                code="EXCESSIVE_NESTING_DEPTH",
            )
        if isinstance(item, dict):
            for v in item.values():
                self._verify_depth(v, current_depth + 1)
        elif isinstance(item, list):
            for v in item:
                self._verify_depth(v, current_depth + 1)


_json_parser_instance: Optional[JsonParser] = None


def get_json_parser() -> JsonParser:
    """Returns singleton instance of JsonParser."""
    global _json_parser_instance
    if _json_parser_instance is None:
        _json_parser_instance = JsonParser()
    return _json_parser_instance
