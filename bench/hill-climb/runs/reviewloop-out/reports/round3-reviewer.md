**Findings (most severe first). Nothing blocks the six items; the main gaps are one tolerance issue and some unpinned or looser edge behaviour.**

1. **`ratelimit/limiter.py:158-159`, low.** Refill is compared as `available >= 1.0` with no tolerance. At an exact refill boundary, `elapsed * rate` can come out one ulp below 1.0.
   - Failure scenario: `RateLimiter(rate=0.36, burst=1)`, admit at t=0, then call at t=`1/0.36` (2.7777777777777777). `elapsed * rate` is 0.9999999999999999, so the call is denied when it should be admitted.
   - I swept `rate = n/100` for n from 1 to 1999. 285 rates miss this way, including sub-1/s rates 0.09, 0.18, 0.36, 0.41, 0.47, 0.72 and 0.91.
   - Item 2's example (0.5, burst 1, t=2.0) is exact and passes. Tests only use 0.5 and 0.25, so this is untested.

2. **`ratelimit/limiter.py:187-188, 136-138`, low (item 5).** The constructors now go through `coerce_int` and `coerce_float` and reject some values the v1 constructors stored unvalidated.
   - Failure scenario: `RateLimiter(1, "3")` or `RateLimiter("1", 2)` now raises `ConfigError`, and `RateLimiter(1, 2.5)` raises `ConfigError` for a fractional burst.
   - The brief doesn't ask for validation in the constructors, and the new `_check_clock` also raises `ConfigError` for a non-callable `clock`. Whether that is acceptable under "signatures unchanged" is a judgement call.
   - `load_config` still accepts strings, so the two paths disagree on strings.

3. **`ratelimit/limiter.py:118-123`, low.** `_read_clock` calls `float(clock())`, so a clock returning a numeric string is accepted.
   - Failure scenario: `clock=lambda: "5"` makes `allow` return True as if the time were 5.0. A bad clock is not treated as an internal error here.

4. **`ratelimit/config.py:43`, low.** `float(value.strip())` accepts Python float-literal forms beyond plain numbers.
   - Failure scenario: `load_config({"rate": "1_0"})` returns `rate=10.0`. Strings like `"1e3"` are accepted too.
   - This is consistent with v1's lenient `float()` and doesn't break item 4, but it is looser than "wrong types rejected".

5. **`ratelimit/limiter.py:142, 161, 163, 168`, low.** `stats` is a plain public dict that is written under the lock but read with no locking.
   - Failure scenario: a reader taking `{"allowed", "denied"}` during concurrent `allow` calls can see the two counters from different instants. Each counter itself is not corrupted.
   - `SlidingWindow` has no `stats` at all, which is the same as v1.

6. **`ratelimit/limiter.py:200-208`, low (pre-existing).** `SlidingWindow` never prunes keys.
   - Failure scenario: a stream of distinct keys grows `_log` without bound, because empty lists are never removed. `RateLimiter._buckets` has the same problem.

7. **`tests/test_limiter.py:35-41`, informational.** The pre-existing `test_refill` was edited. Its `in (True, False)` assertion became strict, and the import line was extended. Item 5 allows stricter tests, and the original tests would still pass, so I'm not counting this as a defect.

**Checked, no defect:**
- **Locking and race behaviour:**
  - The clock is read outside the lock, but the `max(0.0, …)` and `max(last, now)` guards keep an out-of-order reading from granting extra tokens (`limiter.py:157, 160`).
  - In `SlidingWindow`, an out-of-order `now` is conservative rather than over-admitting (`limiter.py:202`).
- **Fail closed:** a raising clock, an unhashable key and a non-finite clock all return False. The denial is counted in `stats` for `RateLimiter`.
- **Config validation:** bool, list, None, NaN, inf, huge ints, unknown keys and non-positive values all raise `ConfigError`.
- **Hygiene:** no debug prints, no scratch files, and `git status` shows only the four modified files with nothing staged.
- **Docs:** the README matches the code.

**Verification:** `python3 -m pytest -q` gives `111 passed in 0.58s` (a second run also passed). The new tests cover concurrency, fractional rates, fail-closed and config validation, and the v1 code would not satisfy them. For example, v1 used `int(elapsed * rate)`, which lost fractional refill, so `rate=0.5, burst=1` could never refill.
