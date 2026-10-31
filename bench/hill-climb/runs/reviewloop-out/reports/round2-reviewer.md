Review of the whole `ratelimit` library: `python3 -m pytest -q` gives `95 passed in 0.65s`. I found no race or fail-open path in the lock and `allow()` logic. I found five defects, plus checklist notes, listed most severe first.

1. **`ratelimit/limiter.py:190,244` — Clock readings of ±inf are accepted, which can lock a key out for good.**
   - The code rejects only NaN.
   - `RateLimiter`: if the clock returns `inf` once, `last` becomes `inf`. Every later finite `now` gives `elapsed=0`, so there is never any refill.
   - `SlidingWindow`: the stored `inf` timestamp satisfies `t > cutoff` forever. After `inf`, `limit=1` admits once, then denies at t=1e9.
   - Measured: both limiters go `True`, then `False` forever.
   - This breaks the fail-closed intent (item 3) the other way: one bad clock value causes a permanent outage for that key.
   - Related, lower severity: `last = max(last, now)` (line 200) means a legitimate backward clock step of 1000s denies the key until the clock catches up. I measured that with `t=1000 → 0`.

2. **`ratelimit/config.py:62-63,93-95` and `ratelimit/limiter.py:140,158` — Huge integers raise `OverflowError` instead of `ConfigError`.**
   - `float(10**400)` raises `OverflowError`, which none of the validators catch.
   - `load_config({"rate": 10**400})` and `RateLimiter(10**400, 1)` both raise `OverflowError`. I ran both and it is confirmed.
   - Item 4 says invalid config raises `ConfigError` from `load_config`; callers catching `ConfigError`/`ValueError` will miss this. `OverflowError` is an `ArithmeticError`, not a `ValueError`.
   - There is no test for it.

3. **`ratelimit/limiter.py:195-206` — Incremental float refill drifts, so a key can be denied at the exact boundary.**
   - `tokens` is updated on every call by adding `elapsed*rate` (item 2), so rounding error accumulates.
   - `RateLimiter(rate=0.2, burst=1)` polled every 0.1s: at t=5.0, exactly 1/rate seconds after the first request, `allow()` returns `False`. I measured this.
   - The 0.5 and 0.1 cases the tests use happen to land exactly, so the tests don't catch it.
   - Item 2 says the limiter denies until the interval has elapsed and then admits. For other rates, how often a caller polls changes the exact admit time.
   - Storing the last-admit time and refilling from that would avoid the drift.

4. **`ratelimit/limiter.py:174-178,229-234` and `ratelimit/config.py:57-99` — Validation goes beyond the checklist and is inconsistent.**
   - Item 5 says signatures are unchanged and only `load_config` should reject bad config (item 4). The constructors now also reject non-numeric, string, non-int-valued and `numpy.int64` arguments, and a non-callable `clock`.
   - A caller that used to pass such values now gets `ConfigError`.
   - `load_config` accepts the string `"1_0"` for `rate` but rejects `"1e3"` for `burst`. It accepts `burst=1000.0` but not `"1000.0"`.
   - `_INT_PATTERN_OK` (`config.py:46,83`) is a redundant pre-filter before `int()`.
   - `_as_float`/`_as_int` in `config.py` and `_check_positive_number`/`_check_positive_int` in `limiter.py` are near-duplicates, which is a maintenance risk.

5. **`tests/test_limiter.py:415-435` — The reset race test asserts almost nothing.**
   - `assert rl.allow("k") in (True, False)` can never fail. It is the same non-assertion the author tightened in `test_refill`.
   - The test would pass against the original v1 code, so it gives no regression coverage for the reset race.
   - The other concurrency tests do check exact counts. I did not run the pre-change code, so I can't confirm they fail without the fix.

**Checklist notes (not defects):**
- **Acceptance:** each of the six items maps to code and tests.
- **Backward compatibility:** the pre-existing tests pass unmodified except `test_refill`, which was made stricter, as allowed. Config string coercion is kept, which the pre-existing `test_values` requires.
- **Hygiene:** no debug prints, scratch files or secrets. `README.md` is not updated to say that numeric strings are accepted in config.
- **Pre-existing, not introduced:** per-key state (`_buckets`, `_log`) is never evicted, so memory grows with the number of distinct keys. `load_config` accepts only `dict`, not other mappings.
