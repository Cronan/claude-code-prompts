1. CONFIRMED AT misleading. `RateLimiter(nan, 1)` and `RateLimiter(inf, 1)` admit every request in a probe, but only through direct construction. The verifier doesn't cover that, and the `load_config` route is item 11.
2. CONFIRMED AT misleading. `SlidingWindow(1, nan)` admitted 3 of 3 requests in a probe. It is reachable only by direct construction or through item 11.
3. CONFIRMED AT blocking. `now = self.clock()` at line 70 runs before `with self._lock`. A preempted thread can append an old timestamp after newer ones, so that entry expires early. That breaks the README's never-over-limit requirement. I didn't reproduce the race, only read it from the code.
4. CONFIRMED AT misleading. `stats` is a plain dict read without the lock. The `except` path returns False without incrementing `denied`. `reset` doesn't touch `stats`.
5. CONFIRMED AT misleading. `hasattr(SlidingWindow(...), 'stats')` is False.
6. CONFIRMED AT misleading. `RateLimiter("0.5", 1)` hits a TypeError on `elapsed * "0.5"`, which is swallowed and returns False, with no log or signal.
7. CONFIRMED AT misleading. `RateLimiter(1,1).reset([])` raises TypeError, while `allow([])` returns False.
8. CONFIRMED AT misleading. A negative `elapsed` at line 36 subtracts tokens, and no test covers a backwards clock. It matters little with `time.monotonic`, the default.
9. CONFIRMED AT misleading. `now=0.3, window=0.1` gives a cutoff of 0.19999999999999998, so a stamp at 0.2 still counts, although it was exactly one window ago. No test covers it.
10. CONFIRMED AT misleading. Neither `_buckets` nor `_log` ever removes a key, apart from `reset`. `_log` keeps empty lists too.
11. CONFIRMED AT blocking. `load_config({'rate':'nan'})`, `{'rate':'inf'}` and `{'window':'nan'}` all return a Config with non-finite values, because `nan <= 0` is False.
12. CONFIRMED AT blocking. `load_config({'burst': float('inf')})` raises OverflowError, not ConfigError. (`burst=nan` is fine: ValueError is caught.)
13. CONFIRMED AT blocking. `{'burst': True}` and `{'rate': True}` are accepted, and `burst=2.9` becomes 2. The string `'5'` is also accepted for burst, so numeric strings are coerced too.
14. CONFIRMED AT misleading. `Config` has only `rate`, `burst` and `window`, so there is no way to get a `SlidingWindow` limit from it.
15. CONFIRMED AT blocking. `grep` finds no thread usage in `tests/`, so the thread-safety requirement has no test.
16. CONFIRMED AT blocking. `grep` finds no `0.5` or other fractional rate in `tests/`.
17. CONFIRMED AT blocking. No test passes a clock that raises, so fail-closed is untested.
18. CONFIRMED AT blocking. `test_config.py` has only 6 tests (defaults, values, not-mapping, bad rate type, zero rate). None cover unknown keys, zero or negative burst or window, negative rate, bool, None, list, NaN or inf, or OverflowError. The README requires unknown keys to be rejected, so that case is untested.

The verifier passes: 12 tests, all green.
