"""Shared type definitions used across the SDK."""

from __future__ import annotations

from typing import Literal

# Re-export from _response and _pagination for convenience
from propheseer._response import APIResponse, RateLimitInfo
from propheseer._pagination import PaginationMeta

__all__ = [
    "APIResponse",
    "RateLimitInfo",
    "PaginationMeta",
    "BillingType",
]

BillingType = Literal["subscription", "credits"]
