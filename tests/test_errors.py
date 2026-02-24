"""Tests for the error class hierarchy."""

from __future__ import annotations

import pytest

from propheseer import (
    PropheseerError,
    AuthenticationError,
    InsufficientCreditsError,
    PermissionDeniedError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
    APIConnectionError,
)


class TestPropheseerError:
    def test_has_correct_properties(self) -> None:
        err = PropheseerError("test error", status=400, code="BAD_REQUEST")
        assert str(err) == "test error"
        assert err.message == "test error"
        assert err.status == 400
        assert err.code == "BAD_REQUEST"
        assert isinstance(err, Exception)

    def test_repr(self) -> None:
        err = PropheseerError("test", status=400, code="BAD")
        assert "PropheseerError" in repr(err)
        assert "400" in repr(err)


class TestAuthenticationError:
    def test_is_401(self) -> None:
        err = AuthenticationError("bad key")
        assert err.status == 401
        assert err.code == "UNAUTHORIZED"
        assert isinstance(err, PropheseerError)
        assert isinstance(err, Exception)

    def test_with_headers(self) -> None:
        err = AuthenticationError("bad key", headers={"x-request-id": "abc"})
        assert err.headers == {"x-request-id": "abc"}


class TestInsufficientCreditsError:
    def test_is_402(self) -> None:
        err = InsufficientCreditsError(
            "no credits",
            balance_cents=50,
            required_cents=100,
        )
        assert err.status == 402
        assert err.balance_cents == 50
        assert err.required_cents == 100
        assert isinstance(err, PropheseerError)


class TestPermissionDeniedError:
    def test_is_403(self) -> None:
        err = PermissionDeniedError("upgrade needed", required_plan="pro")
        assert err.status == 403
        assert err.required_plan == "pro"
        assert isinstance(err, PropheseerError)

    def test_default_code(self) -> None:
        err = PermissionDeniedError("denied")
        assert err.code == "FORBIDDEN"

    def test_custom_code(self) -> None:
        err = PermissionDeniedError("denied", code="PLAN_UPGRADE_REQUIRED")
        assert err.code == "PLAN_UPGRADE_REQUIRED"


class TestNotFoundError:
    def test_is_404(self) -> None:
        err = NotFoundError("not found")
        assert err.status == 404
        assert err.code == "NOT_FOUND"
        assert isinstance(err, PropheseerError)


class TestRateLimitError:
    def test_is_429(self) -> None:
        err = RateLimitError("slow down", retry_after=30)
        assert err.status == 429
        assert err.retry_after == 30
        assert err.code == "RATE_LIMITED"
        assert isinstance(err, PropheseerError)

    def test_no_retry_after(self) -> None:
        err = RateLimitError("slow down")
        assert err.retry_after is None


class TestInternalServerError:
    def test_defaults_to_500(self) -> None:
        err = InternalServerError("server error")
        assert err.status == 500
        assert err.code == "INTERNAL_ERROR"
        assert isinstance(err, PropheseerError)

    def test_accepts_custom_status(self) -> None:
        err = InternalServerError("bad gateway", status=502)
        assert err.status == 502


class TestAPIConnectionError:
    def test_has_no_status(self) -> None:
        cause = ConnectionError("ECONNREFUSED")
        err = APIConnectionError("connection failed", cause=cause)
        assert err.status is None
        assert err.cause is cause
        assert err.__cause__ is cause
        assert isinstance(err, PropheseerError)


class TestErrorHierarchy:
    def test_all_errors_extend_propheseer_error(self) -> None:
        errors = [
            AuthenticationError(""),
            InsufficientCreditsError(""),
            PermissionDeniedError(""),
            NotFoundError(""),
            RateLimitError(""),
            InternalServerError(""),
            APIConnectionError(""),
        ]
        for err in errors:
            assert isinstance(err, PropheseerError)
            assert isinstance(err, Exception)
