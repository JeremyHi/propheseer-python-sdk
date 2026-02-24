"""Tests for the arbitrage resource."""

from __future__ import annotations

import httpx
import pytest
import respx

from propheseer import Propheseer, AsyncPropheseer, PermissionDeniedError
from tests.conftest import MOCK_ARBITRAGE_OPPORTUNITY


class TestSyncArbitrage:
    """Tests for the synchronous arbitrage resource."""

    @respx.mock
    def test_find_returns_arbitrage_opportunities(self, client: Propheseer) -> None:
        respx.get("https://api.propheseer.com/v1/arbitrage").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [MOCK_ARBITRAGE_OPPORTUNITY],
                    "meta": {"total": 1},
                },
            )
        )

        result = client.arbitrage.find()

        assert len(result.data) == 1
        assert result.data[0].spread == 0.05
        assert result.data[0].potential_return == "5.3%"
        assert len(result.data[0].markets) == 2
        assert result.data[0].markets[0].source == "polymarket"
        assert result.data[0].markets[0].yes_price == 0.65
        assert result.data[0].markets[1].source == "kalshi"
        assert result.data[0].markets[1].yes_price == 0.60

    @respx.mock
    def test_find_passes_min_spread_parameter(self, client: Propheseer) -> None:
        route = respx.get("https://api.propheseer.com/v1/arbitrage").mock(
            return_value=httpx.Response(
                200,
                json={"data": [], "meta": {"total": 0}},
            )
        )

        client.arbitrage.find(min_spread=0.10)

        request = route.calls[0].request
        url = str(request.url)
        assert "min_spread=0.1" in url

    @respx.mock
    def test_find_passes_category_parameter(self, client: Propheseer) -> None:
        route = respx.get("https://api.propheseer.com/v1/arbitrage").mock(
            return_value=httpx.Response(
                200,
                json={"data": [], "meta": {"total": 0}},
            )
        )

        client.arbitrage.find(category="politics")

        request = route.calls[0].request
        url = str(request.url)
        assert "category=politics" in url

    @respx.mock
    def test_throws_permission_denied_for_free_plan(
        self, client: Propheseer
    ) -> None:
        respx.get("https://api.propheseer.com/v1/arbitrage").mock(
            return_value=httpx.Response(
                403,
                json={
                    "error": "Arbitrage detection requires a Pro or Business plan",
                    "code": "PLAN_UPGRADE_REQUIRED",
                    "requiredPlan": "pro",
                },
            )
        )

        with pytest.raises(PermissionDeniedError) as exc_info:
            client.arbitrage.find()

        assert exc_info.value.required_plan == "pro"
        assert exc_info.value.status == 403


class TestAsyncArbitrage:
    """Tests for the asynchronous arbitrage resource."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_find_returns_arbitrage_opportunities(
        self, async_client: AsyncPropheseer
    ) -> None:
        respx.get("https://api.propheseer.com/v1/arbitrage").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [MOCK_ARBITRAGE_OPPORTUNITY],
                    "meta": {"total": 1},
                },
            )
        )

        result = await async_client.arbitrage.find()

        assert len(result.data) == 1
        assert result.data[0].spread == 0.05
        assert result.data[0].potential_return == "5.3%"

    @respx.mock
    @pytest.mark.asyncio
    async def test_throws_permission_denied_for_free_plan(
        self, async_client: AsyncPropheseer
    ) -> None:
        respx.get("https://api.propheseer.com/v1/arbitrage").mock(
            return_value=httpx.Response(
                403,
                json={
                    "error": "Arbitrage detection requires a Pro or Business plan",
                    "code": "PLAN_UPGRADE_REQUIRED",
                    "requiredPlan": "pro",
                },
            )
        )

        with pytest.raises(PermissionDeniedError) as exc_info:
            await async_client.arbitrage.find()

        assert exc_info.value.required_plan == "pro"
