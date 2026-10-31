1. **CONFIRMED.** A probe over 999 timestamps with `now = t0 + 10.0` denied 84 of them, matching the claim. The docstring says a request exactly `window` seconds old no longer counts.

2. **CONFIRMED AT Misleading.** The behaviours are real: `SlidingWindow(2,-5)` and `SlidingWindow(2,nan)` admitted all 5 of 5 calls, `RateLimiter(nan,3)` admitted all 10 of 10, and `RateLimiter("1",3)` gave `[True, False, False, False]`. But these are direct constructor inputs. The README puts validation in `load_config`, which does reject these values, and the verifier does not cover direct construction. It is not Blocking.

3. **CONFIRMED.** With `_lock` replaced by `nullcontext()`, 30 runs each of the token-bucket and sliding-window contention tests showed 0 over-admissions. Neither test would catch a missing lock, so the thread-safety requirement has no effective test.

4. **CONFIRMED AT Misleading.** With a clock that always returns NaN, `SlidingWindow(1,10)` admitted all 3 calls (`[True, True, True]`). That is fail-open, but it needs a faulty injected clock and the verifier does not exercise it.

5. **NOT CONFIRMED.** `Config` has no `limit` field, but nothing in the README or the frozen API says `Config` must map to `SlidingWindow`. `load_config` returns validated `rate`, `burst` and `window` and builds no limiter. The claim describes a missing feature, not a defect.

6. **NOT CONFIRMED.** `hasattr(SlidingWindow(1,1), 'stats')` is `False`, so the observation is accurate. However, the README never requires `stats` on `SlidingWindow`, and the frozen API signature list pairs `stats` with `RateLimiter`'s counters. The claim is about an unstated requirement.

The verifier passes with 41 tests.
