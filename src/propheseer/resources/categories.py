"""Categories resource for listing market categories."""

from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

from propheseer._response import APIResponse
from propheseer.types.categories import Category

if TYPE_CHECKING:
    from propheseer._base_client import BaseAsyncClient, BaseSyncClient


class SyncCategories:
    """Synchronous categories resource."""

    def __init__(self, client: "BaseSyncClient") -> None:
        self._client = client

    def list(self) -> APIResponse[List[Category]]:
        """List all available market categories.

        Returns:
            An :class:`APIResponse` containing a list of :class:`Category` objects.

        Example::

            result = client.categories.list()
            for cat in result.data:
                print(f"{cat.name}: {cat.subcategories}")
        """
        raw, rate_limit, response = self._client._request("GET", "/v1/categories")

        data = [Category.from_dict(c) for c in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)


class AsyncCategories:
    """Asynchronous categories resource."""

    def __init__(self, client: "BaseAsyncClient") -> None:
        self._client = client

    async def list(self) -> APIResponse[List[Category]]:
        """List all available market categories.

        Returns:
            An :class:`APIResponse` containing a list of :class:`Category` objects.
        """
        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/categories"
        )

        data = [Category.from_dict(c) for c in raw.get("data", [])]
        return APIResponse(data=data, rate_limit=rate_limit, http_response=response)
