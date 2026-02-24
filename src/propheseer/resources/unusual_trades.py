"""Unusual trades resource for detecting unusual trading activity."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, Generator, Optional, TYPE_CHECKING

from propheseer._pagination import PaginationMeta, SyncPage, AsyncPage
from propheseer.types.unusual_trades import UnusualTrade, UnusualTradeListParams

if TYPE_CHECKING:
    from propheseer._base_client import BaseAsyncClient, BaseSyncClient


class SyncUnusualTrades:
    """Synchronous unusual trades resource.

    Detect unusual trading activity. Requires Pro plan or higher.
    """

    def __init__(self, client: "BaseSyncClient") -> None:
        self._client = client

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        market_id: Optional[str] = None,
        reason: Optional[str] = None,
        min_score: Optional[float] = None,
        since: Optional[str] = None,
        side: Optional[str] = None,
        source: Optional[str] = None,
        exclude_categories: Optional[str] = None,
    ) -> SyncPage[UnusualTrade]:
        """List unusual trades detected by the system.

        Requires Pro plan or higher.

        Args:
            limit: Maximum results per page (default: 50, max: 100).
            offset: Offset for pagination.
            market_id: Filter by market ID.
            reason: Filter by detection reason.
            min_score: Minimum anomaly score.
            since: Only trades since this date (ISO 8601).
            side: Filter by trade side (``"BUY"`` or ``"SELL"``).
            source: Filter by source platform.
            exclude_categories: Categories to exclude (comma-separated).

        Returns:
            A :class:`SyncPage` of :class:`UnusualTrade` objects.

        Example::

            page = client.unusual_trades.list(reason="high_amount", limit=10)
            for trade in page.data:
                print(f"${trade.trade.usdc_value} on {trade.market.question}")
        """
        query: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "market_id": market_id,
            "reason": reason,
            "min_score": min_score,
            "since": since,
            "side": side,
            "source": source,
            "exclude_categories": exclude_categories,
        }

        raw, rate_limit, response = self._client._request(
            "GET", "/v1/unusual-trades", query=query
        )

        data = [UnusualTrade.from_dict(t) for t in raw.get("data", [])]
        meta = PaginationMeta.from_dict(raw.get("meta", {}))
        return SyncPage(data, meta, rate_limit)

    def list_auto_paginate(
        self,
        *,
        limit: Optional[int] = None,
        market_id: Optional[str] = None,
        reason: Optional[str] = None,
        min_score: Optional[float] = None,
        since: Optional[str] = None,
        side: Optional[str] = None,
        source: Optional[str] = None,
        exclude_categories: Optional[str] = None,
        max_items: Optional[int] = None,
    ) -> Generator[UnusualTrade, None, None]:
        """Auto-paginate through all unusual trades matching the query.

        Args:
            limit: Page size (default: 50).
            market_id: Filter by market ID.
            reason: Filter by detection reason.
            min_score: Minimum anomaly score.
            since: Only trades since this date (ISO 8601).
            side: Filter by trade side.
            source: Filter by source platform.
            exclude_categories: Categories to exclude.
            max_items: Maximum total items to yield.

        Yields:
            Individual :class:`UnusualTrade` objects.
        """
        page_limit = limit or 50
        offset = 0
        yielded = 0

        while True:
            page = self.list(
                limit=page_limit,
                offset=offset,
                market_id=market_id,
                reason=reason,
                min_score=min_score,
                since=since,
                side=side,
                source=source,
                exclude_categories=exclude_categories,
            )

            for item in page.data:
                yield item
                yielded += 1
                if max_items and yielded >= max_items:
                    return

            if not page.has_more() or len(page.data) == 0:
                return

            offset = page.next_offset()  # type: ignore[assignment]


class AsyncUnusualTrades:
    """Asynchronous unusual trades resource.

    Detect unusual trading activity. Requires Pro plan or higher.
    """

    def __init__(self, client: "BaseAsyncClient") -> None:
        self._client = client

    async def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        market_id: Optional[str] = None,
        reason: Optional[str] = None,
        min_score: Optional[float] = None,
        since: Optional[str] = None,
        side: Optional[str] = None,
        source: Optional[str] = None,
        exclude_categories: Optional[str] = None,
    ) -> AsyncPage[UnusualTrade]:
        """List unusual trades detected by the system.

        Requires Pro plan or higher.

        Args:
            limit: Maximum results per page (default: 50, max: 100).
            offset: Offset for pagination.
            market_id: Filter by market ID.
            reason: Filter by detection reason.
            min_score: Minimum anomaly score.
            since: Only trades since this date (ISO 8601).
            side: Filter by trade side.
            source: Filter by source platform.
            exclude_categories: Categories to exclude.

        Returns:
            An :class:`AsyncPage` of :class:`UnusualTrade` objects.
        """
        query: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "market_id": market_id,
            "reason": reason,
            "min_score": min_score,
            "since": since,
            "side": side,
            "source": source,
            "exclude_categories": exclude_categories,
        }

        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/unusual-trades", query=query
        )

        data = [UnusualTrade.from_dict(t) for t in raw.get("data", [])]
        meta = PaginationMeta.from_dict(raw.get("meta", {}))
        return AsyncPage(data, meta, rate_limit)

    async def list_auto_paginate(
        self,
        *,
        limit: Optional[int] = None,
        market_id: Optional[str] = None,
        reason: Optional[str] = None,
        min_score: Optional[float] = None,
        since: Optional[str] = None,
        side: Optional[str] = None,
        source: Optional[str] = None,
        exclude_categories: Optional[str] = None,
        max_items: Optional[int] = None,
    ) -> AsyncGenerator[UnusualTrade, None]:
        """Auto-paginate through all unusual trades matching the query.

        Yields:
            Individual :class:`UnusualTrade` objects.
        """
        page_limit = limit or 50
        offset = 0
        yielded = 0

        while True:
            page = await self.list(
                limit=page_limit,
                offset=offset,
                market_id=market_id,
                reason=reason,
                min_score=min_score,
                since=since,
                side=side,
                source=source,
                exclude_categories=exclude_categories,
            )

            for item in page.data:
                yield item
                yielded += 1
                if max_items and yielded >= max_items:
                    return

            if not page.has_more() or len(page.data) == 0:
                return

            offset = page.next_offset()  # type: ignore[assignment]
