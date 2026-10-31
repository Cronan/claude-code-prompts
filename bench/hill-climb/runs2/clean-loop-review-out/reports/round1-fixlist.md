# Round 1 fix list

Reviewers run: tester (sonnet), builder (sonnet), architect (opus), design-critic (sonnet). All four returned usable output.

Challenge results (traced by running the inputs in the repo, see orchestrator notes):

| ID(s) | severity | decision | reason |
|---|---|---|---|
| A-2, B-1, T-1 | high | Accept | Confirmed: load_config accepts NaN, inf, "inf", bool, bytes, truncates burst 2.7 to 2; burst=inf and rate=10**400 escape as OverflowError. Fix: strict shared validator (reject bool/bytes/None, require finite > 0, burst integral), catch OverflowError. Numeric strings stay accepted because frozen test_values requires them (B-1's "int-only burst" variant rejected for that reason). |
| T-2 (B-1 part) | medium | Accept | Confirmed: load_config({1: 1, "x": 2}) raises TypeError from sorted(). Fix: sorted(unknown, key=repr) keeps the existing message for string keys. |
| A-1, B-3, T-3 | high | Accept | Confirmed: RateLimiter(nan, 1), SlidingWindow(1, nan), SlidingWindow(1, -5) all allow every call (fail open); RateLimiter("x", 1) denies forever silently. README requires invalid configuration rejected with ConfigError; rejecting invalid input is a defect fix under hard rule 8, not a semantics change. Constructors call the shared validator. Signatures unchanged. |
| A-3, T-4 | medium | Accept | Confirmed: rate=0.1, burst=1, poll once a second: denied at t=10 (sum 0.9999999999999999). Fix: do not write the bucket back on deny, so refill is one multiplication from the last admission; clamp elapsed to >= 0. Sub-1/s requirement. |
| A-4, B-4 | medium | Accept | Confirmed: a NaN clock reading stores NaN as `last` and the key is admitted on every subsequent call ([True]*5 with clock 0, nan, 1, 2, 3); SlidingWindow logs [nan]. Fix: reject non-finite `now` before any state write (counted as denied); clamp negative elapsed; update stats before the bucket write so a failure leaves no half-applied change. |
| B-2, T-5 | medium -> low | Accept (as low) | Reading the clock outside the lock in SlidingWindow.allow is confirmed at limiter.py:70. The claimed over-admission is NOT confirmed: a stale (older) cutoff retains more stamps, so it can only deny more, never admit more. Accepted anyway as a two-line move matching RateLimiter, removing out-of-order stamps; no observable behaviour change. |
| A-5 | low | Accept | Confirmed: raising clock -> allow() False, stats {"allowed": 0, "denied": 0}. Fix: best-effort denied increment in the except path. The "stats as a copying property" variant is rejected (callers may assign to stats; frozen API). |
| B-5, T-5 (tests) | medium | Accept | Confirmed by reading tests/: no concurrency, fractional-rate, fail-closed or config edge-case tests. Add them. |
| A-5 / Tester IDEA (stats on SlidingWindow) | low | Backlog | New public attribute; not needed for the four requirements. |
| Out-of-scope notes (eviction, Config.limit, Mapping vs dict, reset without try) | - | Backlog / Reject | Not required by the goal. `isinstance(raw, dict)` is kept: widening to Mapping changes what load_config accepts (hard rule 8). |

Ask: none. No fix changes a frozen signature or the result of any existing test.
