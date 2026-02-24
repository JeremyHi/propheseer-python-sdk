"""Shared test fixtures and configuration."""

from __future__ import annotations

import pytest
import respx

from propheseer import Propheseer, AsyncPropheseer


@pytest.fixture
def client() -> Propheseer:
    """Create a sync Propheseer client for testing."""
    return Propheseer(
        api_key="pk_test_123",
        base_url="https://api.propheseer.com",
    )


@pytest.fixture
def async_client() -> AsyncPropheseer:
    """Create an async Propheseer client for testing."""
    return AsyncPropheseer(
        api_key="pk_test_123",
        base_url="https://api.propheseer.com",
    )


MOCK_MARKET = {
    "id": "pm_123",
    "source": "polymarket",
    "sourceId": "123",
    "question": "Will it rain tomorrow?",
    "description": None,
    "category": "science",
    "status": "open",
    "outcomes": [
        {"name": "Yes", "probability": 0.65, "volume24h": 50000},
        {"name": "No", "probability": 0.35, "volume24h": 50000},
    ],
    "resolutionDate": None,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
    "url": "https://polymarket.com/event/rain",
    "imageUrl": None,
    "tags": ["Weather"],
}

MOCK_ARBITRAGE_OPPORTUNITY = {
    "question": "Who will win?",
    "spread": 0.05,
    "potentialReturn": "5.3%",
    "markets": [
        {"source": "polymarket", "yesPrice": 0.65, "url": "https://polymarket.com/..."},
        {"source": "kalshi", "yesPrice": 0.60, "url": "https://kalshi.com/..."},
    ],
}

RATE_LIMIT_HEADERS = {
    "x-ratelimit-plan": "pro",
    "x-billing-type": "subscription",
    "x-ratelimit-limit-day": "10000",
    "x-ratelimit-remaining-day": "9999",
    "x-ratelimit-limit-minute": "100",
    "x-ratelimit-remaining-minute": "98",
}
