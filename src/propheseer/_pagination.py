"""Pagination utilities for paginated API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
)

from propheseer._response import RateLimitInfo

T = TypeVar("T")


@dataclass
class PaginationMeta:
    """Pagination metadata returned by paginated endpoints.

    Attributes:
        total: Total number of items matching the query.
        limit: Maximum items per page.
        offset: Current offset.
        sources: Source metadata (varies by endpoint).
    """

    total: int
    limit: int
    offset: int
    sources: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaginationMeta":
        """Create a PaginationMeta from a dictionary."""
        return cls(
            total=data.get("total", 0),
            limit=data.get("limit", 0),
            offset=data.get("offset", 0),
            sources=data.get("sources"),
        )


class SyncPage(Generic[T]):
    """A page of results from a paginated API endpoint.

    Attributes:
        data: Items on this page.
        meta: Pagination metadata.
        rate_limit: Rate limit information.
    """

    data: List[T]
    meta: PaginationMeta
    rate_limit: Optional[RateLimitInfo]

    def __init__(
        self,
        data: List[T],
        meta: PaginationMeta,
        rate_limit: Optional[RateLimitInfo],
    ) -> None:
        self.data = data
        self.meta = meta
        self.rate_limit = rate_limit

    def has_more(self) -> bool:
        """Whether there are more pages available."""
        return self.meta.offset + self.meta.limit < self.meta.total

    def next_offset(self) -> Optional[int]:
        """The offset for the next page, or ``None`` if no more pages."""
        if not self.has_more():
            return None
        return self.meta.offset + self.meta.limit

    def __iter__(self) -> Iterator[T]:
        """Iterate over items on this page."""
        return iter(self.data)

    def __len__(self) -> int:
        """Number of items on this page."""
        return len(self.data)

    def __repr__(self) -> str:
        return (
            f"SyncPage(data=[...{len(self.data)} items], "
            f"total={self.meta.total}, "
            f"offset={self.meta.offset})"
        )


class AsyncPage(Generic[T]):
    """An async page of results from a paginated API endpoint.

    Attributes:
        data: Items on this page.
        meta: Pagination metadata.
        rate_limit: Rate limit information.
    """

    data: List[T]
    meta: PaginationMeta
    rate_limit: Optional[RateLimitInfo]

    def __init__(
        self,
        data: List[T],
        meta: PaginationMeta,
        rate_limit: Optional[RateLimitInfo],
    ) -> None:
        self.data = data
        self.meta = meta
        self.rate_limit = rate_limit

    def has_more(self) -> bool:
        """Whether there are more pages available."""
        return self.meta.offset + self.meta.limit < self.meta.total

    def next_offset(self) -> Optional[int]:
        """The offset for the next page, or ``None`` if no more pages."""
        if not self.has_more():
            return None
        return self.meta.offset + self.meta.limit

    def __iter__(self) -> Iterator[T]:
        """Iterate over items on this page (synchronously)."""
        return iter(self.data)

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over items on this page asynchronously."""
        for item in self.data:
            yield item

    def __len__(self) -> int:
        """Number of items on this page."""
        return len(self.data)

    def __repr__(self) -> str:
        return (
            f"AsyncPage(data=[...{len(self.data)} items], "
            f"total={self.meta.total}, "
            f"offset={self.meta.offset})"
        )
