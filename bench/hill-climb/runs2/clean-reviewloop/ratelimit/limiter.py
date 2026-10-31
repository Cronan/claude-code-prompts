"""Rate limiting primitives.

Both limiters are keyed: a key is any hashable identifying a client.
They are intended for use from many threads at once, and must never
let a request through when an internal error occurs (fail closed).
"""

import math
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

    def allow(self, key):
        """Return True if ``key`` may proceed now, consuming one token.

        Any internal error denies the request and counts it as denied:
        the clock raising or returning a non-finite value, an unhashable
        key, or ``rate``/``burst`` values that make the token count
        non-numeric or non-finite.
        """
        try:
            with self._lock:
                now = self.clock()
                if not math.isfinite(now):
                    raise ValueError(f"clock returned {now!r}")
                tokens, last = self._buckets.get(key, (float(self.burst), now))
                tokens = tokens + (now - last) * self.rate
                if not math.isfinite(tokens):
                    raise ValueError(f"token count is {tokens!r}")
                tokens = min(float(self.burst), tokens)
                if tokens >= 1.0:
                    self._buckets[key] = (tokens - 1.0, now)
                    self.stats["allowed"] += 1
                    return True
                self._buckets[key] = (tokens, now)
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
        """Forget ``key`` so its next request sees a full bucket.

        Raises ``TypeError`` for an unhashable key, as a dict would; no
        request is admitted by this call.
        """
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
        """Return True if ``key`` may proceed now, recording the request.

        Any internal error denies the request: the clock raising or
        returning a non-finite value, an unhashable key, or a ``window``
        that makes the cutoff non-numeric or non-finite.
        """
        try:
            with self._lock:
                now = self.clock()
                cutoff = now - self.window
                if not (math.isfinite(cutoff) and cutoff < now):
                    raise ValueError(f"window cutoff is {cutoff!r} at {now!r}")
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
        """Forget ``key``'s request log.

        Raises ``TypeError`` for an unhashable key, as a dict would; no
        request is admitted by this call.
        """
        with self._lock:
            self._log.pop(key, None)
