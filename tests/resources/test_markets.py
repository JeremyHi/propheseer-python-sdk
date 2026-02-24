"""Tests for the markets resource."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from propheseer import Propheseer, AsyncPropheseer, AuthenticationError
from propheseer._pagination import SyncPage, AsyncPage
from tests.conftest import MOCK_MARKET, RATE_LIMIT_HEADERS


class TestSyncMarkets:
    """Tests for the synchronous markets resource."""

    @respx.mock
    def test_list_returns_page_of_markets(self, client: Propheseer) -> None:
        respx.get("https://api.propheseer.com/v1/markets").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [MOCK_MARKET],
                    "meta": {"total": 1, "limit": 50, "offset": 0},
                },
                headers=RATE_LIMIT_HEADERS,
            )
        )

        page = client.markets.list()

        assert isinstance(page, SyncPage)
        assert len(page.data) == 1
        assert page.data[0].id == "pm_123"
        assert page.data[0].source == "polymarket"
        assert page.data[0].source_id == "123"
        assert page.data[0].question == "Will it rain tomorrow?"
        assert page.data[0].description is None
        assert page.data[0].category == "science"
        assert page.data[0].status == "open"
        assert len(page.data[0].outcomes) == 2
        assert page.data[0].outcomes[0].name == "Yes"
        assert page.data[0].outcomes[0].probability == 0.65
        assert page.data[0].outcomes[0].volume_24h == 50000
        assert page.data[0].url == "https://polymarket.com/event/rain"
        assert page.data[0].image_url is None
        assert page.data[0].tags == ["Weather"]
        assert page.meta.total == 1
        assert page.rate_limit is not None
        assert page.rate_limit.plan == "pro"
        assert page.rate_limit.remaining_day == 9999

    @respx.mock
    def test_list_passes_query_parameters(self, client: Propheseer) -> None:
        route = respx.get("https://api.propheseer.com/v1/markets").mock(
            return_value=httpx.Response(
                200,
                json={"data": [], "meta": {"total": 0, "limit": 10, "offset": 0}},
            )
        )

        client.markets.list(
            source="kalshi",
            category="politics",
            status="open",
            q="election",
            limit=10,
            offset=5,
        )

        request = route.calls[0].request
        url = str(request.url)
        assert "source=kalshi" in url
        assert "category=politics" in url
        assert "status=open" in url
        assert "q=election" in url
        assert "limit=10" in url
        assert "offset=5" in url

    @respx.mock
    def test_get_returns_single_market(self, client: Propheseer) -> None:
        respx.get("https://api.propheseer.com/v1/markets/pm_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": MOCK_MARKET},
            )
        )

        result = client.markets.get("pm_123")

        assert result.data.id == "pm_123"
        assert result.data.question == "Will it rain tomorrow?"

    @respx.mock
    def test_get_encodes_market_id(self, client: Propheseer) -> None:
        route = respx.get(
            "https://api.propheseer.com/v1/markets/pm_special%2Fid"
        ).mock(
            return_value=httpx.Response(200, json={"data": MOCK_MARKET})
        )

        client.markets.get("pm_special/id")

        assert route.called

    @respx.mock
    def test_list_auto_paginate(self, client: Propheseer) -> None:
        # Page 1
        respx.get(
            "https://api.propheseer.com/v1/markets",
            params__contains={"offset": "0"},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [MOCK_MARKET],
                    "meta": {"total": 2, "limit": 1, "offset": 0},
                },
            )
        )
        # Page 2
        market2 = {**MOCK_MARKET, "id": "pm_456", "question": "Will it snow?"}
        respx.get(
            "https://api.propheseer.com/v1/markets",
            params__contains={"offset": "1"},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [market2],
                    "meta": {"total": 2, "limit": 1, "offset": 1},
                },
            )
        )

        results = list(client.markets.list_auto_paginate(limit=1))

        assert len(results) == 2
        assert results[0].id == "pm_123"
        assert results[1].id == "pm_456"

    @respx.mock
    def test_list_auto_paginate_max_items(self, client: Propheseer) -> None:
        respx.get("https://api.propheseer.com/v1/markets").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [MOCK_MARKET, {**MOCK_MARKET, "id": "pm_456"}],
                    "meta": {"total": 10, "limit": 2, "offset": 0},
                },
            )
        )

        results = list(client.markets.list_auto_paginate(limit=2, max_items=1))

        assert len(results) == 1

    def test_list_throws_auth_error_without_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("PROPHESEER_API_KEY", raising=False)
        client = Propheseer()
        with pytest.raises(AuthenticationError):
            client.markets.list()


class TestAsyncMarkets:
    """Tests for the asynchronous markets resource."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_returns_async_page(
        self, async_client: AsyncPropheseer
    ) -> None:
        respx.get("https://api.propheseer.com/v1/markets").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [MOCK_MARKET],
                    "meta": {"total": 1, "limit": 50, "offset": 0},
                },
                headers=RATE_LIMIT_HEADERS,
            )
        )

        page = await async_client.markets.list()

        assert isinstance(page, AsyncPage)
        assert len(page.data) == 1
        assert page.data[0].id == "pm_123"
        assert page.data[0].source_id == "123"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_returns_single_market(
        self, async_client: AsyncPropheseer
    ) -> None:
        respx.get("https://api.propheseer.com/v1/markets/pm_123").mock(
            return_value=httpx.Response(200, json={"data": MOCK_MARKET})
        )

        result = await async_client.markets.get("pm_123")

        assert result.data.id == "pm_123"
        assert result.data.question == "Will it rain tomorrow?"

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_auto_paginate(
        self, async_client: AsyncPropheseer
    ) -> None:
        respx.get(
            "https://api.propheseer.com/v1/markets",
            params__contains={"offset": "0"},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [MOCK_MARKET],
                    "meta": {"total": 2, "limit": 1, "offset": 0},
                },
            )
        )
        market2 = {**MOCK_MARKET, "id": "pm_456"}
        respx.get(
            "https://api.propheseer.com/v1/markets",
            params__contains={"offset": "1"},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [market2],
                    "meta": {"total": 2, "limit": 1, "offset": 1},
                },
            )
        )

        results = []
        async for market in async_client.markets.list_auto_paginate(limit=1):
            results.append(market)

        assert len(results) == 2
        assert results[0].id == "pm_123"
        assert results[1].id == "pm_456"
