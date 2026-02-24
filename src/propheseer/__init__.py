"""Propheseer Python SDK - Official client for the prediction markets API.

Access normalized data from Polymarket, Kalshi, and Gemini through a single,
type-safe interface.

Example::

    from propheseer import Propheseer

    client = Propheseer(api_key="pk_test_...")

    # List markets
    page = client.markets.list(source="polymarket", limit=10)
    for market in page.data:
        print(f"{market.question}: {market.outcomes[0].probability:.0%}")

    # Find arbitrage (Pro+)
    result = client.arbitrage.find(min_spread=0.05)
    for opp in result.data:
        print(f"{opp.question}: {opp.potential_return}")
"""

from __future__ import annotations

# Client classes
from propheseer._client import Propheseer, AsyncPropheseer

# Constants
from propheseer._constants import VERSION

# Pagination
from propheseer._pagination import SyncPage, AsyncPage, PaginationMeta

# Response
from propheseer._response import APIResponse, RateLimitInfo

# Errors
from propheseer._exceptions import (
    PropheseerError,
    AuthenticationError,
    InsufficientCreditsError,
    PermissionDeniedError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
    APIConnectionError,
)

# WebSocket
from propheseer._websocket import PropheseerWebSocket, AsyncPropheseerWebSocket

# Types - Markets
from propheseer.types.markets import (
    Market,
    Outcome,
    MarketSource,
    MarketStatus,
    MarketCategory,
    MarketListParams,
)

# Types - Categories
from propheseer.types.categories import Category

# Types - Arbitrage
from propheseer.types.arbitrage import (
    ArbitrageOpportunity,
    ArbitrageMarket,
    ArbitrageFindParams,
)

# Types - Unusual Trades
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

# Types - History
from propheseer.types.history import (
    MarketHistoryEntry,
    HistoryListParams,
    SnapshotDate,
)

# Types - Keys
from propheseer.types.keys import (
    KeyInfo,
    KeyUsage,
    UsageHistoryEntry,
    PlanLimits,
)

# Types - Ticker
from propheseer.types.ticker import TickerItem, TickerListParams

__all__ = [
    # Clients
    "Propheseer",
    "AsyncPropheseer",
    # Constants
    "VERSION",
    # Pagination
    "SyncPage",
    "AsyncPage",
    "PaginationMeta",
    # Response
    "APIResponse",
    "RateLimitInfo",
    # Errors
    "PropheseerError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "PermissionDeniedError",
    "NotFoundError",
    "RateLimitError",
    "InternalServerError",
    "APIConnectionError",
    # WebSocket
    "PropheseerWebSocket",
    "AsyncPropheseerWebSocket",
    # Types - Markets
    "Market",
    "Outcome",
    "MarketSource",
    "MarketStatus",
    "MarketCategory",
    "MarketListParams",
    # Types - Categories
    "Category",
    # Types - Arbitrage
    "ArbitrageOpportunity",
    "ArbitrageMarket",
    "ArbitrageFindParams",
    # Types - Unusual Trades
    "UnusualTrade",
    "UnusualTradeMarket",
    "TradeDetails",
    "DetectionInfo",
    "DetectionContext",
    "DetectionReason",
    "TradeSide",
    "UnusualTradeListParams",
    # Types - History
    "MarketHistoryEntry",
    "HistoryListParams",
    "SnapshotDate",
    # Types - Keys
    "KeyInfo",
    "KeyUsage",
    "UsageHistoryEntry",
    "PlanLimits",
    # Types - Ticker
    "TickerItem",
    "TickerListParams",
]
