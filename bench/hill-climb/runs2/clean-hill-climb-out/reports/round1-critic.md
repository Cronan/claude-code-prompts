**10 blocking, 8 misleading, 2 minor**

**I could not run the verifier.** Both `python3 -m pytest -q` and a probe script stopped at the approval prompt and never ran, so no test result is reported here. Every finding below comes from reading the code.

### ratelimit/limiter.py
1. **Blocking, line 37.** A NaN rate admits every request. `min(float(self.burst), nan)` returns `burst`, because `nan < burst` is False, so the bucket refills to full on every call. An infinite rate does the same at line 37: `0 * inf` gives NaN. Fix: reject a rate that is not finite or is ≤ 0 in `__init__` (lines 22–25).
2. **Blocking, lines 71/73.** A NaN window gives `cutoff = nan`. `t > nan` is always False, so the log is emptied and every request is admitted. Fix: validate the window in `__init__` (line 61).
3. **Blocking, line 70.** `self.clock()` is read outside the lock. A thread that is preempted logs an old timestamp, which then leaves the window early. That lets more than `limit` requests through in a real window when threads contend, which breaks the first README requirement. Fix: move line 70–71 inside the `with self._lock:` block.
4. **Misleading, lines 28/40/43.** `stats` is the live mutable dict. Callers read it without the lock and can change it. The error path at line 45 does not count the denial, and `reset` leaves the stats alone. Fix: a property that returns a copy taken under the lock, and count the denial in `except`.
5. **Misleading, lines 61–66.** `SlidingWindow` has no `stats`, but `stats` is on the frozen-behaviour list. I would ask the author which classes it covers.
6. **Misleading, lines 45/80.** `except Exception: return False` hides every error. A limiter built with a bad value such as `RateLimiter("0.5", 1)` denies 100% of requests and gives no sign of why. Fix: call `logging.exception` before returning False.
7. **Misleading, lines 48/83.** `reset` is not wrapped the same way. An unhashable key raises in `reset` but quietly returns False in `allow`. Fix: handle both the same way.
8. **Misleading, line 36.** When the clock goes backwards, `elapsed` is negative and drains tokens. The naive fix (clamp `elapsed` to 0 but still store `last = now`) would admit too many once the clock moves forward again. Fix: `elapsed = max(0.0, now - last)` and store `max(last, now)`. Nothing tests this.
9. **Misleading, line 73.** The docstring's "exactly `window` ago" rule depends on the float result of `now - self.window`. For example, `0.3 - 0.2 < 0.1`, so a request made exactly a window ago still counts. Nothing tests this edge. Fix: add a test with a non-integer window.
10. **Misleading, lines 26/65.** `_buckets` and `_log` keep every key forever, including empty lists. In a service with many keys, memory grows without limit. Fix: delete empty logs and evict idle buckets.
11. **Minor, line 37.** Repeated float addition at fractional rates can leave 0.999… tokens, so a request is denied slightly early. Fix: compare with a small epsilon.

### ratelimit/config.py
12. **Blocking, lines 41–46.** `"nan"` and `"inf"` pass the `<= 0` checks and reach findings 1 and 2. Fix: `if not math.isfinite(rate) or rate <= 0`, and the same check for the window.
13. **Blocking, line 37.** `int(float("inf"))` raises `OverflowError`, which is not caught at line 39. Fix: `except (TypeError, ValueError, OverflowError)`.
14. **Blocking, lines 36–38.** `True` becomes 1.0 or 1, and `burst: 2.9` is silently cut to 2. Both are wrong types that get accepted. Fix: reject `bool`, and reject a non-integral `burst`. I would need to ask the author first: `test_values` (test_config.py:11) requires the strings `"2.5"` and `"4"` to be accepted, which contradicts "wrong types are rejected". `None`, lists and nested dicts are rejected correctly.
15. **Misleading, lines 15–18.** `Config` has no `limit`, so it cannot be used to build `SlidingWindow(limit, window)`. I would ask the author whether `burst` is meant to be the limit.
16. **Minor, line 30.** `isinstance(raw, dict)` rejects mappings that are not dicts, even though the docstring says "mapping". Fix: use `collections.abc.Mapping`.

### Tests: one blocking item per README requirement with no test
17. **Blocking, tests/test_limiter.py.** No test hits one key from many threads.
18. **Blocking, tests/test_limiter.py.** No test uses a fractional rate, for example 0.5.
19. **Blocking, tests/test_limiter.py.** No test has a clock that raises to check that requests are denied.
20. **Blocking, tests/test_config.py.** There are no tests for unknown keys, a negative or zero `burst`/`window`, a negative rate, bool, None, list, NaN or inf values, or `OverflowError`.

`ratelimit/__init__.py` and `pytest.ini` are fine.
