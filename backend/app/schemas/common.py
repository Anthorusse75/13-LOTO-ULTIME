"""Common schemas — pagination, shared types."""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Dependency-injectable pagination parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int
