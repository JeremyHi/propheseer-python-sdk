"""Market type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from propheseer._base_client import _transform_keys

MarketSource = Literal["polymarket", "kalshi", "gemini"]
MarketStatus = Literal["open", "closed", "settled"]
MarketCategory = Literal[
    "politics", "sports", "finance", "entertainment", "science", "other"
]


@dataclass
class Outcome:
    """An outcome within a prediction market.

    Attributes:
        name: Outcome name (e.g. "Yes", "No", "Donald Trump").
        probability: Probability as a decimal between 0 and 1.
        volume_24h: 24-hour trading volume (None if unavailable).
    """

    name: str
    probability: float
    volume_24h: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outcome":
        """Create an Outcome from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            name=transformed.get("name", ""),
            probability=transformed.get("probability", 0.0),
            volume_24h=transformed.get("volume_24h"),
        )


@dataclass
class Market:
    """A normalized prediction market from any supported platform.

    Attributes:
        id: Unique market ID (prefixed: pm_, ks_, gm_).
        source: Source platform.
        source_id: Original ID on the source platform.
        question: The market question.
        description: Market description (may be None).
        category: Normalized category.
        status: Market status.
        outcomes: Available outcomes with probabilities.
        resolution_date: Expected resolution date (ISO 8601, may be None).
        created_at: When the market was created (ISO 8601).
        updated_at: When the market was last updated (ISO 8601).
        url: URL to the market on its source platform.
        image_url: Market image URL (may be None).
        tags: Tags from the source platform.
    """

    id: str
    source: str
    source_id: str
    question: str
    description: Optional[str]
    category: str
    status: str
    outcomes: List[Outcome]
    resolution_date: Optional[str]
    created_at: str
    updated_at: str
    url: str
    image_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Market":
        """Create a Market from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        outcomes_raw = transformed.get("outcomes", [])
        outcomes = [Outcome.from_dict(o) for o in outcomes_raw]
        return cls(
            id=transformed.get("id", ""),
            source=transformed.get("source", ""),
            source_id=transformed.get("source_id", ""),
            question=transformed.get("question", ""),
            description=transformed.get("description"),
            category=transformed.get("category", "other"),
            status=transformed.get("status", "open"),
            outcomes=outcomes,
            resolution_date=transformed.get("resolution_date"),
            created_at=transformed.get("created_at", ""),
            updated_at=transformed.get("updated_at", ""),
            url=transformed.get("url", ""),
            image_url=transformed.get("image_url"),
            tags=transformed.get("tags", []),
        )


@dataclass
class MarketListParams:
    """Parameters for listing markets.

    Attributes:
        source: Filter by source platform.
        category: Filter by category.
        status: Filter by status.
        q: Search query string.
        limit: Maximum results per page (default: 50, max: 200).
        offset: Offset for pagination (default: 0).
    """

    source: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    q: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
