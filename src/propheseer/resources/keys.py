"""Keys resource for API key info and usage statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from propheseer._response import APIResponse
from propheseer.types.keys import KeyInfo

if TYPE_CHECKING:
    from propheseer._base_client import BaseAsyncClient, BaseSyncClient


class SyncKeys:
    """Synchronous keys resource.

    Get API key information and usage statistics.
    """

    def __init__(self, client: "BaseSyncClient") -> None:
        self._client = client

    def me(self) -> APIResponse[KeyInfo]:
        """Get information about the current API key, including usage statistics.

        Returns:
            An :class:`APIResponse` containing the :class:`KeyInfo`.

        Example::

            result = client.keys.me()
            print(f"Plan: {result.data.plan}")
            print(f"Daily: {result.data.usage.daily}/{result.data.limits.requests_per_day}")
        """
        raw, rate_limit, response = self._client._request("GET", "/v1/keys/me")

        key_info = KeyInfo.from_dict(raw.get("data", {}))
        return APIResponse(data=key_info, rate_limit=rate_limit, http_response=response)


class AsyncKeys:
    """Asynchronous keys resource.

    Get API key information and usage statistics.
    """

    def __init__(self, client: "BaseAsyncClient") -> None:
        self._client = client

    async def me(self) -> APIResponse[KeyInfo]:
        """Get information about the current API key, including usage statistics.

        Returns:
            An :class:`APIResponse` containing the :class:`KeyInfo`.
        """
        raw, rate_limit, response = await self._client._request(
            "GET", "/v1/keys/me"
        )

        key_info = KeyInfo.from_dict(raw.get("data", {}))
        return APIResponse(data=key_info, rate_limit=rate_limit, http_response=response)
