I read every file and ran nothing, so these findings come from reading the code, not from executing it.

**Findings**

1. **`ratelimit/config.py:36-37`, medium-high.** `float()` and `int()` coerce instead of type-checking, so wrong types are accepted. The README says wrong types must raise `ConfigError`.
   - `True`, `"4"` and `2.9` are accepted. `burst: 2.9` is silently truncated to 2.
   - `tests/test_config.py:10-12` asserts the string coercion, so the test enshrines the bug.
   - Fix: reject anything that isn't a real `int` or `float` and isn't a `bool`. For `burst`, also reject non-integral floats.

2. **`ratelimit/config.py:41-46`, medium-high.** `nan` and `inf` pass the positivity checks. `float("nan") <= 0` is False, so `rate: nan` or `window: nan` is accepted. `inf` is also accepted.
   - A `nan` rate makes every bucket compute `nan` tokens and deny forever. A `nan` window never expires entries.
   - Fix: use `math.isfinite(x) and x > 0` for `rate` and `window`.

3. **`ratelimit/config.py:37-39`, medium.** `int(float('inf'))` raises `OverflowError`, which the `except (TypeError, ValueError)` clause doesn't catch. YAML `.inf` or a huge JSON number such as `1e999` therefore escapes as a raw exception, not `ConfigError`. Fix: catch `OverflowError` too, or check finiteness before converting.

4. **`ratelimit/config.py:34`, low.** `sorted(unknown)` raises `TypeError` for mixed-type keys, such as `{1: 0, "a": 0}` from YAML. That is not a `ConfigError`. Fix: use `sorted(map(repr, unknown))`, or `sorted(..., key=str)`.

5. **`ratelimit/limiter.py:22-24, 61-63`, medium.** The limiter constructors do no validation, so the config rules are bypassed when a limiter is built directly.
   - `burst=0` or `burst=0.5` denies forever.
   - A negative `rate` drains the bucket.
   - `limit=None` makes `len(stamps) < self.limit` raise, which fail-closed swallows, so every request is denied with no signal.
   - Fix: validate in `__init__` and raise `ValueError` (or `ConfigError`) for non-positive or non-finite values.

6. **`ratelimit/limiter.py:35, 65`, medium.** Per-key state is never evicted.
   - `_buckets` and `_log` gain an entry per key and only `reset` removes it, so unbounded keys such as client IPs leak memory.
   - A `SlidingWindow` key that stops sending keeps its stale timestamps forever, since pruning only happens when that key calls `allow` again.
   - Fix: drop a bucket once it has refilled to `burst`, and delete the `_log` entry when `stamps` is empty. Also sweep idle keys periodically.

7. **`ratelimit/limiter.py:70-72`, low-medium.** `SlidingWindow.allow` reads the clock before taking the lock.
   - Under contention a thread can hold a stale `now` and append an out-of-order timestamp.
   - The limit still isn't exceeded, because a stale cutoff is more conservative. The stale timestamp does skew the window for later calls.
   - Fix: move `now = self.clock()` and `cutoff` inside the `with self._lock:` block, as `RateLimiter` does.

8. **`ratelimit/limiter.py:45-46`, low.** When the fail-closed branch fires, `stats["denied"]` isn't incremented, so the stats undercount denials. Fix: increment `denied` under the lock in the `except` path, guarded so it can't raise.

9. **`tests/`, low (missing coverage).** There is no test for any of the README's core requirements: a multi-threaded test that checks a key never exceeds its limit, a fractional rate such as 0.5, fail-closed behaviour (for example a clock that raises), or `nan`, `inf`, `bool` and unknown keys in `load_config`. Fix: add these tests. They would have caught findings 1–3.

The token-bucket arithmetic and locking in `RateLimiter.allow` are correct. Fractional rates work, and the check and update happen atomically under one lock.
