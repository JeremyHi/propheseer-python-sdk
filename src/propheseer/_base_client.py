"""Base HTTP client with retry logic, rate limit parsing, and error mapping."""

from __future__ import annotations

import os
import random
import re
import time
from typing import Any, Dict, Optional, Tuple, Type, Union

import httpx

from propheseer._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    VERSION,
)
from propheseer._exceptions import (
    APIConnectionError,
    AuthenticationError,
    InsufficientCreditsError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    PropheseerError,
    RateLimitError,
)
from propheseer._response import RateLimitInfo, parse_rate_limit_headers


# ---------- camelCase -> snake_case conversion ----------

_CAMEL_RE_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
_CAMEL_RE_2 = re.compile(r"([a-z0-9])([A-Z])")
_DIGIT_BOUNDARY_RE = re.compile(r"([a-z])(\d)")


def _camel_to_snake(name: str) -> str:
    """Convert a camelCase or PascalCase string to snake_case.

    Handles special cases like ``volume24h`` -> ``volume_24h``
    and ``sourceId`` -> ``source_id``.
    """
    s = _CAMEL_RE_1.sub(r"\1_\2", name)
    s = _CAMEL_RE_2.sub(r"\1_\2", s)
    s = _DIGIT_BOUNDARY_RE.sub(r"\1_\2", s)
    return s.lower()


def _transform_keys(obj: Any) -> Any:
    """Recursively transform all dictionary keys from camelCase to snake_case."""
    if isinstance(obj, dict):
        return {_camel_to_snake(k): _transform_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_transform_keys(item) for item in obj]
    return obj


# ---------- Error mapping ----------


def _is_retryable(status_code: int) -> bool:
    """Whether this HTTP status should trigger a retry."""
    return status_code == 429 or status_code >= 500


def _map_status_to_error(
    status_code: int,
    body: Dict[str, Any],
    headers: httpx.Headers,
) -> PropheseerError:
    """Map an HTTP status code to the appropriate error class."""
    message = body.get("error") or body.get("message") or f"API error: {status_code}"
    header_dict = dict(headers.items())

    if status_code == 401:
        return AuthenticationError(message, headers=header_dict)
    if status_code == 402:
        return InsufficientCreditsError(
            message,
            balance_cents=body.get("balanceCents"),
            required_cents=body.get("requiredCents"),
            headers=header_dict,
        )
    if status_code == 403:
        return PermissionDeniedError(
            message,
            code=body.get("code"),
            required_plan=body.get("requiredPlan"),
            headers=header_dict,
        )
    if status_code == 404:
        return NotFoundError(message, headers=header_dict)
    if status_code == 429:
        return RateLimitError(
            message,
            retry_after=body.get("retryAfter"),
            headers=header_dict,
        )
    if status_code >= 500:
        return InternalServerError(
            message,
            status=status_code,
            headers=header_dict,
        )
    return PropheseerError(
        message,
        status=status_code,
        code=body.get("code"),
        headers=header_dict,
    )


# ---------- Retry delay ----------


def _get_retry_delay(attempt: int, last_error: Optional[Exception] = None) -> float:
    """Calculate the retry delay with exponential backoff and jitter.

    Args:
        attempt: The retry attempt number (1-based).
        last_error: The previous error, used to check for retryAfter on 429.

    Returns:
        Delay in seconds.
    """
    if isinstance(last_error, RateLimitError) and last_error.retry_after:
        return float(last_error.retry_after)

    # Exponential backoff: 0.5s, 1s, 2s, ...
    base_delay: float = 0.5 * (2 ** (attempt - 1))
    jitter: float = random.random() * base_delay * 0.5
    return base_delay + jitter


# ---------- Base clients ----------


class _RequestConfig:
    """Internal request configuration."""

    __slots__ = ("method", "path", "query", "body", "auth")

    def __init__(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
        auth: bool = True,
    ) -> None:
        self.method = method
        self.path = path
        self.query = query
        self.body = body
        self.auth = auth


