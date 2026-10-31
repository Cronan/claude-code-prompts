Findings, most severe first. I found no correctness bug in the main admit path.

1. **`ratelimit/limiter.py:67` (`RateLimiter._deny_on_error`) and `:123` (`SlidingWindow.allow`): the logging call in the fail-closed handler can itself raise.**
   - In `RateLimiter`, `log.warning(..., exc_info=True)` is the first line of `_deny_on_error`, outside its inner `try`. In `SlidingWindow` it sits unguarded inside the `except` block.
   - Scenario: the clock raises while a `logging.Filter` or handler on `ratelimit.limiter` also raises (a `Filter.filter` exception propagates, and so would a `RecursionError`). `allow()` then raises instead of returning False, which breaks acceptance item 3 ("any exception inside `allow()` results in False").
   - The inner `try` only protects the stats update, so the guard covers the wrong part.
   - A related problem: every failing call logs a full traceback. A caller feeding unhashable keys in a loop floods the log, and each of those calls pays for formatting the traceback.

2. **`ratelimit/limiter.py:31-35, 94-98`: scope creep that breaks the frozen constructors (items 5 and 6).**
   - The change adds constructor validation. Item 4 only requires this for `load_config`.
   - It also coerces `self.rate`, `self.burst`, `self.limit` and `self.window`, and imports the private helper `_number` across modules.
   - Scenario: `RateLimiter(rate=1, burst=1.5)` or `RateLimiter(rate=Decimal("0.5"), burst=2)` used to construct. Now they raise `ConfigError`.
   - `RateLimiter(rate="2", burst="3")` previously stored strings, which then failed closed on every call. Now it silently becomes 2.0 and 3.
   - `RateLimiter.stats["denied"]` now also counts error denials (`limiter.py:70`), which is a behaviour change not in the list.
   - The logging added at `:15, :67, :123` is also outside the five items.

3. **`ratelimit/config.py:33`: `_number` narrows what the old `float()`/`int()` path accepted.**
   - `isinstance(value, (numbers.Real, str))` rejects `Decimal`, because it is not a `Real`. It also rejects `bytes`.
   - Scenario: `load_config({"rate": Decimal("0.5")})` was accepted before and now raises `ConfigError`.
   - Strings like `"1_0"` (which `float()` reads as 10.0) and `" 5 "` are accepted. This is probably fine, but no test pins it.

4. **`ratelimit/config.py:52`: `isinstance(raw, dict)` is stricter than "mapping".**
   - This line was already there before the change.
   - Scenario: `load_config(types.MappingProxyType({"rate": 0.5}))` or any other non-`dict` `Mapping` raises `ConfigError("config must be a mapping")`. That is a valid mapping being rejected.

5. **`ratelimit/limiter.py:39, 57-60`: `stats` is a live public dict.**
   - Callers read `rl.stats` without the lock while worker threads write to it. Item 1 asks for all `stats` reads to happen under the lock, and there is no locked accessor.
   - Scenario: a monitoring thread reads `rl.stats` mid-update and sees a count that doesn't match the other.

6. **`ratelimit/limiter.py:37, 100`: per-key state is never evicted (existing issue, item 2 resource cleanup).**
   - Scenario: a stream of unique keys, such as client IPs, grows `_buckets` and `_log` without bound until `reset(key)` is called for each one.

7. **Tests (`tests/test_limiter.py`, `tests/test_config.py`): coverage and style gaps.**
   - `tests/test_limiter.py:73-79` puts `import logging/threading/pytest` and the `ConfigError` import in the middle of the file, after the original tests. This does not match the file's style.
   - The two concurrency tests use a frozen `FakeClock`, and `RateLimiter.allow` already held the lock around its clock read. So `test_rate_limiter_concurrent_never_exceeds_burst` would pass on the original code and doesn't pin the change. Only `test_clock_read_under_lock` covers the `SlidingWindow` fix.
   - There is no test for "arithmetic on bad values" in `allow()`, for example `rl.rate = "x"` or a clock returning `None` or a string.
   - There is no test that `allow()` still returns False when logging itself raises (finding 1).
   - The only non-mapping config test is the pre-existing `[1, 2]`. `None`, `str` and other non-dict mappings are untested.
