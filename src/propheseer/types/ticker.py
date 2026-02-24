"""Ticker type definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from propheseer._base_client import _transform_keys


@dataclass
class TickerItem:
    """A simplified market item for the ticker.

    Attributes:
        id: Market ID.
        question: Market question.
        probability: Primary outcome probability.
        source: Source platform.
    """

    id: str
    question: str
    probability: float
    source: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TickerItem":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            id=transformed.get("id", ""),
            question=transformed.get("question", ""),
            probability=transformed.get("probability", 0.0),
            source=transformed.get("source", ""),
        )


@dataclass
class TickerListParams:
    """Parameters for listing ticker items.

    Attributes:
        limit: Maximum items (default: 12, max: 20).
    """

    limit: Optional[int] = None