class BaseSyncClient:
    """Synchronous base HTTP client with retry logic, rate limit parsing,
    and error mapping.

    Args:
        api_key: API key for authentication.
            Falls back to the ``PROPHESEER_API_KEY`` environment variable.
        base_url: Base URL for the API.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on retryable errors.
    """

    api_key: Optional[str]
    base_url: str
    timeout: float
    max_retries: int

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("PROPHESEER_API_KEY")
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        self._client = httpx.Client(timeout=self.timeout)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "BaseSyncClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
        auth: bool = True,
    ) -> Tuple[Any, Optional[RateLimitInfo], httpx.Response]:
        """Make an authenticated API request with retry and error handling.

        Returns:
            A tuple of (parsed JSON data, rate limit info, raw response).
        """
        if auth and not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass it to the constructor "
                "or set the PROPHESEER_API_KEY environment variable."
            )

        url = self._build_url(path, query)
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": f"propheseer-python/{VERSION}",
        }
        if auth and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                delay = _get_retry_delay(attempt, last_error)
                time.sleep(delay)

            try:
                response = self._client.request(
                    method,
                    url,
                    headers=headers,
                    json=body if body is not None else None,
                )

                if response.is_success:
                    data = response.json()
                    rate_limit = parse_rate_limit_headers(response.headers)
                    return data, rate_limit, response

                # Parse error body
                error_body: Dict[str, Any] = {}
                try:
                    error_body = response.json()
                except Exception:
                    pass

                error = _map_status_to_error(
                    response.status_code, error_body, response.headers
                )

                if _is_retryable(response.status_code) and attempt < self.max_retries:
                    last_error = error
                    continue

                raise error

            except PropheseerError:
                raise
            except httpx.TimeoutException as exc:
                timeout_error = APIConnectionError(
                    f"Request timed out after {self.timeout}s",
                    cause=exc,
                )
                if attempt < self.max_retries:
                    last_error = timeout_error
                    continue
                raise timeout_error
            except httpx.HTTPError as exc:
                conn_error = APIConnectionError(
                    f"Connection error: {exc}",
                    cause=exc,
                )
                if attempt < self.max_retries:
                    last_error = conn_error
                    continue
                raise conn_error

        raise last_error or PropheseerError("Request failed after retries")

    def _build_url(
        self,
        path: str,
        query: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a full URL from a path and optional query parameters."""
        url = f"{self.base_url}{path}"
        if query:
            params = {
                k: str(v)
                for k, v in query.items()
                if v is not None
            }
            if params:
                qs = "&".join(f"{k}={v}" for k, v in params.items())
                url = f"{url}?{qs}"
        return url


class BaseAsyncClient:
    """Asynchronous base HTTP client with retry logic, rate limit parsing,
    and error mapping.

    Args:
        api_key: API key for authentication.
            Falls back to the ``PROPHESEER_API_KEY`` environment variable.
        base_url: Base URL for the API.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on retryable errors.
    """

    api_key: Optional[str]
    base_url: str
    timeout: float
    max_retries: int

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("PROPHESEER_API_KEY")
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "BaseAsyncClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
        auth: bool = True,
    ) -> Tuple[Any, Optional[RateLimitInfo], httpx.Response]:
        """Make an authenticated async API request with retry and error handling.

        Returns:
            A tuple of (parsed JSON data, rate limit info, raw response).
        """
        import asyncio

        if auth and not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass it to the constructor "
                "or set the PROPHESEER_API_KEY environment variable."
            )

        url = self._build_url(path, query)
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": f"propheseer-python/{VERSION}",
        }
        if auth and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                delay = _get_retry_delay(attempt, last_error)
                await asyncio.sleep(delay)

            try:
                response = await self._client.request(
                    method,
                    url,
                    headers=headers,
                    json=body if body is not None else None,
                )

                if response.is_success:
                    data = response.json()
                    rate_limit = parse_rate_limit_headers(response.headers)
                    return data, rate_limit, response

                # Parse error body
                error_body: Dict[str, Any] = {}
                try:
                    error_body = response.json()
                except Exception:
                    pass

                error = _map_status_to_error(
                    response.status_code, error_body, response.headers
                )

                if _is_retryable(response.status_code) and attempt < self.max_retries:
                    last_error = error
                    continue

                raise error

            except PropheseerError:
                raise
            except httpx.TimeoutException as exc:
                timeout_error = APIConnectionError(
                    f"Request timed out after {self.timeout}s",
                    cause=exc,
                )
                if attempt < self.max_retries:
                    last_error = timeout_error
                    continue
                raise timeout_error
            except httpx.HTTPError as exc:
                conn_error = APIConnectionError(
                    f"Connection error: {exc}",
                    cause=exc,
                )
                if attempt < self.max_retries:
                    last_error = conn_error
                    continue
                raise conn_error

        raise last_error or PropheseerError("Request failed after retries")

    def _build_url(
        self,
        path: str,
        query: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a full URL from a path and optional query parameters."""
        url = f"{self.base_url}{path}"
        if query:
            params = {
                k: str(v)
                for k, v in query.items()
                if v is not None
            }
            if params:
                qs = "&".join(f"{k}={v}" for k, v in params.items())
                url = f"{url}?{qs}"
        return url
