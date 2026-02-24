"""API key type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from propheseer._base_client import _transform_keys


@dataclass
class KeyUsage:
    """API key usage statistics.

    Attributes:
        daily: Requests made today.
        minute: Requests made this minute.
        total: Total requests ever.
    """

    daily: int
    minute: int
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyUsage":
        """Create from a dictionary."""
        return cls(
            daily=data.get("daily", 0),
            minute=data.get("minute", 0),
            total=data.get("total", 0),
        )


@dataclass
class UsageHistoryEntry:
    """Daily usage history entry.

    Attributes:
        date: Date (YYYY-MM-DD).
        count: Number of requests.
    """

    date: str
    count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageHistoryEntry":
        """Create from a dictionary."""
        return cls(
            date=data.get("date", ""),
            count=data.get("count", 0),
        )


@dataclass
class PlanLimits:
    """Plan rate limits.

    Attributes:
        requests_per_day: Maximum requests per day.
        requests_per_minute: Maximum requests per minute.
    """

    requests_per_day: int
    requests_per_minute: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanLimits":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            requests_per_day=transformed.get("requests_per_day", 0),
            requests_per_minute=transformed.get("requests_per_minute", 0),
        )


@dataclass
class KeyInfo:
    """Information about the current API key.

    Attributes:
        id: Key ID.
        name: Key name.
        plan: Plan name.
        limits: Rate limits for the plan.
        usage: Current usage.
        history: Daily usage history.
        created_at: When the key was created (ISO 8601).
        last_used_at: When the key was last used (ISO 8601, may be None).
    """

    id: str
    name: str
    plan: str
    limits: PlanLimits
    usage: KeyUsage
    history: List[UsageHistoryEntry]
    created_at: str
    last_used_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyInfo":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        limits_raw = transformed.get("limits", {})
        usage_raw = transformed.get("usage", {})
        history_raw = transformed.get("history", [])
        return cls(
            id=transformed.get("id", ""),
            name=transformed.get("name", ""),
            plan=transformed.get("plan", ""),
            limits=PlanLimits.from_dict(limits_raw),
            usage=KeyUsage.from_dict(usage_raw),
            history=[UsageHistoryEntry.from_dict(h) for h in history_raw],
            created_at=transformed.get("created_at", ""),
            last_used_at=transformed.get("last_used_at"),
        )
