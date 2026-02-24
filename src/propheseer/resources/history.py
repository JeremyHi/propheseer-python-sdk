"""History resource for accessing historical market snapshots."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from propheseer._response import APIResponse
from propheseer.types.history import MarketHistoryEntry, SnapshotDate

if TYPE_CHECKING:
    from propheseer._base_client import BaseAsyncClient, BaseSyncClient


class SyncHistory:
    """Synchronous history resource.

    Access historical market snapshots. Requires Business plan or higher.
    """

    def __init__(self, client: "BaseSyncClient") -> None:
        self._client = client

    def list(
        self,
        *,
        market_id: Optional[str] = None,
        source: Optional[str] = None,
        category: Optional[str] = None,
        days: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> APIResponse[List[MarketHistoryEntry]]:
        """List historical market snapshots.

        Requires Business plan or higher.

        Args:
            market_id: Filter by specific market ID.
            source: Filter by source platform.
            category: Filter by category.
            days: Number of days of history (default: 30).
            limit: Maximum results (default: 1000).

        Returns:
            An :class:`APIResponse` containing a list of
            :class:`MarketHistoryEntry` objects.

        Example::

            result = client.history.list(market_id="pm_12345", days=7)
            for entry in result.data:
                print(f"{entry.snapshot_date}: {entry.data}")
        """
        query: Dict[str, Any] = {
            "market_id": market_id,
            "source": source,
            "category": category,
            "days": days,
            "limit": limit,
        }

        raw, rate_limit, response = self._client._request(
            "GET", "/v1/markets/history", query=query
        )

        data = [MarketHistoryEntry.from_dict(e) for e in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)

    def dates(self) -> APIResponse[List[SnapshotDate]]:
        """List available snapshot dates.

        Requires Business plan or higher.

        Returns:
            An :class:`APIResponse` containing a list of :class:`SnapshotDate`
            objects.

        Example::

            result = client.history.dates()
            for d in result.data:
                print(f"{d.date}: {d.count} markets")
        """
        raw, rate_limit, response = self._client._request(
            "GET", "/v1/markets/history/dates"
        )

        data = [SnapshotDate.from_dict(d) for d in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)


class AsyncHistory:
    """Asynchronous history resource.

    Access historical market snapshots. Requires Business plan or higher.
    """

    def __init__(self, client: "BaseAsyncClient") -> None:
        self._client = client

    async def list(
        self,
        *,
        market_id: Optional[str] = None,
        source: Optional[str] = None,
        category: Optional[str] = None,
        days: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> APIResponse[List[MarketHistoryEntry]]:
        """List historical market snapshots.

        Requires Business plan or higher.

        Args:
            market_id: Filter by specific market ID.
            source: Filter by source platform.
            category: Filter by category.
            days: Number of days of history (default: 30).
            limit: Maximum results (default: 1000).

        Returns:
            An :class:`APIResponse` containing a list of
            :class:`MarketHistoryEntry` objects.
        """
        query: Dict[str, Any] = {
            "market_id": market_id,
            "source": source,
            "category": category,
            "days": days,
            "limit": limit,
        }

        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/markets/history", query=query
        )

        data = [MarketHistoryEntry.from_dict(e) for e in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)

    async def dates(self) -> APIResponse[List[SnapshotDate]]:
        """List available snapshot dates.

        Requires Business plan or higher.

        Returns:
            An :class:`APIResponse` containing a list of :class:`SnapshotDate`
            objects.
        """
        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/markets/history/dates"
        )

        data = [SnapshotDate.from_dict(d) for d in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)
