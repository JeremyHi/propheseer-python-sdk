"""Type definitions for the Propheseer SDK."""

from propheseer.types.shared import APIResponse, RateLimitInfo, PaginationMeta

from propheseer.types.markets import (
    Market,
    Outcome,
    MarketSource,
    MarketStatus,
    MarketCategory,
    MarketListParams,
)

from propheseer.types.categories import Category

from propheseer.types.arbitrage import (
    ArbitrageOpportunity,
    ArbitrageMarket,
    ArbitrageFindParams,
)

from propheseer.types.unusual_trades import (
    UnusualTrade,
    UnusualTradeMarket,
    TradeDetails,
    DetectionInfo,
    DetectionContext,
    DetectionReason,
    TradeSide,
    UnusualTradeListParams,
)

from propheseer.types.history import (
    MarketHistoryEntry,
    HistoryListParams,
    SnapshotDate,
)

from propheseer.types.keys import (
    KeyInfo,
    KeyUsage,
    UsageHistoryEntry,
    PlanLimits,
)

from propheseer.types.ticker import TickerItem, TickerListParams

__all__ = [
    # Shared
    "APIResponse",
    "RateLimitInfo",
    "PaginationMeta",
    # Markets
    "Market",
    "Outcome",
    "MarketSource",
    "MarketStatus",
    "MarketCategory",
    "MarketListParams",
    # Categories
    "Category",
    # Arbitrage
    "ArbitrageOpportunity",
    "ArbitrageMarket",
    "ArbitrageFindParams",
    # Unusual Trades
    "UnusualTrade",
    "UnusualTradeMarket",
    "TradeDetails",
    "DetectionInfo",
    "DetectionContext",
    "DetectionReason",
    "TradeSide",
    "UnusualTradeListParams",
    # History
    "MarketHistoryEntry",
    "HistoryListParams",
    "SnapshotDate",
    # Keys
    "KeyInfo",
    "KeyUsage",
    "UsageHistoryEntry",
    "PlanLimits",
    # Ticker
    "TickerItem",
    "TickerListParams",
]
