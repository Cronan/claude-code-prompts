1. **CONFIRMED AT blocking.** `load_config({"burst": Decimal("2.9")})` and `Fraction(5,2)` return `burst=2`. `Decimal("2.5")` also truncates silently. README requirement 4 says invalid config is rejected, and the line-40 check only covers `float`.

2. **CONFIRMED AT blocking.** `b"2"` gives `burst=2` and `rate=2.0`. `" 1_0 "` gives 10 for both `burst` and `rate`. Bytes are a wrong type under requirement 4, and the existing tests don't cover them.

3. **CONFIRMED AT misleading.**
   - `RateLimiter(nan, 2)` admits 5 of 5 calls.
   - `RateLimiter(-1, 3)` admits 3 and then denies.
   - `SlidingWindow(2.5, 10)` admits 3.
   - README requirement 4 is about configuration, and `load_config` rejects NaN, non-positive and non-finite values. The bad values only get through when the constructors are called directly, so I rank this below blocking.

4. **CONFIRMED AT misleading.** I replaced the limiter's lock with a no-op and ran `tests/test_limiter.py`. Only the two YieldingKey tests failed (SlidingWindow gave 80 against a limit of 20). The other four never-exceeds tests passed, so they don't check the lock.

5. **CONFIRMED AT misleading.** With the clock raising after one allowed call, `allow` returned False and `stats` stayed `{'allowed': 1, 'denied': 0}`. Nothing is logged. It still fails closed, so the requirement holds.

6. **CONFIRMED AT misleading.** `hasattr(SlidingWindow(...), "stats")` is False. The code has no `stats` for `SlidingWindow`, and the README doesn't say it should. Whether this counts as a defect depends on reading "frozen interface lists stats" as applying to both classes. No test covers it.

7. **CONFIRMED AT misleading.** The clock stepped back from 100 to 0 after one call on a burst-2 bucket. The bucket became `(-99.0, 0.0)` and the key was denied. At t=100 it was allowed again. The claim's figure of -100.0 is slightly off, because the bucket held 1 token, so it is -99.0. The behaviour is as claimed, and `time.monotonic` normally prevents it. No test covers it.

8. **CONFIRMED AT misleading.** The only advance in the SlidingWindow test is 11.0, at line 61 of `tests/test_limiter.py`. Nothing tests the exact-window edge, which the docstring specifies. I did not mutate `>` to `>=` to confirm that the suite passes, but no test exercises an advance of exactly 10.0, so it would pass.

9. **CONFIRMED AT misleading.** `_buckets` and `_log` get an entry for every key that is allowed or denied, and only `reset` removes one. The stale-entry growth is real. The README makes no memory requirement, so it is only a maintainability concern.

I ran the verifier: 45 passed. Nothing in the repository was edited. My probe scripts are in the scratchpad.
