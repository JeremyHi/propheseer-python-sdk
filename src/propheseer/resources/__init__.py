"""API resource namespaces."""

from propheseer.resources.markets import SyncMarkets, AsyncMarkets
from propheseer.resources.categories import SyncCategories, AsyncCategories
from propheseer.resources.arbitrage import SyncArbitrage, AsyncArbitrage
from propheseer.resources.unusual_trades import SyncUnusualTrades, AsyncUnusualTrades
from propheseer.resources.history import SyncHistory, AsyncHistory
from propheseer.resources.keys import SyncKeys, AsyncKeys
from propheseer.resources.ticker import SyncTicker, AsyncTicker

__all__ = [
    "SyncMarkets",
    "AsyncMarkets",
    "SyncCategories",
    "AsyncCategories",
    "SyncArbitrage",
    "AsyncArbitrage",
    "SyncUnusualTrades",
    "AsyncUnusualTrades",
    "SyncHistory",
    "AsyncHistory",
    "SyncKeys",
    "AsyncKeys",
    "SyncTicker",
    "AsyncTicker",
]
