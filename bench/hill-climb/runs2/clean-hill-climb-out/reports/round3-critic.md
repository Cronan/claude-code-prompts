**3 blocking, 6 misleading, 3 minor**

Verifier: `python3 -m pytest -q` → `45 passed in 0.19s`.

### Blocking

1. **`ratelimit/config.py:44`** `burst = int(raw_burst)`. The non-whole-number check on line 40 only looks at `float`, so `Decimal("2.9")` and `Fraction(5,2)` are quietly cut down to `burst=2`. That is exactly what you get from `json.loads(..., parse_float=Decimal)`. Fix: reject the value when `raw_burst != int(raw_burst)`, whatever its type.

2. **`ratelimit/config.py:43-45`** `float(...)`/`int(...)` accept bytes (`b"2"` → 2.0) and strings like `" 1_0 "` (→ 10.0). README:13 says wrong types are rejected, but `tests/test_config.py:11` requires `"2.5"` to be accepted. So I'd need to ask the author whether strings are allowed at all. Bytes are a wrong type either way. Fix: before converting, raise `ConfigError` unless the value is an `int`, `float` or `str`.

3. **`ratelimit/limiter.py:22-24`, `61-63`** The constructors check nothing. `RateLimiter(float("nan"), 2)` let 5 of 5 calls through, because `min(burst, nan)` returns `burst`, so the bucket never empties. That breaks "never admits more than its limit". `RateLimiter(-1, 3)` admits; `SlidingWindow(2.5, …)` let 3 through. Configuration accepted here never reaches `ConfigError`. Fix: run the `load_config` checks in each `__init__`.

### Misleading

4. **`tests/test_limiter.py:120`, `127`, `179`, `188`** With the lock replaced by a no-op, these four "never exceeds" tests still pass, 3 runs out of 3. Only the `YieldingKey` tests (152, 159) fail without the lock. Fix: add a docstring saying they don't detect a missing lock, or remove them.

5. **`ratelimit/limiter.py:45-46`, `80-81`** `except Exception: return False` hides the error: nothing is logged and `stats["denied"]` doesn't go up. After a clock failure, stats still read `{'allowed': 1, 'denied': 0}`. In production you'd see every request denied and no signal of why. Fix: call `log.exception` and add `stats["errors"]`.

6. **`ratelimit/limiter.py:61-66`** `SlidingWindow` has no `stats` attribute, but the frozen interface lists `stats`. I can't tell which class it applies to, so this needs the author. Fix: add `stats` to `SlidingWindow`, or write down that only `RateLimiter` has it.

7. **`ratelimit/limiter.py:36-39`** If the clock goes backwards, `elapsed` goes negative. A 100s step back left the bucket at `(-100.0, 0.0)`, and the key was denied until the clock got back to where it was. This fails closed, but a `time.time` clock stepped by NTP would lock keys out, and no test covers it. Fix: `elapsed = max(0.0, now - last)` and never move `last` backwards.

8. **`ratelimit/limiter.py:56-58`** The docstring's exact-edge rule is correct (I checked it at t=10.0), but no test covers it: `tests/test_limiter.py:61` advances 11.0. A change from `>` to `>=` would pass every test. Fix: add a test that advances exactly `window`.

9. **`ratelimit/limiter.py:39`, `42`, `76`, `78`** State is stored for every key ever seen, including denied keys and empty stamp lists, and is never removed. Spraying many keys grows memory without limit. Fix: delete empty logs and buckets that are full again.

### Minor

10. **`ratelimit/config.py:12-15`** It's unclear how `Config` maps onto `SlidingWindow(limit, …)`; maybe `burst` is the limit. Needs the author. Fix: document it in the `load_config` docstring.

11. **`ratelimit/config.py:40-44`** `4.0` is accepted but `"4.0"` is rejected. Fix: parse string bursts with `float` first, then check for a whole number.

12. **`ratelimit/limiter.py:48-50`, `83-85`; `config.py:31`** `reset([])` raises `TypeError` while `allow([])` returns False. `isinstance(raw, dict)` rejects `MappingProxyType` even though the docstring says "a mapping". Fix: catch `TypeError` in `reset`, and check against `collections.abc.Mapping`.

### Files and checks with no findings

- `README.md`, `pytest.ini`, `ratelimit/__init__.py`: fine apart from the contradiction in item 2.
- `tests/test_config.py`: fine apart from missing Decimal and bytes cases.
- `allow` holds the lock across every read-compute-write, clock read included.
- Burst of 1 and a token at exactly 1.0 (rates 0.1, 0.3, 0.5, 0.7, 3.0) behave correctly.
- In `load_config`, overflow, NaN and infinity all raise `ConfigError`.
