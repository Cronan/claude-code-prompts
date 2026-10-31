1. **CONFIRMED.** `now = self.clock()` is read before `with self._lock:` in both `allow` methods. Two probes with a fake clock replayed the sequence. The token bucket (rate 1.0, burst 1) with a stale t=0 stamp then a t=5 call admitted both. SlidingWindow(1, 10) admitted a request at t=10 when the first was logged at 0 instead of 5. This is a real over-admission against the README's "never admits more than its limit".

2. **CONFIRMED.** RateLimiter(0.1, 1), polled every 1 s after the first admit, next admitted at t=11, not t=10.

3. **CONFIRMED.** All three calls (`RateLimiter(10**400, 1)`, `RateLimiter(1.0, 10**400)`, `SlidingWindow(10**400, 1.0)`) raise `OverflowError` instead of `ConfigError`.

4. **CONFIRMED.** I found no test with a stale clock-versus-lock ordering or a 0.1 rate (the `0.1` grep hit is only a start-offset loop in a sliding-window test).

5. **CONFIRMED AT Misleading.** SlidingWindow with a 30-day window and a request 2 ms before expiry was admitted (`True`). The relative tolerance is about 2.6 ms there. This is not covered by the verifier, and it only affects the boundary.

6. **CONFIRMED AT Misleading.** With a NaN clock, `allow` returns False and `stats` stays `{'allowed': 0, 'denied': 0}`. The `except` path has the same gap. Fail-closed still holds, so only the accounting is off.

7. **CONFIRMED AT Misleading.** `stats` is a plain live dict on RateLimiter, and SlidingWindow has no `stats` (`hasattr` is False). The README doesn't promise a stats API. Counter increments are done under the lock.

8. **CONFIRMED AT Misleading.** `RateLimiter(1, 0)` and `SlidingWindow(0, 1)` construct, while `load_config({"burst": 0})` raises. `test_zero_burst_and_zero_limit_deny_everything` requires the constructors to accept zero. The README sentence is ambiguous, but the inconsistency between the two paths is real.

9. **CONFIRMED.** `"4.0"` is rejected, `4.0` gives 4, `b"4"` gives 4 and `"1_0"` gives 10. Bytes and underscore strings are accepted, though the docstring only promises numbers or numeric strings, so the "wrong types" claim is strongest for bytes. Rejecting `"4.0"` while accepting `4.0` is the inconsistent part.

10. **CONFIRMED.** `load_config(collections.UserDict({}))` raises `ConfigError("config must be a mapping")`, but the docstring says "a mapping".

11. **NOT CONFIRMED.** I replaced each limiter's `_lock` with `nullcontext()` in memory. `test_sliding_window_never_over_admits_under_contention` failed 5 out of 5 runs, so that test does detect the missing lock. `test_token_bucket_never_over_admits_under_contention` passed 5 out of 5, so the claim holds for the token bucket only. The bucket test cannot see a missing lock because the GIL rarely switches threads inside `allow`. Only the `_YieldingKey` tests catch it. The claim is therefore half right: it is wrong for the sliding window and right for the token bucket.
