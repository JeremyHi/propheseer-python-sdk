"""Tests for client creation and configuration."""

from __future__ import annotations

import os

import pytest

from propheseer import Propheseer, AsyncPropheseer, AuthenticationError, VERSION


class TestPropheseerClient:
    """Tests for the synchronous Propheseer client."""

    def test_creates_client_with_api_key(self) -> None:
        client = Propheseer(api_key="pk_test_123")
        assert client.api_key == "pk_test_123"
        assert client.base_url == "https://api.propheseer.com"

    def test_uses_custom_base_url(self) -> None:
        client = Propheseer(
            api_key="pk_test_123",
            base_url="http://localhost:3000",
        )
        assert client.base_url == "http://localhost:3000"

    def test_strips_trailing_slash_from_base_url(self) -> None:
        client = Propheseer(
            api_key="pk_test_123",
            base_url="http://localhost:3000/",
        )
        assert client.base_url == "http://localhost:3000"

    def test_has_all_resource_namespaces(self) -> None:
        client = Propheseer(api_key="pk_test_123")
        assert client.markets is not None
        assert client.categories is not None
        assert client.arbitrage is not None
        assert client.unusual_trades is not None
        assert client.history is not None
        assert client.keys is not None
        assert client.ticker is not None

    def test_uses_default_timeout_and_retries(self) -> None:
        client = Propheseer(api_key="pk_test_123")
        assert client.timeout == 30.0
        assert client.max_retries == 2

    def test_allows_custom_timeout_and_retries(self) -> None:
        client = Propheseer(
            api_key="pk_test_123",
            timeout=10.0,
            max_retries=5,
        )
        assert client.timeout == 10.0
        assert client.max_retries == 5

    def test_reads_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PROPHESEER_API_KEY", "pk_env_key")
        client = Propheseer()
        assert client.api_key == "pk_env_key"

    def test_explicit_api_key_overrides_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("PROPHESEER_API_KEY", "pk_env_key")
        client = Propheseer(api_key="pk_explicit")
        assert client.api_key == "pk_explicit"

    def test_no_api_key_creates_client(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("PROPHESEER_API_KEY", raising=False)
        client = Propheseer()
        assert client.api_key is None

    def test_context_manager(self) -> None:
        with Propheseer(api_key="pk_test_123") as client:
            assert client.api_key == "pk_test_123"

    def test_version_is_set(self) -> None:
        assert VERSION == "0.1.0"


class TestAsyncPropheseerClient:
    """Tests for the asynchronous Propheseer client."""

    def test_creates_async_client_with_api_key(self) -> None:
        client = AsyncPropheseer(api_key="pk_test_123")
        assert client.api_key == "pk_test_123"
        assert client.base_url == "https://api.propheseer.com"

    def test_has_all_resource_namespaces(self) -> None:
        client = AsyncPropheseer(api_key="pk_test_123")
        assert client.markets is not None
        assert client.categories is not None
        assert client.arbitrage is not None
        assert client.unusual_trades is not None
        assert client.history is not None
        assert client.keys is not None
        assert client.ticker is not None

    def test_uses_default_timeout_and_retries(self) -> None:
        client = AsyncPropheseer(api_key="pk_test_123")
        assert client.timeout == 30.0
        assert client.max_retries == 2
