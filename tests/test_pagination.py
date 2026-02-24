"""Tests for pagination utilities."""

from __future__ import annotations

import pytest

from propheseer._pagination import PaginationMeta, SyncPage, AsyncPage


class TestSyncPage:
    def test_has_more_returns_true_when_more_items_exist(self) -> None:
        page = SyncPage(
            ["a", "b"],
            PaginationMeta(total=5, limit=2, offset=0),
            None,
        )
        assert page.has_more() is True

    def test_has_more_returns_false_when_all_items_returned(self) -> None:
        page = SyncPage(
            ["a", "b"],
            PaginationMeta(total=2, limit=2, offset=0),
            None,
        )
        assert page.has_more() is False

    def test_has_more_returns_false_at_last_page(self) -> None:
        page = SyncPage(
            ["e"],
            PaginationMeta(total=5, limit=2, offset=4),
            None,
        )
        assert page.has_more() is False

    def test_next_offset_returns_correct_offset(self) -> None:
        page = SyncPage(
            ["a", "b"],
            PaginationMeta(total=5, limit=2, offset=0),
            None,
        )
        assert page.next_offset() == 2

    def test_next_offset_returns_none_when_no_more_pages(self) -> None:
        page = SyncPage(
            ["a", "b"],
            PaginationMeta(total=2, limit=2, offset=0),
            None,
        )
        assert page.next_offset() is None

    def test_iter(self) -> None:
        page = SyncPage(
            ["a", "b", "c"],
            PaginationMeta(total=3, limit=3, offset=0),
            None,
        )
        assert list(page) == ["a", "b", "c"]

    def test_len(self) -> None:
        page = SyncPage(
            ["a", "b"],
            PaginationMeta(total=5, limit=2, offset=0),
            None,
        )
        assert len(page) == 2

    def test_repr(self) -> None:
        page = SyncPage(
            ["a", "b"],
            PaginationMeta(total=5, limit=2, offset=0),
            None,
        )
        r = repr(page)
        assert "SyncPage" in r
        assert "2 items" in r
        assert "total=5" in r


class TestAsyncPage:
    def test_has_more_returns_true_when_more_items_exist(self) -> None:
        page = AsyncPage(
            ["a", "b"],
            PaginationMeta(total=5, limit=2, offset=0),
            None,
        )
        assert page.has_more() is True

    def test_has_more_returns_false_when_all_items_returned(self) -> None:
        page = AsyncPage(
            ["a", "b"],
            PaginationMeta(total=2, limit=2, offset=0),
            None,
        )
        assert page.has_more() is False

    def test_next_offset(self) -> None:
        page = AsyncPage(
            ["a", "b"],
            PaginationMeta(total=5, limit=2, offset=0),
            None,
        )
        assert page.next_offset() == 2

    def test_sync_iter(self) -> None:
        page = AsyncPage(
            ["a", "b"],
            PaginationMeta(total=2, limit=2, offset=0),
            None,
        )
        assert list(page) == ["a", "b"]

    @pytest.mark.asyncio
    async def test_async_iter(self) -> None:
        page = AsyncPage(
            ["a", "b", "c"],
            PaginationMeta(total=3, limit=3, offset=0),
            None,
        )
        results = []
        async for item in page:
            results.append(item)
        assert results == ["a", "b", "c"]
