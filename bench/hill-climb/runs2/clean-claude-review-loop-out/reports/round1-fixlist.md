# Round 1 triage

Verifier substitution: the skill names `npm run lint` and `npm run test`; this repo has neither, so `python3 -m pytest -q` is used as the verifier (no lint step exists).

| # | Finding | Decision | Reason |
|---|---------|----------|--------|
| 1 | config.py:36-37 `float()`/`int()` coerce wrong types (bool, non-integral burst) | **Fix** (partial) | Reject `bool` and non-integral `burst` (2.9 -> 2 is silent data loss). String coercion stays: frozen `test_values` asserts `"2.5"`/`"4"` are accepted, so numeric strings are by design. |
| 2 | config.py:41-46 `nan`/`inf` pass the positivity checks | **Fix** | `nan` rate denies forever, `nan` window never expires; README says invalid config raises `ConfigError`. |
| 3 | config.py:37-39 `int(inf)` raises `OverflowError`, not `ConfigError` | **Fix** | Real escape of a non-`ConfigError` exception from `load_config`. Folded into the finiteness check from #2. |
| 4 | config.py:34 `sorted(unknown)` raises `TypeError` on mixed-type keys | **Fix** | Same class as #3: a raw exception where `ConfigError` is required. One-token fix (`key=repr`). |
| 5 | limiter.py constructors do no validation | **Skip** | Scope creep. Validation is `load_config`'s job; a limiter built with bad numbers denying every request is the fail-closed behaviour the README asks for. |
| 6 | limiter.py per-key state never evicted | **Skip** | Scope creep. Capacity/eviction policy is not among the four stated requirements and changing it alters semantics beyond a minimal fix. Noted as a follow-up. |
| 7 | limiter.py:70-72 `SlidingWindow.allow` reads clock outside the lock | **Fix** | Out-of-order timestamps under contention; cannot exceed the limit but skews later windows. One-line move, matches `RateLimiter`. |
| 8 | limiter.py:45-46 fail-closed path does not count a denial in `stats` | **Fix** | `stats` undercounts; the README's fail-closed denial should be visible. Guarded so the except path cannot itself raise. |
| 9 | tests missing for threading, fractional rate, fail-closed, nan/inf/bool/unknown keys | **Fix** | Brief allows tests to be added; these cover the four README requirements and lock in #1-#3. |
