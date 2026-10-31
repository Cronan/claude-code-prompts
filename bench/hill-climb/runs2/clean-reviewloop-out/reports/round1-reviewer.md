**Findings, most severe first.** I found no change under review. The tree is a single commit, and the code in `limiter.py` and `config.py` meets almost none of items 1–4. I could only read files, so I traced these by hand and ran nothing.

1. **`ratelimit/config.py:36-38`, bool accepted.** `float(True)` and `int(True)` succeed, so booleans pass validation. `load_config({"rate": True})` returns `Config(rate=1.0, ...)`, and `{"burst": False}` is rejected only because of the later `<= 0` check. Item 4 requires `ConfigError` for bools. Both are wrong for the same reason: there is no type check.

2. **`ratelimit/config.py:41-46`, NaN and inf accepted.** The only checks are `<= 0`, and NaN fails every comparison. So `load_config({"rate": float("nan")})`, `{"rate": "nan"}`, `{"window": "inf"}` and `{"rate": "1e999"}` all return a `Config`. Item 4 requires rejecting non-finite numbers.

3. **`ratelimit/config.py:37`, non-integral `burst` silently truncated.** `int(2.7)` gives 2, so `load_config({"burst": 2.7})` returns `burst=2` instead of raising. Item 4 requires rejecting non-integral `burst`.

4. **`ratelimit/config.py:36-40`, bare `OverflowError` escapes.** The `except` clause catches only `(TypeError, ValueError)`.
   - `load_config({"burst": float("inf")})` raises `OverflowError` from `int(inf)`.
   - `load_config({"rate": 10**400})` and `{"window": 10**400}` raise `OverflowError` from `float()`.
   
   Item 4 says never a bare `OverflowError`.

5. **`ratelimit/config.py:34`, bare `TypeError` on mixed-type keys.** `sorted(unknown)` fails when the unknown keys are not mutually orderable. `load_config({1: 0, "x": 0})` raises `TypeError` instead of `ConfigError`.

6. **`ratelimit/limiter.py:70-72`, `SlidingWindow` reads the clock outside the lock.** Item 1 requires the clock read to be under the lock. Thread A can read `now=5`, then thread B reads `now=6` and takes the lock first. A then appends the older timestamp out of order, using a cutoff computed before the state it mutates. The log is no longer ordered by time, and the update is not tied to the time it was based on. The fix is to move `now = self.clock()` and `cutoff` inside `with self._lock:`.

7. **`ratelimit/limiter.py:70-79`, NaN clock or window fails open in `SlidingWindow`.** This is not an exception, so the `except` never fires.
   - If the clock returns NaN, `cutoff` is NaN. Then `t > cutoff` is always False, `stamps` is empty, and every call returns True.
   - A NaN `window` passed to the constructor, which is unvalidated, has the same effect.
   - Item 3 says bad values must never admit.

8. **`ratelimit/limiter.py:35-43`, a NaN clock poisons `RateLimiter` buckets.** A NaN `now` is stored as `last`. Every later call for that key computes `elapsed = NaN`, so tokens are NaN (denied) or reset to `burst` by `min(burst, nan)`. Behaviour depends on `min` argument order and is not deliberately fail-closed. Related: `rate=inf` gives `inf * 0 = nan`, and `min` then returns `burst`, which admits.

9. **`ratelimit/limiter.py:48-50` and `83-85`, `reset()` is not guarded.** It is outside any try/except, so `reset(unhashable)` raises `TypeError` out of the call. Item 3 says `reset()` must never raise in a way that leaves a key admitted. Whether this violates it depends on how you read the item. At minimum it is unspecified and untested.

10. **`ratelimit/limiter.py:45-46`, denials on exception are not counted.** A swallowed exception returns False without `stats["denied"] += 1`. Item 3 doesn't require the count. The exception is silently swallowed with no trace, which makes internal errors invisible.

11. **`tests/`, no test for any new behaviour (items 1–4).** There are no tests for any of the following:
    - concurrent `allow()` with threads;
    - `rate=0.5, burst=1` denying at t=1.0 and admitting at t=2.0;
    - `clock()` raising, or an unhashable key, returning False;
    - bool, NaN, inf, None, list, dict, non-numeric-string, non-integral-burst or unknown-key rejection;
    - `load_config({"rate": 0.5})`.
    
    Item 5 asks for tests that fail without the change. The 12 passing tests are the pre-existing ones, so "green" says nothing about items 1–4.

12. **`README.md` and the acceptance list overall.** The README restates the requirements but nothing implements them. Items 2 (rate=0.5 works by float arithmetic, but is unpinned) and 5 (frozen surface intact) hold. Items 1, 3 and 4 are only partly met, as findings 1–9 show. Item 6 (no scope creep) is satisfied only because nothing was changed.

13. **`ratelimit/limiter.py:26, 65`, unbounded state (low severity).** Keys never expire. `SlidingWindow` even stores an empty list after a denied or expired call. A stream of unique keys grows `_buckets` and `_log` without limit. This predates the change and is not in the acceptance list, so it is noted only.

**Sub-1/s check (item 2).** With `RateLimiter(rate=0.5, burst=1)`:
- t=0: admits and leaves 0 tokens.
- t=1.0: tokens are 0.5, so it denies.
- t=2.0: tokens are exactly 1.0, so it admits.

Config accepts `{"rate": 0.5}`. This holds, but no test pins it.
