"""Reusable pagination utilities."""

from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field
from sqlalchemy.orm import Query


class PaginationParams(BaseModel):
    """Query parameters accepted by all list endpoints.

    Supports both ``page_size`` and ``limit`` as parameter names.
    """

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page (alias: limit)")

    # Keep 'limit' as an accepted alias at construction time
    def __init__(self, **data):
        if "limit" in data and "page_size" not in data:
            data["page_size"] = data.pop("limit")
        super().__init__(**data)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResult(BaseModel):
    """Envelope returned inside the ``data`` key of paginated responses."""

    items: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


def paginate(query: Query, params: PaginationParams) -> PaginatedResult:
    """Apply offset/limit pagination to a SQLAlchemy query."""
    total = query.count()
    items = query.offset(params.skip).limit(params.page_size).all()
    total_pages = max(1, (total + params.page_size - 1) // params.page_size)
    return PaginatedResult(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
    )
