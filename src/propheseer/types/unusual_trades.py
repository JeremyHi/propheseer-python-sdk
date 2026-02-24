"""Unusual trade type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from propheseer._base_client import _transform_keys

DetectionReason = Literal[
    "potential_insider", "high_amount", "new_wallet", "near_resolution"
]
TradeSide = Literal["BUY", "SELL"]


@dataclass
class UnusualTradeMarket:
    """Market information associated with an unusual trade.

    Attributes:
        id: Market ID.
        question: Market question.
        source: Source platform.
        end_date: Market end date (may be None).
        url: URL to the market.
        tags: Tags from the platform.
        image_url: Market image URL.
    """

    id: str
    question: str
    source: str
    end_date: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnusualTradeMarket":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            id=transformed.get("id", ""),
            question=transformed.get("question", ""),
            source=transformed.get("source", ""),
            end_date=transformed.get("end_date"),
            url=transformed.get("url"),
            tags=transformed.get("tags", []),
            image_url=transformed.get("image_url"),
        )


@dataclass
class TradeDetails:
    """Details of the flagged trade.

    Attributes:
        wallet_address: Trader's wallet address.
        side: Buy or sell.
        size: Trade size (contracts).
        price: Trade price.
        usdc_value: USDC value of the trade.
        timestamp: When the trade occurred (ISO 8601).
        transaction_hash: On-chain transaction hash.
    """

    wallet_address: str
    side: str
    size: float
    price: float
    usdc_value: float
    timestamp: str
    transaction_hash: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeDetails":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            wallet_address=transformed.get("wallet_address", ""),
            side=transformed.get("side", ""),
            size=transformed.get("size", 0),
            price=transformed.get("price", 0.0),
            usdc_value=transformed.get("usdc_value", 0.0),
            timestamp=transformed.get("timestamp", ""),
            transaction_hash=transformed.get("transaction_hash", ""),
        )


@dataclass
class DetectionContext:
    """Market context for the detection.

    Attributes:
        market_avg_size: Average trade size in this market.
        market_std_dev: Standard deviation of trade sizes.
    """

    market_avg_size: float
    market_std_dev: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectionContext":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            market_avg_size=transformed.get("market_avg_size", 0.0),
            market_std_dev=transformed.get("market_std_dev", 0.0),
        )


@dataclass
class DetectionInfo:
    """Why the trade was flagged.

    Attributes:
        reason: Detection reason.
        anomaly_score: Anomaly score (0-100).
        context: Market context for the detection.
    """

    reason: str
    anomaly_score: float
    context: DetectionContext

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectionInfo":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        context_raw = transformed.get("context", {})
        return cls(
            reason=transformed.get("reason", ""),
            anomaly_score=transformed.get("anomaly_score", 0.0),
            context=DetectionContext.from_dict(context_raw),
        )


@dataclass
class UnusualTrade:
    """An unusual trade detected by the system.

    Attributes:
        id: Trade ID.
        market: Associated market.
        trade: Trade details.
        detection: Detection information.
        detected_at: When the trade was detected (ISO 8601).
    """

    id: str
    market: UnusualTradeMarket
    trade: TradeDetails
    detection: DetectionInfo
    detected_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnusualTrade":
        """Create from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            id=transformed.get("id", ""),
            market=UnusualTradeMarket.from_dict(transformed.get("market", {})),
            trade=TradeDetails.from_dict(transformed.get("trade", {})),
            detection=DetectionInfo.from_dict(transformed.get("detection", {})),
            detected_at=transformed.get("detected_at", ""),
        )


@dataclass
class UnusualTradeListParams:
    """Parameters for listing unusual trades.

    Attributes:
        limit: Maximum results per page (default: 50, max: 100).
        offset: Offset for pagination.
        market_id: Filter by market ID.
        reason: Filter by detection reason.
        min_score: Minimum anomaly score.
        since: Only trades since this date (ISO 8601).
        side: Filter by trade side.
        source: Filter by source platform.
        exclude_categories: Categories to exclude (comma-separated).
    """

    limit: Optional[int] = None
    offset: Optional[int] = None
    market_id: Optional[str] = None
    reason: Optional[str] = None
    min_score: Optional[float] = None
    since: Optional[str] = None
    side: Optional[str] = None
    source: Optional[str] = None
    exclude_categories: Optional[str] = None
