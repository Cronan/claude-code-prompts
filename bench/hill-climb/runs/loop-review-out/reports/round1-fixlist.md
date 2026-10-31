# Round 1 fix list

Synthesis table (deduplicated; every finding challenged against the code and, where runnable, reproduced with python3 before classification):

| ID(s) | severity | decision | reason |
|---|---|---|---|
| T-1, B-1, A-2 | blocker | Accept | Confirmed by repro: clock raising ZeroDivisionError makes both `allow()` return True. Fix: `return False` in both handlers. |
| T-2, B-2, A-1 | blocker | Accept | Confirmed by inspection: `_buckets` writes (:43,:46) and `stats` (:44,:47) are outside `_lock`; only the read is locked. Fix: whole read-modify-write under the lock; drop private `_snapshot`. |
| T-3, B-3, A-3 | blocker | Accept | Confirmed by repro: rate=0.5, burst=1 denies at t=2.0. Fix: float tokens, admit at `>= 1`, keep fractional credit (do not reset `last` on deny). Frozen tests still pass (`test_refill` accepts either value). |
| T-4, B-4, A-4 | high | Accept | Confirmed by repro on 8 inputs (burst=0/-3, window=0, rate=True/"inf"/"nan", burst=2.7, unknown key). Fix: unknown keys, bool, non-integral burst, non-finite and non-positive rejected with ConfigError; string coercion kept for frozen `test_values`. Rejecting invalid input is a defect fix under hard rule 8, not a semantics change. |
| T-5, B-5 | medium | Accept | Confirmed by inspection: `self.clock()` called before the lock in SlidingWindow (:74); one-line move. Falls out of the RateLimiter rewrite as well. |
| A-5 | low | Ask | Docstring says a stamp exactly `window` old no longer counts; code (`t >= cutoff`) keeps it. Either fix is caller-observable and outside the four README requirements. Needs a product decision. |

Design critic: zero findings (no UI in scope). No feature proposals.

Fixes to apply, in rank order:
1. ratelimit/limiter.py: fail closed in both `allow()` (T-1/B-1/A-2).
2. ratelimit/limiter.py: single critical section in `RateLimiter.allow`, remove `_snapshot` (T-2/B-2/A-1); clock inside lock in `SlidingWindow.allow` (T-5/B-5).
3. ratelimit/limiter.py: float refill, `>= 1`, retain credit (T-3/B-3/A-3).
4. ratelimit/config.py: full validation (T-4/B-4/A-4).
5. tests: regression tests for each of the above as the tester proposed.
