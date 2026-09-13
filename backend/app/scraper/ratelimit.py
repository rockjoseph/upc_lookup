"""A tiny in-process rate limiter + TTL cache for outbound scrape requests.

Kept intentionally simple (no Redis / external deps) since this app is meant
to be run by a single user tracking a personal watch-list, not at scale.
"""
import random
import threading
import time
from typing import Any, Dict, Optional, Tuple


class RateLimiter:
    """Ensures at least `min_interval` seconds elapse between calls.

    Adds random jitter (±20%) to appear more human-like and less bot-like.
    """

    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._lock = threading.Lock()
        self._last_call = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            # Add random jitter: 80% to 120% of min_interval
            jittered_interval = self.min_interval * random.uniform(0.8, 1.2)
            sleep_for = jittered_interval - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._last_call = time.monotonic()


class TTLCache:
    """A minimal thread-safe TTL cache, avoids re-scraping the same URL."""

    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + self.ttl_seconds, value)
