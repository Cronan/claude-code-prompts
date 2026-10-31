**Tally: 8 blocking, 2 misleading, 1 minor.**

The verifier passes (`12 passed`), but it tests none of the four README requirements. My probes broke three of them directly: the limiter fails open, a 0.5/s rate is unusable, and bad config is accepted. The thread-safety requirement fails by reading the code; my stress run did not reproduce the race.

**Blocking**

1. **`ratelimit/limiter.py:93-94` and `:128-129`.** `except Exception: return True` fails open, which breaks the fail-closed requirement. A clock that raises made both limiters return True. Fix: `return False` (and count it as denied).
2. **`limiter.py:84`** `tokens = min(self.burst, tokens + int(elapsed * self.rate))`, plus `:87` and `:90` writing `(tokens, now)`. `int()` throws away the fractional token, and resetting `last` on every call (denials included) throws away the time that has built up. With rate 0.5 and burst 1, polling once a second for 10 s was denied all 10 times. Any polling faster than `1/rate` starves the key for good. Fix: store tokens as a float and add `elapsed * rate` without truncating.
3. **`limiter.py:82-91`** `tokens, last = self._snapshot(key, now)`, then `self._buckets[key] = ...` and `self.stats[...] += 1` run outside the lock. Two threads can read the same snapshot and both spend the last token, which is double admission. Stats updates can also be lost. My 16-thread stress run under this interpreter didn't trigger it, but that luck depends on the GIL. Fix: hold `self._lock` around the whole read-compute-write.
4. **`limiter.py:121`** `if t >= cutoff`. A request exactly `window` seconds old still counts, which contradicts the docstring at `:105-106`. The probe confirmed it: at t=10 with window 10, the call was denied. Fix: `t > cutoff`.
5. **`ratelimit/config.py:42-44`** `if rate <= 0:` is the only range check:
   - `burst` of 0 or -5 is accepted.
   - `window` of 0 or -1 is accepted.
   - `rate` and `window` accept nan, and `rate` accepts inf (`nan <= 0` is False).
   - `burst=inf` raises `OverflowError` instead of `ConfigError`, because `:40` doesn't catch it.

   Fix: check every field with `math.isfinite(x) and x > 0` and add `OverflowError` to the except.
6. **`config.py:25`** `KNOWN_KEYS = {"rate", "burst", "window"}` is never used, so `{"bogus": 1}` loads without complaint. Fix: `if set(raw) - KNOWN_KEYS: raise ConfigError(...)`.
7. **`config.py:37-38`** `float(raw.get("rate", 1.0))` / `int(raw.get("burst", 10))`. `True` is accepted (it becomes rate 1.0 or burst 1), and `burst=2.9` is silently cut to 2. Fix: reject `bool`, and reject any non-integral `burst`.
8. **`tests/test_limiter.py:61`** `assert rl.allow("a") in (True, False)` can never fail. More broadly, no test covers concurrency, fail-closed, fractional rates, the window boundary, or any config check other than a bad or zero `rate`. Fix: tighten it to `assert rl.allow("a")`, and add one test per README requirement.

**Misleading**

9. **`tests/test_config.py:11`** `load_config({"rate": "2.5", "burst": "4", "window": 30})`. This frozen test requires that numeric strings be accepted. The README says "wrong types… rejected". I can't tell whether `"2.5"` counts as a wrong type, so this needs the author. Fix: write the accepted type set (numbers plus numeric strings, not bool) into the README.
10. **`limiter.py:66-69`** and **`:109-111`**: the constructors don't validate anything. `RateLimiter(1, 0)` and `SlidingWindow(0, 1)` quietly deny every request, and negative values are accepted. Validation only happens in `load_config`. Nothing maps `Config` onto either limiter, and `Config` has no `limit` field for `SlidingWindow`, so I'm guessing that `burst` becomes `limit`. Fix: share the validator with the constructors, or say in the README that they don't validate.

**Minor**

11. **`limiter.py:72`** `self.stats = {...}` exists only on `RateLimiter`. The frozen-API list says `stats` without naming a class. Fix: say in the README which class has it.

`ratelimit/__init__.py` and `pytest.ini` are fine.
