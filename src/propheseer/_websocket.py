"""WebSocket clients for real-time market updates (sync and async).

Requires the ``websockets`` package::

    pip install propheseer[websocket]
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import quote

from propheseer._constants import (
    DEFAULT_WS_BASE_URL,
    DEFAULT_WS_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_WS_PING_INTERVAL,
    VERSION,
)

logger = logging.getLogger("propheseer.websocket")


# ---------- Event emitter mixin ----------


class _EventEmitter:
    """Simple event emitter supporting typed callbacks."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def on(self, event: str, callback: Callable[..., Any]) -> None:
        """Register an event listener.

        Args:
            event: Event name (e.g. ``"connected"``, ``"market_update"``).
            callback: Function to call when the event fires.
        """
        self._listeners.setdefault(event, []).append(callback)

    def off(self, event: str, callback: Callable[..., Any]) -> None:
        """Remove an event listener.

        Args:
            event: Event name.
            callback: The callback to remove.
        """
        listeners = self._listeners.get(event, [])
        self._listeners[event] = [cb for cb in listeners if cb is not callback]

    def _emit(self, event: str, *args: Any) -> None:
        """Emit an event to all registered listeners."""
        for callback in self._listeners.get(event, []):
            try:
                callback(*args)
            except Exception:
                logger.exception("Error in %s event handler", event)


# ---------- Sync WebSocket ----------


