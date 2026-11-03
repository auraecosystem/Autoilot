"""Dependency-free validator for the v0.1 LMLM execution-request IR.

This validates structure and declared capability bounds. It does not authorize
execution; authorization belongs to the LMLM policy engine.
"""

from __future__ import annotations

from typing import Any, Mapping


class IRValidationError(ValueError):
    """Raised when an IR document violates the v0.1 contract."""


_TOP_LEVEL_KEYS = {
    "operation",
    "provider",
    "model",
    "input",
    "permissions",
    "verification",
}
_INPUT_KEYS = {"type", "source"}
_VERIFICATION_KEYS = {"required"}
_ALLOWED_PERMISSIONS = {"inference"}


def _require_exact_keys(
    value: Mapping[str, Any], expected: set[str], location: str
) -> None:
    actual = set(value)
    missing = expected - actual
    unknown = actual - expected
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing keys: {sorted(missing)}")
        if unknown:
            details.append(f"unknown keys: {sorted(unknown)}")
        raise IRValidationError(f"{location}: " + "; ".join(details))


def validate_ir(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a shallow normalized copy of a v0.1 IR document.

    The function rejects unknown fields and capabilities by default (fail
    closed). It intentionally performs no model loading or tool execution.
    """
    if not isinstance(document, Mapping):
        raise IRValidationError("IR must be a mapping")

    _require_exact_keys(document, _TOP_LEVEL_KEYS, "IR")

    if document["operation"] != "model.generate":
        raise IRValidationError("unsupported operation")
    if document["provider"] not in {"local", "builtin"}:
        raise IRValidationError("provider must be 'local' or 'builtin'")

    model = document["model"]
    if not isinstance(model, str) or not model.strip() or len(model) > 128:
        raise IRValidationError("model must be a non-empty string of at most 128 characters")

    input_spec = document["input"]
    if not isinstance(input_spec, Mapping):
        raise IRValidationError("input must be a mapping")
    _require_exact_keys(input_spec, _INPUT_KEYS, "input")
    if input_spec["type"] != "text" or input_spec["source"] != "user_input":
        raise IRValidationError("input must describe text sourced from user_input")

    permissions = document["permissions"]
    if not isinstance(permissions, list) or not permissions:
        raise IRValidationError("permissions must be a non-empty list")
    if any(not isinstance(item, str) for item in permissions):
        raise IRValidationError("permissions must contain strings")
    if len(set(permissions)) != len(permissions):
        raise IRValidationError("permissions must not contain duplicates")
    unknown_permissions = set(permissions) - _ALLOWED_PERMISSIONS
    if unknown_permissions:
        raise IRValidationError(
            f"unsupported permissions: {sorted(unknown_permissions)}"
        )

    verification = document["verification"]
    if not isinstance(verification, Mapping):
        raise IRValidationError("verification must be a mapping")
    _require_exact_keys(verification, _VERIFICATION_KEYS, "verification")
    if not isinstance(verification["required"], bool):
        raise IRValidationError("verification.required must be a boolean")

    # Return ordinary dicts so callers do not retain custom Mapping behavior.
    return {
        "operation": "model.generate",
        "provider": document["provider"],
        "model": model.strip(),
        "input": {"type": "text", "source": "user_input"},
        "permissions": sorted(permissions),
        "verification": {"required": verification["required"]},
    }
