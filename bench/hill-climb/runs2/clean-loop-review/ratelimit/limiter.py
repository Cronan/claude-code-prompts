"""Rate limiting primitives.

Both limiters are keyed: a key is any hashable identifying a client.
They are intended for use from many threads at once, and must never
let a request through when an internal error occurs (fail closed).
"""

import math
import threading
import time

from .config import _positive_int, _positive_number


class RateLimiter:
    """Token bucket limiter.

    ``rate`` is tokens added per second (may be fractional, e.g. 0.5 for
    one request every two seconds). ``burst`` is the bucket capacity and
    the number of requests a fresh key may make at once.

    ``clock`` is injectable for testing and must return seconds as a float.
    Invalid ``rate`` or ``burst`` raises ``ConfigError``.
    """

    def __init__(self, rate, burst, clock=time.monotonic):
        self.rate = _positive_number("rate", rate)
        self.burst = _positive_int("burst", burst)
        self.clock = clock
        self._buckets = {}
        self._lock = threading.Lock()
        self.stats = {"allowed": 0, "denied": 0}

    def allow(self, key):
        """Return True if ``key`` may proceed now, consuming one token."""
        try:
            with self._lock:
                now = self.clock()
                if not math.isfinite(now):
                    self.stats["denied"] += 1
                    return False
                tokens, last = self._buckets.get(key, (float(self.burst), now))
                elapsed = max(0.0, now - last)
                tokens = min(float(self.burst), tokens + elapsed * self.rate)
                if tokens >= 1.0:
                    self.stats["allowed"] += 1
                    self._buckets[key] = (tokens - 1.0, now)
                    return True
                # On deny leave the bucket as it was: refill is then computed
                # in one step from the last admission, so fractional rates do
                # not accumulate floating-point error across repeated polls.
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
    counts. Invalid ``limit`` or ``window`` raises ``ConfigError``.
    """

    def __init__(self, limit, window, clock=time.monotonic):
        self.limit = _positive_int("limit", limit)
        self.window = _positive_number("window", window)
        self.clock = clock
        self._log = {}
        self._lock = threading.Lock()

    def allow(self, key):
        try:
            with self._lock:
                now = self.clock()
                if not math.isfinite(now):
                    return False
                cutoff = now - self.window
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
