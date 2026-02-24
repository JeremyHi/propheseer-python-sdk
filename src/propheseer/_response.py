"""API response wrapper with rate limit information."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar

import httpx

T = TypeVar("T")


@dataclass
class RateLimitInfo:
    """Rate limit information extracted from API response headers.

    Attributes:
        plan: User's plan (free, pro, business, etc.).
        billing_type: Billing type: ``"subscription"`` or ``"credits"``.
        limit_day: Daily request limit (subscription billing).
        remaining_day: Remaining daily requests (subscription billing).
        limit_minute: Per-minute request limit (subscription billing).
        remaining_minute: Remaining per-minute requests (subscription billing).
        credit_balance_cents: Credit balance in cents (credit billing).
        credit_balance: Formatted credit balance (credit billing).
        request_cost_cents: Cost of the request in cents (credit billing).
        request_cost: Formatted request cost (credit billing).
    """

    plan: str
    billing_type: str = "subscription"
    limit_day: Optional[int] = None
    remaining_day: Optional[int] = None
    limit_minute: Optional[int] = None
    remaining_minute: Optional[int] = None
    credit_balance_cents: Optional[int] = None
    credit_balance: Optional[str] = None
    request_cost_cents: Optional[int] = None
    request_cost: Optional[str] = None


@dataclass
class APIResponse(Generic[T]):
    """Wrapper for API responses that includes rate limit info.

    Attributes:
        data: The response data.
        rate_limit: Rate limit information from response headers.
        http_response: The raw httpx.Response object.
    """

    data: T
    rate_limit: Optional[RateLimitInfo] = None
    http_response: Optional[httpx.Response] = None


def parse_rate_limit_headers(headers: httpx.Headers) -> Optional[RateLimitInfo]:
    """Parse rate limit information from API response headers.

    Args:
        headers: The HTTP response headers.

    Returns:
        A :class:`RateLimitInfo` object, or ``None`` if no rate limit headers
        are present.
    """
    plan = headers.get("x-ratelimit-plan")
    if not plan:
        return None

    billing_type = headers.get("x-billing-type", "subscription")

    info = RateLimitInfo(plan=plan, billing_type=billing_type)

    if billing_type == "credits":
        balance_cents = headers.get("x-credit-balance-cents")
        if balance_cents is not None:
            info.credit_balance_cents = int(balance_cents)
        credit_balance = headers.get("x-credit-balance")
        if credit_balance is not None:
            info.credit_balance = credit_balance
        cost_cents = headers.get("x-request-cost-cents")
        if cost_cents is not None:
            info.request_cost_cents = int(cost_cents)
        request_cost = headers.get("x-request-cost")
        if request_cost is not None:
            info.request_cost = request_cost
    else:
        limit_day = headers.get("x-ratelimit-limit-day")
        if limit_day is not None:
            info.limit_day = int(limit_day)
        remaining_day = headers.get("x-ratelimit-remaining-day")
        if remaining_day is not None:
            info.remaining_day = int(remaining_day)
        limit_minute = headers.get("x-ratelimit-limit-minute")
        if limit_minute is not None:
            info.limit_minute = int(limit_minute)
        remaining_minute = headers.get("x-ratelimit-remaining-minute")
        if remaining_minute is not None:
            info.remaining_minute = int(remaining_minute)

    return info
