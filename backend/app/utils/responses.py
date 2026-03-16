"""Structured API response helpers."""

from __future__ import annotations

from typing import Any, Optional


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[dict] = None,
) -> dict:
    """Standard JSON envelope returned by every endpoint."""
    body: dict = {"success": True, "message": message, "data": data}
    if meta is not None:
        body["meta"] = meta
    return body


def error_response(
    message: str = "Error",
    details: Any = None,
) -> dict:
    """Standard error envelope (used by exception handlers)."""
    return {"success": False, "message": message, "details": details}
