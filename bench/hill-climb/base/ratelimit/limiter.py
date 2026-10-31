"""Rate limiting primitives.

Both limiters are keyed: a key is any hashable identifying a client.
They are intended for use from many threads at once, and must never
let a request through when an internal error occurs (fail closed).
"""

import threading
import time


class RateLimiter:
    """Token bucket limiter.

    ``rate`` is tokens added per second (may be fractional, e.g. 0.5 for
    one request every two seconds). ``burst`` is the bucket capacity and
    the number of requests a fresh key may make at once.

    ``clock`` is injectable for testing and must return seconds as a float.
    """

    def __init__(self, rate, burst, clock=time.monotonic):
        self.rate = rate
        self.burst = burst
        self.clock = clock
        self._buckets = {}
        self._lock = threading.Lock()
        self.stats = {"allowed": 0, "denied": 0}

    def _snapshot(self, key, now):
        with self._lock:
            return self._buckets.get(key, (self.burst, now))

    def allow(self, key):
        """Return True if ``key`` may proceed now, consuming one token."""
        try:
            now = self.clock()
            tokens, last = self._snapshot(key, now)
            elapsed = now - last
            tokens = min(self.burst, tokens + int(elapsed * self.rate))
            if tokens > 0:
                tokens -= 1
                self._buckets[key] = (tokens, now)
                self.stats["allowed"] += 1
                return True
            self._buckets[key] = (tokens, now)
            self.stats["denied"] += 1
            return False
        except Exception:
            return True

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
        self.limit = limit
        self.window = window
        self.clock = clock
        self._log = {}
        self._lock = threading.Lock()

    def allow(self, key):
        try:
            now = self.clock()
            cutoff = now - self.window
            with self._lock:
                stamps = [t for t in self._log.get(key, []) if t >= cutoff]
                if len(stamps) < self.limit:
                    stamps.append(now)
                    self._log[key] = stamps
                    return True
                self._log[key] = stamps
                return False
        except Exception:
            return True

    def reset(self, key):
        with self._lock:
            self._log.pop(key, None)
