# Round 1 fix list (from round1-reviewer.md)

1. limiter.py: both `allow()` except handlers return True -> return False (fail closed). Count the denial in stats where possible, never let the handler itself raise.
2. limiter.py: RateLimiter.allow does read-modify-write and stats updates outside `_lock` -> hold the lock for the whole allow() body; remove `_snapshot`.
3. limiter.py: `int(elapsed * rate)` truncates fractional refill and `last` is rewritten on every call, so sub-1/s rates starve -> store tokens as float, refill `tokens + elapsed * rate` (clamped to burst, negative elapsed clamped to 0), admit when tokens >= 1.
4. config.py: validation missing -> reject bool, None, list/dict and other non-numeric types; reject NaN/inf; reject non-positive rate, burst, window; reject fractional burst; reject unknown keys (use KNOWN_KEYS). Numeric strings stay accepted because the frozen `test_values` requires `"2.5"`/`"4"` to load; a string must parse cleanly (a non-integer string for burst is rejected).
5. limiter.py: constructors accept rate=0, burst=-1, limit=0, window=-1, None -> validate in `__init__` and raise ConfigError (a ValueError subclass) so a bad limiter cannot be built and then fail at allow() time.
6. SlidingWindow: except path fails open -> covered by item 1. Unbounded key growth: not fixed; a keyed limiter with no TTL/eviction API is outside the four README requirements and adding one would be scope creep. Recorded as not fixed.
7. tests/test_limiter.py: `test_refill` is vacuous -> make it stricter (assert True after 1.0s); the brief permits making tests stricter.
8. No tests for the new requirements -> add: sub-1/s refill scenario, raising clock denies (both limiters), concurrency test (many threads, one key, admitted == limit) for both limiters, constructor validation, config rejection cases (bool, None, list, zero/negative burst and window, unknown key, NaN, fractional burst, non-integer burst string).
9. Hygiene: `__pycache__` directories are byproducts of running the verifier (not committed, not in the diff); removed after each run. README already states the requirements; no change needed once the code meets them.
