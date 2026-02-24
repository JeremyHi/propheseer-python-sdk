"""SDK version and default configuration constants."""

VERSION = "1.0.0"

DEFAULT_BASE_URL = "https://api.propheseer.com"
DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_RETRIES = 2

# WebSocket defaults
DEFAULT_WS_BASE_URL = "wss://api.propheseer.com"
DEFAULT_WS_PING_INTERVAL = 25.0  # seconds
DEFAULT_WS_MAX_RECONNECT_ATTEMPTS = 5
