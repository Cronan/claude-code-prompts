# Round 3 fix list (final call; confirmed by verifier; applied only where pytest covers the edit)

Confirmed: 6 blocking (1, 2, 3, 4, 9, 10), 4 misleading (5, 6, 7, 8). Disputed: 11 (verifier: true for the token-bucket test only, false for the sliding-window test). Items 7 and 8 are owner decisions (which class carries `stats`; whether zero burst/limit is legal) and are not fixed. Minors 11-13 from the critic are not covered by a verifier and go to the owner's list.

| # | File | Line | Defect | One-line fix | Test added | Must leave unchanged |
|---|---|---|---|---|---|---|
| 1 | ratelimit/limiter.py | `now = self.clock()` before `with self._lock:` (both `allow`) | Stale clock read after lock wait causes double admission | Read the clock inside the lock | stale-clock test using a lock held by the test | Fail-closed on clock exception; all single-thread results |
| 2 | ratelimit/limiter.py | `if tokens >= 1.0:` | Float accumulation: rate 0.1 admits at t=11 not t=10 | Compare with a 1e-9 absolute tolerance | rate 0.1 polled every 1 s admits at t=10 | 0.5 and 1.0 rate tests |
| 3 | ratelimit/limiter.py | `_check_number`: `math.isfinite(value)` | OverflowError for huge ints | Catch OverflowError, raise ConfigError | 10**400 args rejected with ConfigError | All valid constructions |
| 4 | tests | missing tests for 1 and 2 | | Added as above | | |
| 5 | ratelimit/limiter.py | `_in_window`: `rel_tol=1e-9` | Tolerance scales with window: 30-day window admits 2 ms early | `abs_tol=4*math.ulp(now)`, `rel_tol=0` | 30-day window, 2 ms inside is denied | Fractional boundary test |
| 6 | ratelimit/limiter.py | NaN-clock and `except` paths skip `stats` | allowed + denied under-counts calls on failure | Count a denial on both paths (guarded) | stats after NaN clock and unhashable key | Happy-path stats |
| 9 | ratelimit/config.py | `_positive_int` / `_positive_float` | `"4.0"` rejected while `4.0` accepted; `b"4"` and `"1_0"` accepted | Accept only int, float, str; reject `_` in strings; parse str via float then require integral | `"4.0"` -> 4; `b"4"`, `"1_0"` rejected | `test_values` (`"2.5"`, `"4"`, 30) |
| 10 | ratelimit/config.py | `isinstance(raw, dict)` | Non-dict Mappings rejected despite docstring | `collections.abc.Mapping` | UserDict accepted | `test_not_mapping` (list rejected) |
