6 blocking, 4 misleading, 3 minor

The verifier passes: `python3 -m pytest -q` → 64 passed. Every finding below comes from a probe I ran against the library.

**ratelimit/limiter.py**

1. **Blocking.** `now = self.clock()` is read before `with self._lock:` in both `allow` methods. That timestamp gets old while the thread waits for the lock. In the probe, thread A read t=0 and blocked on the lock; it got the lock at t=5. For `RateLimiter(1.0, 1)`, A was admitted with `last=0`, and then B at t=5 refilled a full token, so two requests went through at t=5 with burst=1. For `SlidingWindow(1, 10)`, A's entry was logged as 0 instead of 5, so a second request at t=10 was admitted only 5s after A. Both cases admit more than the limit under contention. Fix: read the clock inside the lock.
2. **Blocking.** `tokens = min(float(self.burst), tokens + elapsed * self.rate)` adds up rounding error. With rate=0.1, burst=1 and a poll every 1s, the next request is admitted at t=11 instead of t=10. The 0.5 test only passes because 0.5 is exact in binary. Fix: compare `tokens >= 1.0 - 1e-9`, or work out tokens from the time of the last admission.
3. **Blocking.** `if not math.isfinite(value):` raises `OverflowError`, not `ConfigError`, for large ints: `RateLimiter(10**400, 1)`, `RateLimiter(1.0, 10**400)` and `SlidingWindow(10**400, 1.0)` all do this. Fix: catch `OverflowError` in `_check_number` and raise `ConfigError`.
4. **Blocking (missing test).** No test covers a clock read that is out of date by the time the lock is taken (#1), or a rate like 0.1 (#2). Fix: add both cases using a lock held by the test and a FakeClock.
5. **Misleading.** `if math.isclose(age, self.window, rel_tol=1e-9):` sets the tolerance relative to the window size, but the rounding error depends on how large `now` is. With a 30-day window, a request 2 ms *inside* the window was admitted. Fix: use `abs_tol=4*math.ulp(now)` and `rel_tol=0`.
6. **Misleading.** `return False` on the NaN-clock path and in `except Exception:` never update `stats`. After a NaN-clock call and an unhashable-key call, `stats` was still `{'allowed': 0, 'denied': 0}`. So `allowed + denied` stops matching the number of calls exactly when something fails. Fix: increment `denied` on both paths.
7. **Misleading.** `self.stats = {"allowed": 0, "denied": 0}` hands out the live dict without the lock, so a caller can read the two counts mid-update or change them. Also, `SlidingWindow` has no `stats` at all, even though `stats` is listed as frozen public API. I would need the author to say which class `stats` is meant for. Fix: add a `stats` property that returns a copy taken under the lock.
8. **Misleading.** `_check_number("burst", burst, allow_zero=True)` and `_check_number("limit", limit, allow_zero=True)` accept 0, while `load_config` rejects `burst: 0`. The README says non-positive values are rejected. The frozen test `test_zero_burst_and_zero_limit_deny_everything` requires 0 to be accepted, so this needs the author to rule on it. Fix: document that zero means "deny all" in the README and both docstrings.

**ratelimit/config.py**

9. **Blocking.** `result = int(value)` rejects `"4.0"`, but `4.0` is accepted. It also accepts `b"4"` (gives burst=4) and `"1_0"` (gives 10). The README says wrong types are rejected. Fix: allow only `int`, `float` and `str`, and parse strings with `float()` before checking they are whole.
10. **Blocking.** `if not isinstance(raw, dict):` rejects `UserDict` and any other non-dict mapping, although the docstring says "a mapping such as parsed JSON or YAML". Fix: check `isinstance(raw, collections.abc.Mapping)`.
11. **Minor.** `if not math.isfinite(as_float) or as_float != result:` gives `2**53+1` the error "must be a whole number". The rejection is fine but the message is wrong. Fix: compare `int(as_float) == result` and give a precision error.
12. **Minor.** `class Config:` does not validate itself: `Config(rate=-1, burst=0, window=nan)` builds without error. Fix: validate in `__post_init__`.
13. **Minor.** Both `self._buckets` and `self._log` grow by one entry per key and are never cleared. `SlidingWindow` stores an empty list even for keys it denies. Fix: drop keys that are full or empty.

**tests/test_limiter.py**

14. **Blocking (test cannot fail).** `assert total == 500` in `test_token_bucket_never_over_admits_under_contention` still passed in 5 of 5 runs after I swapped the lock for `nullcontext()`, so it does not detect a missing lock. Only the `_YieldingKey` test does. Fix: use `_YieldingKey`, or delete the test as redundant.

The other checks hold:
- Burst of 1, sub-second polling and the exact-`window` boundary all behave correctly.
- Every validation the docstring lists is enforced.
- The fail-closed `except` covers every path where `allow` could otherwise return True.

**tests/test_config.py**: fine apart from the gaps in #3 and #9 (large ints, bytes, "4.0", non-dict mappings).

`ratelimit/__init__.py` and `pytest.ini` are fine.
