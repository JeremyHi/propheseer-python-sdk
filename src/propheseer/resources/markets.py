"""Markets resource for listing and retrieving prediction markets."""

from __future__ import annotations

from typing import Any, Dict, Generator, AsyncGenerator, Optional, TYPE_CHECKING
from urllib.parse import quote

from propheseer._pagination import PaginationMeta, SyncPage, AsyncPage
from propheseer._response import APIResponse
from propheseer.types.markets import Market, MarketListParams

if TYPE_CHECKING:
    from propheseer._base_client import BaseAsyncClient, BaseSyncClient


class SyncMarkets:
    """Synchronous markets resource.

    List and search prediction markets from Polymarket, Kalshi, and Gemini.
    """

    def __init__(self, client: "BaseSyncClient") -> None:
        self._client = client

    def list(
        self,
        *,
        source: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        q: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> SyncPage[Market]:
        """List markets with optional filters.

        Args:
            source: Filter by source platform (``"polymarket"``, ``"kalshi"``,
                ``"gemini"``).
            category: Filter by category.
            status: Filter by status (``"open"``, ``"closed"``, ``"settled"``).
            q: Search query string.
            limit: Maximum results per page (default: 50, max: 200).
            offset: Offset for pagination (default: 0).

        Returns:
            A :class:`SyncPage` of :class:`Market` objects.

        Example::

            page = client.markets.list(source="polymarket", limit=10)
            for market in page.data:
                print(market.question)
        """
        query: Dict[str, Any] = {
            "source": source,
            "category": category,
            "status": status,
            "q": q,
            "limit": limit,
            "offset": offset,
        }

        raw, rate_limit, response = self._client._request(
            "GET", "/v1/markets", query=query
        )

        data = [Market.from_dict(m) for m in raw.get("data", [])]
        meta = PaginationMeta.from_dict(raw.get("meta", {}))
        return SyncPage(data, meta, rate_limit)

    def get(self, market_id: str) -> APIResponse[Market]:
        """Get a single market by ID.

        Args:
            market_id: The market ID (e.g. ``"pm_12345"``).

        Returns:
            An :class:`APIResponse` containing the :class:`Market`.

        Example::

            result = client.markets.get("pm_12345")
            print(result.data.question)
        """
        encoded_id = quote(market_id, safe="")
        raw, rate_limit, response = self._client._request(
            "GET", f"/v1/markets/{encoded_id}"
        )

        market = Market.from_dict(raw.get("data", {}))
        return APIResponse(data=market, rate_limit=rate_limit, http_response=response)

    def list_auto_paginate(
        self,
        *,
        source: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        q: Optional[str] = None,
        limit: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> Generator[Market, None, None]:
        """Auto-paginate through all markets matching the query.

        Args:
            source: Filter by source platform.
            category: Filter by category.
            status: Filter by status.
            q: Search query string.
            limit: Page size (default: 50).
            max_items: Maximum total items to yield.

        Yields:
            Individual :class:`Market` objects.

        Example::

            for market in client.markets.list_auto_paginate(source="kalshi"):
                print(market.question)
        """
        page_limit = limit or 50
        offset = 0
        yielded = 0

        while True:
            page = self.list(
                source=source,
                category=category,
                status=status,
                q=q,
                limit=page_limit,
                offset=offset,
            )

            for item in page.data:
                yield item
                yielded += 1
                if max_items and yielded >= max_items:
                    return

            if not page.has_more() or len(page.data) == 0:
                return

            offset = page.next_offset()  # type: ignore[assignment]


class AsyncMarkets:
    """Asynchronous markets resource.

    List and search prediction markets from Polymarket, Kalshi, and Gemini.
    """

    def __init__(self, client: "BaseAsyncClient") -> None:
        self._client = client

    async def list(
        self,
        *,
        source: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        q: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> AsyncPage[Market]:
        """List markets with optional filters.

        Args:
            source: Filter by source platform.
            category: Filter by category.
            status: Filter by status.
            q: Search query string.
            limit: Maximum results per page (default: 50, max: 200).
            offset: Offset for pagination (default: 0).

        Returns:
            An :class:`AsyncPage` of :class:`Market` objects.
        """
        query: Dict[str, Any] = {
            "source": source,
            "category": category,
            "status": status,
            "q": q,
            "limit": limit,
            "offset": offset,
        }

        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/markets", query=query
        )

        data = [Market.from_dict(m) for m in raw.get("data", [])]
        meta = PaginationMeta.from_dict(raw.get("meta", {}))
        return AsyncPage(data, meta, rate_limit)

    async def get(self, market_id: str) -> APIResponse[Market]:
        """Get a single market by ID.

        Args:
            market_id: The market ID (e.g. ``"pm_12345"``).

        Returns:
            An :class:`APIResponse` containing the :class:`Market`.
        """
        encoded_id = quote(market_id, safe="")
        raw, rate_limit, response = await self._client._request(
            "GET", f"/v1/markets/{encoded_id}"
        )

        market = Market.from_dict(raw.get("data", {}))
        return APIResponse(data=market, rate_limit=rate_limit, http_response=response)

    async def list_auto_paginate(
        self,
        *,
        source: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        q: Optional[str] = None,
        limit: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> AsyncGenerator[Market, None]:
        """Auto-paginate through all markets matching the query.

        Args:
            source: Filter by source platform.
            category: Filter by category.
            status: Filter by status.
            q: Search query string.
            limit: Page size (default: 50).
            max_items: Maximum total items to yield.

        Yields:
            Individual :class:`Market` objects.
        """
        page_limit = limit or 50
        offset = 0
        yielded = 0

        while True:
            page = await self.list(
                source=source,
                category=category,
                status=status,
                q=q,
                limit=page_limit,
                offset=offset,
            )

            for item in page.data:
                yield item
                yielded += 1
                if max_items and yielded >= max_items:
                    return

            if not page.has_more() or len(page.data) == 0:
                return

            offset = page.next_offset()  # type: ignore[assignment]
