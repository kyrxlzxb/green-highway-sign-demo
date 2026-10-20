"""Provider-neutral multimodal inference contracts and safe JSON normalization."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InferenceErrorContract(BaseModel):
    """Sanitized provider or response-processing failure."""

    model_config = ConfigDict(extra="forbid")

    category: str
    code: str
    message: str
    provider_exception_type: str | None = None
    provider_error_code: str | None = None
    http_status: int | None = None
    request_id: str | None = None


class MultimodalInferenceRequest(BaseModel):
    """Reference-only request contract; image bytes never enter orchestration state."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model_id: str
    model_reference_type: Literal["model_id", "inference_profile"] = "model_id"
    region: str
    system_prompt_reference: str
    task_prompt_reference: str
    prompt_version: str
    image_artifact_reference: str
    image_media_type: str
    inference_parameters: dict[str, int | float]
    requested_response_schema_version: str
    run_id: str
    correlation_id: str

    @model_validator(mode="after")
    def references_only(self) -> "MultimodalInferenceRequest":
        if not self.image_artifact_reference or self.image_artifact_reference.startswith(("/", "\\")):
            raise ValueError("Image artifact reference must be a non-empty relative reference")
        return self


class MultimodalInferenceResponse(BaseModel):
    """Normalized provider response envelope."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model_id: str
    request_id: str | None = None
    raw_response_artifact_reference: str
    normalized_text: str = ""
    parsed_json_candidate: dict[str, Any] | None = None
    input_token_count: int | None = None
    output_token_count: int | None = None
    latency_ms: int | None = None
    stop_reason: str | None = None
    provider_warnings: list[str] = Field(default_factory=list)
    error: InferenceErrorContract | None = None
    retryable: bool = False


class RetryAttempt(BaseModel):
    """One bounded retry decision suitable for run evidence."""

    model_config = ConfigDict(extra="forbid")

    attempt_number: int = Field(ge=1)
    reason_code: str
    previous_error_category: str | None = None
    prompt_changed: bool = False
    image_changed: bool = False
    provider_request_id: str | None = None


class InferenceRetryPolicy(BaseModel):
    """Finite retry budgets for provider and response failures."""

    model_config = ConfigDict(extra="forbid")

    transient_provider_retries: int = Field(default=1, ge=0, le=3)
    throttling_retries: int = Field(default=1, ge=0, le=3)
    malformed_json_retries: int = Field(default=1, ge=0, le=2)
    schema_invalid_retries: int = Field(default=1, ge=0, le=2)
    semantic_invalid_retries: int = Field(default=0, ge=0, le=1)
    correction_attempts: int = Field(default=1, ge=0, le=1)

    def provider_budget(self, category: str) -> int:
        return self.throttling_retries if category == "throttling" else self.transient_provider_retries


@dataclass(frozen=True)
class InferenceCallContext:
    """Application-owned references supplied to a context-aware executor."""

    run_id: str
    system_prompt_reference: str
    task_prompt_reference: str
    prompt_version: str
    image_artifact_reference: str
    requested_response_schema_version: str = "1.0"
    correlation_id: str = ""

    def resolved_correlation_id(self) -> str:
        return self.correlation_id or f"corr-{uuid.uuid4().hex}"


class JsonNormalizationError(ValueError):
    """Raised when one unambiguous JSON object cannot be extracted safely."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class NormalizedJsonCandidate:
    text: str
    document: dict[str, Any]
    repairs: tuple[str, ...]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JsonNormalizationError("duplicate_json_key", "JSON contains a duplicate object key")
        result[key] = value
    return result


def _strip_fence(text: str) -> tuple[str, bool]:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped, False
    lines = stripped.splitlines()
    if len(lines) < 3 or lines[-1].strip() != "```":
        raise JsonNormalizationError("malformed_markdown_fence", "Markdown JSON fence is incomplete")
    return "\n".join(lines[1:-1]).strip(), True


def _balanced_objects(text: str) -> list[str]:
    objects: list[str] = []
    depth = 0
    start: int | None = None
    in_string = False
    escaped = False
    for index, character in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "{":
            if depth == 0:
                start = index
            depth += 1
        elif character == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(text[start : index + 1])
                start = None
    return objects


def normalize_json_candidate(text: str) -> NormalizedJsonCandidate:
    """Apply only deterministic structural repairs and reject ambiguity."""

    candidate, fenced = _strip_fence(text)
    repairs: list[str] = ["markdown_fence_removed"] if fenced else []
    try:
        document = json.loads(candidate, object_pairs_hook=_reject_duplicate_keys)
    except JsonNormalizationError:
        raise
    except json.JSONDecodeError:
        objects = _balanced_objects(candidate)
        if len(objects) != 1:
            raise JsonNormalizationError("ambiguous_json_object", "Response does not contain one unambiguous JSON object")
        candidate = objects[0]
        repairs.append("surrounding_text_trimmed")
        try:
            document = json.loads(candidate, object_pairs_hook=_reject_duplicate_keys)
        except JsonNormalizationError:
            raise
        except json.JSONDecodeError as error:
            raise JsonNormalizationError("malformed_json", "JSON candidate is malformed") from error
    if not isinstance(document, dict):
        raise JsonNormalizationError("json_root_not_object", "JSON response root must be an object")
    normalized = json.dumps(document, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return NormalizedJsonCandidate(normalized, document, tuple(repairs))