class PropheseerWebSocket(_EventEmitter):
    """Synchronous WebSocket client for real-time market updates.

    Uses a background thread for the WebSocket connection loop.
    Requires the ``websockets`` package (``pip install propheseer[websocket]``).

    Args:
        api_key: API key for authentication.
        base_url: Base WebSocket URL (default: ``wss://api.propheseer.com``).
        reconnect: Whether to automatically reconnect on disconnect (default: True).
        max_reconnect_attempts: Maximum reconnection attempts (default: 5).
        ping_interval: Ping interval in seconds (default: 25).

    Events:
        - ``connected(message)``: Fired when connected.
        - ``market_update(message)``: Fired on market price update.
        - ``market_snapshot(message)``: Fired on market snapshot.
        - ``subscribed(message)``: Fired when subscription confirmed.
        - ``unsubscribed(message)``: Fired when unsubscription confirmed.
        - ``error(error)``: Fired on error (dict or Exception).
        - ``disconnect(code, reason)``: Fired on disconnection.
        - ``reconnect(attempt)``: Fired on reconnect attempt.

    Example::

        from propheseer import PropheseerWebSocket

        ws = PropheseerWebSocket(api_key="pk_test_...")

        @ws.on("connected")
        def on_connected(msg):
            print(f"Connected: {msg['sessionId']}")
            ws.subscribe(["pm_12345"])

        @ws.on("market_update")
        def on_update(msg):
            print("Update:", msg)

        ws.connect()  # blocking until connected
        # ... later:
        ws.close()
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        reconnect: bool = True,
        max_reconnect_attempts: int = DEFAULT_WS_MAX_RECONNECT_ATTEMPTS,
        ping_interval: float = DEFAULT_WS_PING_INTERVAL,
    ) -> None:
        super().__init__()
        resolved_key = api_key or os.environ.get("PROPHESEER_API_KEY")
        if not resolved_key:
            raise ValueError(
                "API key is required for WebSocket connection. "
                "Pass api_key or set PROPHESEER_API_KEY."
            )

        self._api_key = resolved_key
        base = (base_url or DEFAULT_WS_BASE_URL).rstrip("/")
        # Ensure ws:// or wss:// scheme
        if base.startswith("http://"):
            base = "ws://" + base[7:]
        elif base.startswith("https://"):
            base = "wss://" + base[8:]
        self._base_url = base
        self._reconnect_enabled = reconnect
        self._max_reconnect_attempts = max_reconnect_attempts
        self._ping_interval = ping_interval

        self._ws: Any = None
        self._thread: Optional[threading.Thread] = None
        self._ping_thread: Optional[threading.Thread] = None
        self._closed = False
        self._reconnect_attempts = 0
        self._subscribed_markets: Set[str] = set()
        self._connected_event = threading.Event()

    def on(self, event: str, callback: Optional[Callable[..., Any]] = None) -> Any:
        """Register an event listener. Can be used as a decorator.

        Args:
            event: Event name.
            callback: Function to call. If None, returns a decorator.

        Example::

            @ws.on("market_update")
            def handler(msg):
                print(msg)
        """
        if callback is not None:
            super().on(event, callback)
            return callback

        # Use as decorator
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            super(PropheseerWebSocket, self).on(event, fn)
            return fn

        return decorator

    def connect(self, timeout: float = 10.0) -> None:
        """Connect to the WebSocket server.

        Blocks until the connection is established or timeout is reached.

        Args:
            timeout: Maximum seconds to wait for connection (default: 10).
        """
        try:
            import websockets.sync.client as ws_sync
        except ImportError:
            raise ImportError(
                "The 'websockets' package is required for WebSocket support. "
                "Install it with: pip install propheseer[websocket]"
            )

        self._closed = False
        self._connected_event.clear()

        url = f"{self._base_url}/ws?api_key={quote(self._api_key, safe='')}"

        def run() -> None:
            try:
                additional_headers = {
                    "User-Agent": f"propheseer-python/{VERSION}",
                }
                self._ws = ws_sync.connect(
                    url,
                    additional_headers=additional_headers,
                )
                self._reconnect_attempts = 0
                self._connected_event.set()
                self._start_ping()

                while not self._closed:
                    try:
                        raw = self._ws.recv(timeout=1.0)
                        message = json.loads(raw)
                        self._handle_message(message)
                    except TimeoutError:
                        continue
                    except Exception as exc:
                        if self._closed:
                            break
                        self._emit("error", exc)
                        break

            except Exception as exc:
                self._emit("error", exc)
                self._connected_event.set()  # Unblock connect()
            finally:
                self._stop_ping()
                if self._ws:
                    try:
                        self._ws.close()
                    except Exception:
                        pass
                self._emit("disconnect", 1000, "")
                if not self._closed and self._reconnect_enabled:
                    self._attempt_reconnect()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        self._connected_event.wait(timeout=timeout)

    def subscribe(self, market_ids: List[str]) -> None:
        """Subscribe to real-time updates for specific market IDs.

        Args:
            market_ids: List of market IDs to subscribe to.
        """
        for mid in market_ids:
            self._subscribed_markets.add(mid)
        self._send({"type": "subscribe", "markets": market_ids})

    def unsubscribe(self, market_ids: List[str]) -> None:
        """Unsubscribe from market updates.

        Args:
            market_ids: List of market IDs to unsubscribe from.
        """
        for mid in market_ids:
            self._subscribed_markets.discard(mid)
        self._send({"type": "unsubscribe", "markets": market_ids})

    def list_subscriptions(self) -> None:
        """Request the current list of subscribed markets."""
        self._send({"type": "list_subscriptions"})

    def close(self) -> None:
        """Close the WebSocket connection."""
        self._closed = True
        self._stop_ping()
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None

    def _handle_message(self, message: Dict[str, Any]) -> None:
        msg_type = message.get("type", "")
        if msg_type in (
            "connected",
            "market_update",
            "market_snapshot",
            "subscribed",
            "unsubscribed",
            "error",
        ):
            self._emit(msg_type, message)

    def _send(self, data: Dict[str, Any]) -> None:
        if self._ws:
            try:
                self._ws.send(json.dumps(data))
            except Exception:
                pass

    def _start_ping(self) -> None:
        self._stop_ping()

        def ping_loop() -> None:
            while not self._closed and self._ws:
                time.sleep(self._ping_interval)
                if not self._closed and self._ws:
                    self._send({"type": "ping"})

        self._ping_thread = threading.Thread(target=ping_loop, daemon=True)
        self._ping_thread.start()

    def _stop_ping(self) -> None:
        self._ping_thread = None

    def _attempt_reconnect(self) -> None:
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self._emit(
                "error",
                Exception(
                    f"Failed to reconnect after {self._max_reconnect_attempts} attempts"
                ),
            )
            return

        self._reconnect_attempts += 1
        delay = min(1.0 * (2 ** (self._reconnect_attempts - 1)), 30.0)
        self._emit("reconnect", self._reconnect_attempts)

        time.sleep(delay)
        if self._closed:
            return

        try:
            self.connect()
            if self._subscribed_markets:
                self.subscribe(list(self._subscribed_markets))
        except Exception:
            pass


# ---------- Async WebSocket ----------


class AsyncPropheseerWebSocket(_EventEmitter):
    """Asynchronous WebSocket client for real-time market updates.

    Requires the ``websockets`` package (``pip install propheseer[websocket]``).

    Args:
        api_key: API key for authentication.
        base_url: Base WebSocket URL (default: ``wss://api.propheseer.com``).
        reconnect: Whether to automatically reconnect on disconnect (default: True).
        max_reconnect_attempts: Maximum reconnection attempts (default: 5).
        ping_interval: Ping interval in seconds (default: 25).

    Example::

        import asyncio
        from propheseer import AsyncPropheseerWebSocket

        async def main():
            ws = AsyncPropheseerWebSocket(api_key="pk_test_...")

            ws.on("connected", lambda msg: print(f"Connected: {msg['sessionId']}"))
            ws.on("market_update", lambda msg: print("Update:", msg))

            await ws.connect()
            ws.subscribe(["pm_12345"])

            await asyncio.sleep(60)  # listen for a while
            ws.close()
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        reconnect: bool = True,
        max_reconnect_attempts: int = DEFAULT_WS_MAX_RECONNECT_ATTEMPTS,
        ping_interval: float = DEFAULT_WS_PING_INTERVAL,
    ) -> None:
        super().__init__()
        resolved_key = api_key or os.environ.get("PROPHESEER_API_KEY")
        if not resolved_key:
            raise ValueError(
                "API key is required for WebSocket connection. "
                "Pass api_key or set PROPHESEER_API_KEY."
            )

        self._api_key = resolved_key
        base = (base_url or DEFAULT_WS_BASE_URL).rstrip("/")
        if base.startswith("http://"):
            base = "ws://" + base[7:]
        elif base.startswith("https://"):
            base = "wss://" + base[8:]
        self._base_url = base
        self._reconnect_enabled = reconnect
        self._max_reconnect_attempts = max_reconnect_attempts
        self._ping_interval = ping_interval

        self._ws: Any = None
        self._ping_task: Any = None
        self._receive_task: Any = None
        self._closed = False
        self._reconnect_attempts = 0
        self._subscribed_markets: Set[str] = set()

    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        import asyncio

        try:
            import websockets
        except ImportError:
            raise ImportError(
                "The 'websockets' package is required for WebSocket support. "
                "Install it with: pip install propheseer[websocket]"
            )

        self._closed = False
        url = f"{self._base_url}/ws?api_key={quote(self._api_key, safe='')}"

        additional_headers = {
            "User-Agent": f"propheseer-python/{VERSION}",
        }

        self._ws = await websockets.connect(
            url,
            additional_headers=additional_headers,
        )
        self._reconnect_attempts = 0
        self._start_ping()
        self._start_receive()

    def subscribe(self, market_ids: List[str]) -> None:
        """Subscribe to real-time updates for specific market IDs.

        Args:
            market_ids: List of market IDs to subscribe to.
        """
        for mid in market_ids:
            self._subscribed_markets.add(mid)
        self._send_nowait({"type": "subscribe", "markets": market_ids})

    def unsubscribe(self, market_ids: List[str]) -> None:
        """Unsubscribe from market updates.

        Args:
            market_ids: List of market IDs to unsubscribe from.
        """
        for mid in market_ids:
            self._subscribed_markets.discard(mid)
        self._send_nowait({"type": "unsubscribe", "markets": market_ids})

    def list_subscriptions(self) -> None:
        """Request the current list of subscribed markets."""
        self._send_nowait({"type": "list_subscriptions"})

    async def close(self) -> None:
        """Close the WebSocket connection."""
        import asyncio

        self._closed = True
        if self._ping_task:
            self._ping_task.cancel()
            self._ping_task = None
        if self._receive_task:
            self._receive_task.cancel()
            self._receive_task = None
        if self._ws:
            await self._ws.close()
            self._ws = None

    def _handle_message(self, message: Dict[str, Any]) -> None:
        msg_type = message.get("type", "")
        if msg_type in (
            "connected",
            "market_update",
            "market_snapshot",
            "subscribed",
            "unsubscribed",
            "error",
        ):
            self._emit(msg_type, message)

    def _send_nowait(self, data: Dict[str, Any]) -> None:
        import asyncio

        if self._ws:
            try:
                asyncio.ensure_future(self._ws.send(json.dumps(data)))
            except Exception:
                pass

    def _start_ping(self) -> None:
        import asyncio

        if self._ping_task:
            self._ping_task.cancel()

        async def ping_loop() -> None:
            while not self._closed and self._ws:
                await asyncio.sleep(self._ping_interval)
                if not self._closed and self._ws:
                    try:
                        await self._ws.send(json.dumps({"type": "ping"}))
                    except Exception:
                        break

        self._ping_task = asyncio.ensure_future(ping_loop())

    def _start_receive(self) -> None:
        import asyncio

        if self._receive_task:
            self._receive_task.cancel()

        async def receive_loop() -> None:
            try:
                async for raw in self._ws:
                    if self._closed:
                        break
                    try:
                        message = json.loads(raw)
                        self._handle_message(message)
                    except json.JSONDecodeError:
                        pass
            except Exception as exc:
                if not self._closed:
                    self._emit("error", exc)
            finally:
                self._emit("disconnect", 1000, "")
                if not self._closed and self._reconnect_enabled:
                    await self._attempt_reconnect()

        self._receive_task = asyncio.ensure_future(receive_loop())

    async def _attempt_reconnect(self) -> None:
        import asyncio

        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self._emit(
                "error",
                Exception(
                    f"Failed to reconnect after {self._max_reconnect_attempts} attempts"
                ),
            )
            return

        self._reconnect_attempts += 1
        delay = min(1.0 * (2 ** (self._reconnect_attempts - 1)), 30.0)
        self._emit("reconnect", self._reconnect_attempts)

        await asyncio.sleep(delay)
        if self._closed:
            return

        try:
            await self.connect()
            if self._subscribed_markets:
                self.subscribe(list(self._subscribed_markets))
        except Exception:
            pass
