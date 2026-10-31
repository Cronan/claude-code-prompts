**2 blocking, 7 misleading, 1 minor**

Verifier: `python3 -m pytest -q` gives **40 passed**. I checked each claim below with a probe script; I edited nothing.

**Blocking**

1. `ratelimit/config.py:35` (`raise ConfigError(f"unknown keys: {sorted(unknown)}")`): if the unknown keys mix types, such as `{1: 2, "x": 3}`, `sorted` itself raises `TypeError`, so the caller gets `TypeError` instead of `ConfigError`. This breaks requirement 4. Fix: `sorted(map(repr, unknown))`.
2. `ratelimit/config.py:39-44` (the float-only whole-number check before `burst = int(raw_burst)`): `Fraction(5,2)` and `Decimal("2.9")` are silently cut down to `burst=2`, though `2.9` as a float is rejected. Fix: reject any value where `int(x) != x`, or require `isinstance(raw_burst, (int, str))`.

**Misleading**

3. `ratelimit/config.py:43-45` and `tests/test_config.py:7`: strings such as `"2.5"`, `" 2 "` and `b"1.5"` are accepted, and an existing test locks that in. The README says "wrong types" are rejected. I need the author to say which is right. Meanwhile `"4.0"` is rejected for burst while `4.0` is accepted. Fix: write the accepted string forms into the README.
4. `ratelimit/limiter.py:26-29` and `65-68`: the constructors validate nothing. `RateLimiter("1", 5)` denies every request with no error. `RateLimiter(-1, 5)` drains the bucket. `SlidingWindow(2.5, 10)` admits 3 requests. Is requirement 4 meant to apply only to `load_config`? I'd have to ask. Fix: run the same checks in `__init__` and raise `ConfigError`.
5. `ratelimit/limiter.py:49-50` and `84-85` (`except Exception: return False`): this also swallows caller bugs. An unhashable key (`allow(["x"])`) or a wrong-typed rate gives a silent `False`, the error is never logged, and `stats` is not updated (it stays `{'allowed': 0, 'denied': 0}`). A service would just look like it is throttling. Fix: log the exception and add `stats["errors"] += 1`.
6. `ratelimit/limiter.py:32`: `stats` is the live internal dict. Callers read and change it without the lock, for example to reset counters, and there is no snapshot accessor. `SlidingWindow` has no `stats` at all, although the frozen API lists `stats` without saying which class owns it. Fix: make `stats` a property that returns `dict(...)` under the lock, and ask the author whether `SlidingWindow` should have one.
7. `ratelimit/config.py:15-18`: `Config` has no `limit` field. So you cannot tell from the code how a `SlidingWindow` is built from config (does `burst` become `limit`?). I'd have to ask the author. Fix: document the mapping, or add `limit`.
8. `tests/test_limiter.py:120-130`: both concurrency tests use a `FakeClock` that never moves. So refill is never tested while threads contend, and 8×100 calls under the GIL probably wouldn't reveal a race even with the lock removed. Requirement 1 is effectively untested. Fix: advance the clock from a separate thread, and run more iterations with `sys.setswitchinterval(1e-6)`.
9. Requirements and boundaries with no test:
   - exact window edge: `limiter.py:77` (`t > cutoff`) is correct for the docstring, but untested;
   - clock going backwards: `limiter.py:40` (negative `elapsed`) lowers the token count, which is safe, but untested;
   - fail-closed for any failure other than the clock;
   - `RateLimiter` with `rate=inf` or `nan` passed directly: `nan` denies everything, and `inf` admits everything because `min(burst, nan)` returns `burst`;
   - nested-mapping `burst` and a `dict`-like `Mapping` that is not a `dict` (`config.py:31` uses `isinstance(raw, dict)` although the docstring says "mapping").

   Fix: add one test for each.

**Minor**

10. `ratelimit/limiter.py:30` and `69`: `_buckets` and `_log` are never cleaned out, so memory grows without limit as new keys arrive. On top of that, `SlidingWindow.allow` rebuilds the whole list on every call while holding the lock (line 77). Fix: evict stale keys, and use a `deque` with `popleft`.

**Files with no findings**
- `ratelimit/__init__.py`: fine.
- `pytest.ini`: fine.
