# Round 3 fix list (final critic call: apply only where the pytest verifier covers the edit; everything else goes to the owner's list)

Ranks are the round-3 verifier's.

| # | File | Line | Defect | One-line fix | Must leave unchanged |
|---|---|---|---|---|---|
| B1 | ratelimit/config.py | 40-44 | Non-whole-number check only looks at `float`; `Decimal("2.9")`, `Fraction(5,2)` silently truncate to 2 | Reject when `raw_burst != int(raw_burst)` for any non-string numeric; add Decimal/Fraction tests | `test_values` (`"4"` accepted), `test_integral_float_burst_accepted`, all other config tests |
| B2 | ratelimit/config.py | 43-45 | `float()`/`int()` accept bytes (`b"2"`) and underscore/whitespace strings; bytes are a wrong type | Reject any value that is not `int`, `float`, `str`, `Decimal` or `Fraction` before converting; add bytes test | Strings `"2.5"`/`"4"` still accepted (`test_values` frozen); the policy on whether strings should be accepted at all stays with the owner |
| M7 | ratelimit/limiter.py | 36-39 | Backwards clock makes `elapsed` negative, draining tokens and locking the key out until the clock catches up | `elapsed = max(0.0, now - last)`; store `max(last, now)` as the new timestamp; add a backwards-clock test | All existing RateLimiter tests; SlidingWindow untouched |
| M8 | tests/test_limiter.py | 61 | Exact-window edge (`t > cutoff`) untested; `>` to `>=` passes the suite | Add a test that advances exactly `window` and expects admission | Existing tests; limiter.py untouched |

Confirmed in round 3 but not applied (no verifier covers the edit, or a policy decision the owner must take): 3 constructor validation (does requirement 4 apply to direct construction?); 4 the four lock-insensitive concurrency tests (a docstring is not verifier-covered; keep them as regression tests for the counts); 5 logging and an `errors` counter (adding a key to `stats` breaks the frozen `test_stats_counts` and `test_token_bucket_concurrent_never_exceeds_burst` equality assertions; shape of `stats` is the owner's call); 6 `SlidingWindow.stats` (owner must say which class owns `stats`); 9 unbounded key growth (design change).
