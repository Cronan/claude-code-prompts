3 blocking, 3 misleading, 4 minor

Verifier: `python3 -m pytest -q` passes all 41 tests. Every finding below was checked with a probe against the library.

**Blocking**

1. `ratelimit/limiter.py:83`, `stamps = [t for t in self._log.get(key, []) if t > cutoff]`. The docstring says a request exactly `window` seconds old has left the window, but floating-point rounding in `now - self.window` breaks this. With a stamp at `t0=i*0.1` and `now=t0+10.0`, the second request was still denied in 84 of 999 cases. The existing boundary test passes only because it uses whole-number timestamps. Fix: keep a stamp only if `now - t < self.window`, and add a test with non-integral timestamps.

2. `limiter.py:26-28` and `71-73` (`self.rate = rate`, `self.window = window`, ...). The constructors don't check their arguments, and several bad values let every request through:
   - `SlidingWindow(2, -5)` admits every request.
   - `SlidingWindow(2, nan)` admits every request.
   - `RateLimiter(nan, 3)` admits every request, because `min(3.0, nan)` returns 3.0 and the bucket refills to full on each call.
   - `RateLimiter("1", 3)` admits once, then denies forever.
   
   This breaks "never admits more than its limit". `load_config` blocks these values, but anyone calling the constructors directly gets no protection. Fix: run the same positive-finite checks in `__init__` and raise `ConfigError`.

3. `tests/test_limiter.py:166-181`, the two contention tests. These can't catch a missing lock. I swapped `_lock` for `contextlib.nullcontext()` and ran each test 30 times: 0 of 30 runs over-admitted, for both classes. So nothing tests the thread-safety requirement. Fix: add a test whose key's `__hash__` calls `time.sleep(0)`, which forces a thread switch between the read and the write of the bucket, and assert the exact admitted count.

**Misleading**

4. `limiter.py:80-83`, `cutoff = now - self.window`. If an injected clock returns NaN, every `t > cutoff` is False, so the log is emptied and every call is admitted (`[True, True, True, True]`). That fails open on a fault the class is documented to deny. Fix: `if not math.isfinite(now): return False`.

5. `config.py:112-115`, `class Config: rate / burst / window`. Nothing configures `SlidingWindow.limit`. I'd have to guess whether `burst` is meant to be the limit, and limit 0 can't be expressed or rejected through config. Ask the author. Fix: add a `limit` field, or document the mapping.

6. `limiter.py:32`, `self.stats = {"allowed": 0, "denied": 0}`. Only `RateLimiter` has `stats`, while the frozen API lists `stats` without saying which class. Ask the author. Fix: add `stats` to `SlidingWindow`, or state that it is token-bucket only.

**Minor**

7. `config.py:139`, `result = int(value)`. The integral float `4.0` is accepted, but the string `"4.0"` is rejected, which contradicts the docstring's "numeric strings". `10**400` is also rejected, because converting it to a float overflows. Fix: parse with `float()`, then check `.is_integer()`.

8. `config.py:126`, `result = float(value)`. `b"2"` and `b"4"` are accepted as numbers, although the README says wrong types are rejected. Fix: reject anything that isn't `int`, `float` or `str`.

9. `limiter.py:49`, `self.stats["allowed"] += 1`. On the exception path neither counter goes up, so `allowed + denied` can fall short of the number of calls. `stats` is also a live dict that callers read without the lock. Fix: count a denial in the `except` block, and return a copy of `stats` taken under the lock.

10. `limiter.py:51` and `88`. Every key ever seen keeps an entry, including keys that were only ever denied, and nothing evicts them. Memory grows with the number of distinct keys. Fix: evict idle keys.

**Checked and fine**

- Reading the clock outside the lock (`limiter.py:37`, `80`) only makes the result stricter, never looser; I found no lost update or double admission.
- Fractional rates work: rate 0.1, polled every 0.1 s, refills exactly on poll 100. Burst 1 and limit 0 behave correctly.
- `load_config` rejects bools, NaN/inf, non-positive values for every field, and unknown keys.
- `__init__.py` and `pytest.ini` are fine.

**Coverage gaps**

- No test for constructor validation.
- No sliding-window test with sub-second or fractional timestamps.
- No test for a NaN or non-monotonic clock.
