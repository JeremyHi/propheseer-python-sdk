"""Arbitrage type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from propheseer._base_client import _transform_keys


@dataclass
class ArbitrageMarket:
    """A market involved in an arbitrage opportunity.

    Attributes:
        source: Source platform.
        yes_price: Yes price (probability).
        url: URL to the market.
    """

    source: str
    yes_price: float
    url: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArbitrageMarket":
        """Create an ArbitrageMarket from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            source=transformed.get("source", ""),
            yes_price=transformed.get("yes_price", 0.0),
            url=transformed.get("url", ""),
        )


@dataclass
class ArbitrageOpportunity:
    """An arbitrage opportunity across platforms.

    Attributes:
        question: The market question.
        spread: Price spread between platforms (decimal).
        potential_return: Potential return percentage (e.g. "5.2%").
        markets: Markets involved in the opportunity.
    """

    question: str
    spread: float
    potential_return: str
    markets: List[ArbitrageMarket] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArbitrageOpportunity":
        """Create an ArbitrageOpportunity from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        markets_raw = transformed.get("markets", [])
        markets = [ArbitrageMarket.from_dict(m) for m in markets_raw]
        return cls(
            question=transformed.get("question", ""),
            spread=transformed.get("spread", 0.0),
            potential_return=transformed.get("potential_return", ""),
            markets=markets,
        )


@dataclass
class ArbitrageFindParams:
    """Parameters for finding arbitrage opportunities.

    Attributes:
        min_spread: Minimum spread to include (default: 0.03).
        category: Filter by category.
    """

    min_spread: Optional[float] = None
    category: Optional[str] = None
