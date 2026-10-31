"""Rate limiting primitives.

Both limiters are keyed: a key is any hashable identifying a client.
They are intended for use from many threads at once, and must never
let a request through when an internal error occurs (fail closed).
"""

import math
import threading
import time

from .config import ConfigError


def _check_number(name, value, allow_zero):
    """Reject non-numeric, bool, non-finite and out-of-range constructor args."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name} must be a number")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        # int too large to convert to float
        finite = False
    if not finite:
        raise ConfigError(f"{name} must be finite")
    if value < 0 or (value == 0 and not allow_zero):
        raise ConfigError(f"{name} must be positive")


class RateLimiter:
    """Token bucket limiter.

    ``rate`` is tokens added per second (may be fractional, e.g. 0.5 for
    one request every two seconds). ``burst`` is the bucket capacity and
    the number of requests a fresh key may make at once.

    ``clock`` is injectable for testing and must return seconds as a float.
    """

    def __init__(self, rate, burst, clock=time.monotonic):
        _check_number("rate", rate, allow_zero=False)
        _check_number("burst", burst, allow_zero=True)
        if int(burst) != burst:
            raise ConfigError("burst must be a whole number")
        self.rate = rate
        self.burst = burst
        self.clock = clock
        self._buckets = {}
        self._lock = threading.Lock()
        self.stats = {"allowed": 0, "denied": 0}

    def allow(self, key):
        """Return True if ``key`` may proceed now, consuming one token."""
        try:
            with self._lock:
                # The clock is read under the lock: a timestamp taken before
                # waiting for the lock would be stale by the time it is used,
                # and a stale ``last`` lets the next caller refill a token
                # that was already spent.
                now = self.clock()
                if not math.isfinite(now):
                    # A broken clock must not be able to refill the bucket.
                    self.stats["denied"] += 1
                    return False
                tokens, last = self._buckets.get(key, (float(self.burst), now))
                elapsed = now - last
                if elapsed > 0:
                    # Tokens are kept as a float so fractional rates (0.5/s)
                    # and sub-second polling accumulate rather than truncate.
                    tokens = min(float(self.burst), tokens + elapsed * self.rate)
                    last = now
                # Repeated additions of elapsed * rate accumulate rounding
                # error (ten additions of 0.1 give 0.9999999999999999), so a
                # token within 1e-9 of whole counts as whole.
                if tokens >= 1.0 - 1e-9:
                    tokens -= 1.0
                    self._buckets[key] = (tokens, last)
                    self.stats["allowed"] += 1
                    return True
                self._buckets[key] = (tokens, last)
                self.stats["denied"] += 1
                return False
        except Exception:
            # Fail closed: an internal error must never admit a request.
            self._count_denied()
            return False

    def _count_denied(self):
        try:
            with self._lock:
                self.stats["denied"] += 1
        except Exception:
            pass

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
        _check_number("limit", limit, allow_zero=True)
        if int(limit) != limit:
            raise ConfigError("limit must be a whole number")
        _check_number("window", window, allow_zero=False)
        self.limit = limit
        self.window = window
        self.clock = clock
        self._log = {}
        self._lock = threading.Lock()

    def _in_window(self, now, stamp):
        """True if ``stamp`` is strictly less than ``window`` seconds old.

        ``now - stamp`` can round (e.g. 16.4 - 6.4 gives 10.000000000000002)
        so a stamp exactly ``window`` old would otherwise still count. The
        rounding error of the subtraction is bounded by the spacing of floats
        around ``now``, so an age within a few ulps of ``now`` from ``window``
        is treated as expired. The tolerance must not scale with ``window``:
        a relative tolerance would expire requests milliseconds early on a
        30-day window.
        """
        age = now - stamp
        if math.isclose(age, self.window, rel_tol=0.0, abs_tol=4 * math.ulp(now)):
            return False
        return age < self.window

    def allow(self, key):
        try:
            with self._lock:
                # Read the clock under the lock; see RateLimiter.allow.
                now = self.clock()
                if not math.isfinite(now):
                    # A NaN clock would empty the log and admit everything.
                    return False
                stamps = [
                    t for t in self._log.get(key, []) if self._in_window(now, t)
                ]
                if len(stamps) < self.limit:
                    stamps.append(now)
                    self._log[key] = stamps
                    return True
                self._log[key] = stamps
                return False
        except Exception:
            # Fail closed: an internal error must never admit a request.
            return False

    def reset(self, key):
        with self._lock:
            self._log.pop(key, None)
