"""Main Propheseer client classes (sync and async)."""

from __future__ import annotations

from typing import Optional

from propheseer._base_client import BaseAsyncClient, BaseSyncClient
from propheseer.resources.markets import SyncMarkets, AsyncMarkets
from propheseer.resources.categories import SyncCategories, AsyncCategories
from propheseer.resources.arbitrage import SyncArbitrage, AsyncArbitrage
from propheseer.resources.unusual_trades import SyncUnusualTrades, AsyncUnusualTrades
from propheseer.resources.history import SyncHistory, AsyncHistory
from propheseer.resources.keys import SyncKeys, AsyncKeys
from propheseer.resources.ticker import SyncTicker, AsyncTicker


class Propheseer(BaseSyncClient):
    """Synchronous Propheseer SDK client for the prediction markets API.

    Args:
        api_key: API key for authentication.
            Falls back to the ``PROPHESEER_API_KEY`` environment variable.
        base_url: Base URL for the API (default: ``https://api.propheseer.com``).
        timeout: Request timeout in seconds (default: 30).
        max_retries: Maximum number of retries on retryable errors (default: 2).

    Example::

        from propheseer import Propheseer

        client = Propheseer(api_key="pk_test_...")

        # List markets
        page = client.markets.list(source="polymarket")
        for market in page.data:
            print(market.question)

        # Find arbitrage (Pro+)
        result = client.arbitrage.find()
        for opp in result.data:
            print(f"{opp.question}: {opp.potential_return}")

        # Check your usage
        key_info = client.keys.me()
        print(f"Plan: {key_info.data.plan}")
    """

    markets: SyncMarkets
    """List and search prediction markets."""

    categories: SyncCategories
    """List market categories."""

    arbitrage: SyncArbitrage
    """Find cross-platform arbitrage opportunities (Pro+)."""

    unusual_trades: SyncUnusualTrades
    """Detect unusual trading activity (Pro+)."""

    history: SyncHistory
    """Access historical market snapshots (Business+)."""

    keys: SyncKeys
    """Get API key info and usage statistics."""

    ticker: SyncTicker
    """Public market ticker (no auth required)."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.markets = SyncMarkets(self)
        self.categories = SyncCategories(self)
        self.arbitrage = SyncArbitrage(self)
        self.unusual_trades = SyncUnusualTrades(self)
        self.history = SyncHistory(self)
        self.keys = SyncKeys(self)
        self.ticker = SyncTicker(self)


class AsyncPropheseer(BaseAsyncClient):
    """Asynchronous Propheseer SDK client for the prediction markets API.

    Args:
        api_key: API key for authentication.
            Falls back to the ``PROPHESEER_API_KEY`` environment variable.
        base_url: Base URL for the API (default: ``https://api.propheseer.com``).
        timeout: Request timeout in seconds (default: 30).
        max_retries: Maximum number of retries on retryable errors (default: 2).

    Example::

        import asyncio
        from propheseer import AsyncPropheseer

        async def main():
            async with AsyncPropheseer(api_key="pk_test_...") as client:
                page = await client.markets.list(source="polymarket")
                for market in page.data:
                    print(market.question)

        asyncio.run(main())
    """

    markets: AsyncMarkets
    """List and search prediction markets."""

    categories: AsyncCategories
    """List market categories."""

    arbitrage: AsyncArbitrage
    """Find cross-platform arbitrage opportunities (Pro+)."""

    unusual_trades: AsyncUnusualTrades
    """Detect unusual trading activity (Pro+)."""

    history: AsyncHistory
    """Access historical market snapshots (Business+)."""

    keys: AsyncKeys
    """Get API key info and usage statistics."""

    ticker: AsyncTicker
    """Public market ticker (no auth required)."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.markets = AsyncMarkets(self)
        self.categories = AsyncCategories(self)
        self.arbitrage = AsyncArbitrage(self)
        self.unusual_trades = AsyncUnusualTrades(self)
        self.history = AsyncHistory(self)
        self.keys = AsyncKeys(self)
        self.ticker = AsyncTicker(self)
