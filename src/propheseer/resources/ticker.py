"""Ticker resource for public market ticker data."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from propheseer._response import APIResponse
from propheseer.types.ticker import TickerItem

if TYPE_CHECKING:
    from propheseer._base_client import BaseAsyncClient, BaseSyncClient


class SyncTicker:
    """Synchronous ticker resource.

    Public market ticker (no authentication required).
    """

    def __init__(self, client: "BaseSyncClient") -> None:
        self._client = client

    def list(
        self,
        *,
        limit: Optional[int] = None,
    ) -> APIResponse[List[TickerItem]]:
        """List ticker items (public, no auth required).

        Args:
            limit: Maximum items (default: 12, max: 20).

        Returns:
            An :class:`APIResponse` containing a list of :class:`TickerItem`
            objects.

        Example::

            result = client.ticker.list(limit=10)
            for item in result.data:
                print(f"{item.question}: {item.probability:.0%}")
        """
        query: Dict[str, Any] = {
            "limit": limit,
        }

        raw, rate_limit, response = self._client._request(
            "GET", "/v1/public/ticker", query=query, auth=False
        )

        data = [TickerItem.from_dict(t) for t in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)


class AsyncTicker:
    """Asynchronous ticker resource.

    Public market ticker (no authentication required).
    """

    def __init__(self, client: "BaseAsyncClient") -> None:
        self._client = client

    async def list(
        self,
        *,
        limit: Optional[int] = None,
    ) -> APIResponse[List[TickerItem]]:
        """List ticker items (public, no auth required).

        Args:
            limit: Maximum items (default: 12, max: 20).

        Returns:
            An :class:`APIResponse` containing a list of :class:`TickerItem`
            objects.
        """
        query: Dict[str, Any] = {
            "limit": limit,
        }

        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/public/ticker", query=query, auth=False
        )

        data = [TickerItem.from_dict(t) for t in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)
