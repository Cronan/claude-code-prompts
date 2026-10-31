"""Rate limiting primitives.

Both limiters are keyed: a key is any hashable identifying a client.
They are intended for use from many threads at once, and must never
let a request through when an internal error occurs (fail closed).
"""

import math
import threading
import time

from .config import ConfigError, coerce_float, coerce_int


def _check_clock(clock):
    if not callable(clock):
        raise ConfigError("clock must be callable")
    return clock


def _read_clock(clock):
    """Return the clock's reading as a finite float, or raise."""
    now = float(clock())
    if not math.isfinite(now):
        raise ValueError(f"clock returned a non-finite value: {now!r}")
    return now


class RateLimiter:
    """Token bucket limiter.

    ``rate`` is tokens added per second (may be fractional, e.g. 0.5 for
    one request every two seconds). ``burst`` is the bucket capacity and
    the number of requests a fresh key may make at once.

    ``clock`` is injectable for testing and must return seconds as a float.
    """

    def __init__(self, rate, burst, clock=time.monotonic):
        self.rate = coerce_float("rate", rate)
        self.burst = coerce_int("burst", burst)
        self.clock = _check_clock(clock)
        self._buckets = {}
        self._lock = threading.Lock()
        self.stats = {"allowed": 0, "denied": 0}

    def allow(self, key):
        """Return True if ``key`` may proceed now, consuming one token.

        Any internal error denies the request (fail closed). Per-key state
        is ``(tokens, last)`` and is rewritten only when a request is
        admitted, so polling a denied key neither discards fractional refill
        nor accumulates rounding error, and a clock reading that goes
        backwards grants nothing and leaves the stored baseline alone.
        """
        try:
            now = _read_clock(self.clock)
            with self._lock:
                tokens, last = self._buckets.get(key, (float(self.burst), now))
                elapsed = max(0.0, now - last)
                available = min(float(self.burst), tokens + elapsed * self.rate)
                if available >= 1.0:
                    self._buckets[key] = (available - 1.0, max(last, now))
                    self.stats["allowed"] += 1
                    return True
                self.stats["denied"] += 1
                return False
        except Exception:
            try:
                with self._lock:
                    self.stats["denied"] += 1
            except Exception:
                pass
            return False

    def reset(self, key):
        with self._lock:
            self._buckets.pop(key, None)


class SlidingWindow:
    """Sliding-window log limiter.

    Allows at most ``limit`` requests in any ``window`` seconds. A request
    made exactly ``window`` seconds ago has left the window and no longer
    counts.
    """

    def __init__(self, limit, window, clock=time.monotonic):
        self.limit = coerce_int("limit", limit)
        self.window = coerce_float("window", window)
        self.clock = _check_clock(clock)
        self._log = {}
        self._lock = threading.Lock()

    def allow(self, key):
        """Return True if ``key`` may proceed now.

        Any internal error denies the request (fail closed).
        """
        try:
            now = _read_clock(self.clock)
            cutoff = now - self.window
            with self._lock:
                stamps = [t for t in self._log.get(key, []) if t > cutoff]
                if len(stamps) < self.limit:
                    stamps.append(now)
                    self._log[key] = stamps
                    return True
                self._log[key] = stamps
                return False
        except Exception:
            return False

    def reset(self, key):
        with self._lock:
            self._log.pop(key, None)
