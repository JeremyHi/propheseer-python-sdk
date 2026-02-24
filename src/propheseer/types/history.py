"""History type definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from propheseer._base_client import _transform_keys


@dataclass
class MarketHistoryEntry:
    """A historical market snapshot.

    Attributes:
        market_id: Market ID.
        snapshot_date: Snapshot date (YYYY-MM-DD).
        data: The full snapshot data (varies by endpoint).
    """

    market_id: str
    snapshot_date: str
    data: Dict[str, Any]

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "MarketHistoryEntry":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(raw)
        return cls(
            market_id=transformed.get("market_id", ""),
            snapshot_date=transformed.get("snapshot_date", ""),
            data=transformed,
        )


@dataclass
class HistoryListParams:
    """Parameters for listing market history.

    Attributes:
        market_id: Filter by specific market ID.
        source: Filter by source platform.
        category: Filter by category.
        days: Number of days of history (default: 30).
        limit: Maximum results (default: 1000).
    """

    market_id: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    days: Optional[int] = None
    limit: Optional[int] = None


@dataclass
class SnapshotDate:
    """A date with available snapshot data.

    Attributes:
        date: Date string (YYYY-MM-DD).
        count: Number of markets captured.
    """

    date: str
    count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SnapshotDate":
        """Create from a dictionary."""
        return cls(
            date=data.get("date", ""),
            count=data.get("count", 0),
        )
