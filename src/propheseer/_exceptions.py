"""Exception hierarchy for the Propheseer SDK.

All API errors are raised as subclasses of :class:`PropheseerError`.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class PropheseerError(Exception):
    """Base error class for all Propheseer SDK errors.

    Attributes:
        message: Human-readable error description.
        status: HTTP status code (if applicable).
        code: Machine-readable error code from the API.
        headers: Response headers (if available).
    """

    message: str
    status: Optional[int]
    code: Optional[str]
    headers: Optional[Dict[str, str]]

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.headers = headers

    def __repr__(self) -> str:
        attrs = [f"message={self.message!r}"]
        if self.status is not None:
            attrs.append(f"status={self.status}")
        if self.code is not None:
            attrs.append(f"code={self.code!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class AuthenticationError(PropheseerError):
    """Thrown when the API key is missing or invalid (HTTP 401)."""

    def __init__(
        self,
        message: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            message,
            status=401,
            code="UNAUTHORIZED",
            headers=headers,
        )


class InsufficientCreditsError(PropheseerError):
    """Thrown when the user has insufficient credits (HTTP 402).

    Attributes:
        balance_cents: Current balance in cents.
        required_cents: Required amount in cents.
    """

    balance_cents: Optional[int]
    required_cents: Optional[int]

    def __init__(
        self,
        message: str,
        *,
        balance_cents: Optional[int] = None,
        required_cents: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            message,
            status=402,
            code="INSUFFICIENT_CREDITS",
            headers=headers,
        )
        self.balance_cents = balance_cents
        self.required_cents = required_cents


class PermissionDeniedError(PropheseerError):
    """Thrown when the user lacks permission for the requested resource (HTTP 403).

    Attributes:
        required_plan: Plan required to access the resource.
    """

    required_plan: Optional[str]

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        required_plan: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            message,
            status=403,
            code=code or "FORBIDDEN",
            headers=headers,
        )
        self.required_plan = required_plan


class NotFoundError(PropheseerError):
    """Thrown when the requested resource is not found (HTTP 404)."""

    def __init__(
        self,
        message: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            message,
            status=404,
            code="NOT_FOUND",
            headers=headers,
        )


class RateLimitError(PropheseerError):
    """Thrown when rate limits are exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying.
    """

    retry_after: Optional[int]

    def __init__(
        self,
        message: str,
        *,
        retry_after: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            message,
            status=429,
            code="RATE_LIMITED",
            headers=headers,
        )
        self.retry_after = retry_after


class InternalServerError(PropheseerError):
    """Thrown when the API returns a server error (HTTP 5xx)."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            message,
            status=status or 500,
            code="INTERNAL_ERROR",
            headers=headers,
        )


class APIConnectionError(PropheseerError):
    """Thrown when a network or connection error occurs.

    Attributes:
        cause: The underlying exception that caused the connection error.
    """

    cause: Optional[Exception]

    def __init__(
        self,
        message: str,
        *,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.cause = cause
        self.__cause__ = cause
