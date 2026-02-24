"""Arbitrage resource for finding cross-platform arbitrage opportunities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from propheseer._response import APIResponse
from propheseer.types.arbitrage import ArbitrageOpportunity, ArbitrageFindParams

if TYPE_CHECKING:
    from propheseer._base_client import BaseAsyncClient, BaseSyncClient


class SyncArbitrage:
    """Synchronous arbitrage resource.

    Find cross-platform arbitrage opportunities. Requires Pro plan or higher.
    """

    def __init__(self, client: "BaseSyncClient") -> None:
        self._client = client

    def find(
        self,
        *,
        min_spread: Optional[float] = None,
        category: Optional[str] = None,
    ) -> APIResponse[List[ArbitrageOpportunity]]:
        """Find arbitrage opportunities across platforms.

        Requires Pro plan or higher.

        Args:
            min_spread: Minimum spread to include (default: 0.03).
            category: Filter by category.

        Returns:
            An :class:`APIResponse` containing a list of
            :class:`ArbitrageOpportunity` objects.

        Example::

            result = client.arbitrage.find(min_spread=0.05)
            for opp in result.data:
                print(f"{opp.question}: {opp.potential_return}")
        """
        query: Dict[str, Any] = {
            "min_spread": min_spread,
            "category": category,
        }

        raw, rate_limit, response = self._client._request(
            "GET", "/v1/arbitrage", query=query
        )

        data = [ArbitrageOpportunity.from_dict(o) for o in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)


class AsyncArbitrage:
    """Asynchronous arbitrage resource.

    Find cross-platform arbitrage opportunities. Requires Pro plan or higher.
    """

    def __init__(self, client: "BaseAsyncClient") -> None:
        self._client = client

    async def find(
        self,
        *,
        min_spread: Optional[float] = None,
        category: Optional[str] = None,
    ) -> APIResponse[List[ArbitrageOpportunity]]:
        """Find arbitrage opportunities across platforms.

        Requires Pro plan or higher.

        Args:
            min_spread: Minimum spread to include (default: 0.03).
            category: Filter by category.

        Returns:
            An :class:`APIResponse` containing a list of
            :class:`ArbitrageOpportunity` objects.
        """
        query: Dict[str, Any] = {
            "min_spread": min_spread,
            "category": category,
        }

        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/arbitrage", query=query
        )

        data = [ArbitrageOpportunity.from_dict(o) for o in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)
