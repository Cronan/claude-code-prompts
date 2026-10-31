# Round 1 fix list (confirmed blocking only; 8 blocking + 10 misleading > 8, so misleading carried forward unchanged)

| # | File | Line | Defect | One-line fix | Must leave unchanged |
|---|---|---|---|---|---|
| B1 | ratelimit/limiter.py | 70 | SlidingWindow.allow reads clock() outside the lock; a preempted thread logs a stale stamp that leaves the window early, admitting more than limit under contention | Move `now = self.clock()` and `cutoff` inside `with self._lock:` | RateLimiter untouched; all existing SlidingWindow tests |
| B2 | ratelimit/config.py | 41-46 | "nan"/"inf" (string or float) pass `<= 0` checks, producing non-finite rate/window | Add `math.isfinite` check to rate and window | Defaults 1.0/10/60.0; numeric-string coercion required by test_values |
| B3 | ratelimit/config.py | 37-39 | `int(float("inf"))` raises OverflowError, not caught | Add OverflowError to the except tuple | Same as B2 |
| B4 | ratelimit/config.py | 36-38 | bool accepted as a number; non-integral burst (2.9) silently truncated | Reject bool for all three; reject a float burst that is not integral | Numeric strings "2.5"/"4" still accepted (test_values frozen) |
| B5 | tests/test_limiter.py | - | No test of one key under many threads | Add a threaded test asserting allowed count == burst / limit | Existing tests |
| B6 | tests/test_limiter.py | - | No test of a fractional rate | Add test with rate=0.5: deny at 1s, allow at 2s | Existing tests |
| B7 | tests/test_limiter.py | - | No test of fail-closed with a raising clock | Add test with a clock that raises; allow returns False for both limiters | Existing tests |
| B8 | tests/test_config.py | - | No tests for unknown keys, zero/negative burst/window, negative rate, bool, None, list, nan/inf, overflow | Add parametrised ConfigError tests | Existing tests |

Carried forward (confirmed misleading, not fixed this round): M1 NaN/inf rate via direct construction; M2 NaN window via direct construction; M3 stats live dict, except path uncounted, reset leaves stats; M4 SlidingWindow has no stats; M5 except swallows errors silently; M6 reset not wrapped like allow; M7 backwards clock drains tokens; M8 float cutoff edge for "exactly window ago"; M9 unbounded key growth; M10 Config has no limit field.
