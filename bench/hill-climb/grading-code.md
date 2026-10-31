# Grading: code-review loops on `ratelimit`

Only critic and reviewer reports are graded. Each seed counts once per contender, and items a reviewer marked out of scope count only if they name a seed. A "checked and fine" claim that misdescribes the code counts as FALSE. Wrong line numbers (`:93-94` in an 89-line file) are not counted as FALSE where the quoted code is correct. I checked the clock-outside-lock claims with a simulation of stale `now` reads, which shows over-admission.

## hill-climb (r2 judged at d1ca561, r3 at 6073574)

| R | File | Finding | Class |
|---|---|---|---|
| 1 | critic | fail-open except | D6 |
| 1 | critic | int() refill, `last` reset | D2 |
| 1 | critic | writes/stats outside lock | D3 |
| 1 | critic | `t >= cutoff` | D1 |
| 1 | critic | burst/window/unknown keys unchecked | D4 |
| 1 | critic | `burst=inf` raises OverflowError (config.py:38, uncaught) | REAL |
| 1 | critic | nan/inf accepted; bool and 2.9 accepted | SCOPE x2 |
| 1 | critic | test_refill tautology | D5 |
| 1 | critic | numeric strings; constructors unvalidated; stats only on RateLimiter | SCOPE x3 |
| 2 | critic | float rounding at boundary; constructor nan/negative; NaN clock | SCOPE x3 |
| 2 | critic | own contention tests cannot detect a missing lock (0/30) | REAL |
| 2 | critic | no Config `limit`; SlidingWindow stats; "4.0"/10**400; bytes; stats on except; eviction | SCOPE x6 |
| 2 | critic | "Reading the clock outside the lock ... only makes the result stricter, never looser" | FALSE |
| 3 | critic | clock read before lock, stale `now` over-admits | REAL |
| 3 | critic | `rel_tol=1e-9` admits 2 ms inside a 30-day window (own code) | REAL |
| 3 | critic | rate 0.1 late; constructor OverflowError; missing tests; failure-path stats; live stats; zero burst; "4.0"/b"4"/"1_0"; UserDict; 2**53 message; Config post-init; key growth; redundant contention test | SCOPE x12 |

Verifier decisions:
- Round 1: confirmed items 1 to 10, with 9 and 10 at misleading.
- Round 2: did not confirm 5 or 6, and downgraded 2 and 4.
- Round 3: confirmed items 1 to 10, with 5 to 8 at misleading, and half-disputed 14.

## reviewloop (final working tree)

| R | File | Finding | Class |
|---|---|---|---|
| 1 | reviewer | fail-open | D6 |
| 1 | reviewer | RateLimiter race | D3 |
| 1 | reviewer | int() truncation | D2 |
| 1 | reviewer | burst/window/unknown keys | D4 |
| 1 | reviewer | test_refill vacuous | D5 |
| 1 | reviewer | bool/strings/nan; constructors; key expiry; pycache | SCOPE x4 |
| 2 | reviewer | ±inf clock lockout; drift at 0.2 (conservative); validation over-reach | SCOPE x3 |
| 2 | reviewer | `rate: 10**400` raises OverflowError (also true at base config.py:37) | REAL |
| 2 | reviewer | own reset-race test asserts `in (True, False)` | REAL |
| 3 | reviewer | ulp miss; strict constructors; string clock; "1_0"; unlocked stats; pruning; test edit | SCOPE x7 |
| 3 | reviewer | "max(0.0, …) and max(last, now) guards keep an out-of-order reading from granting extra tokens" | FALSE |

No reviewer named D1, though the code fixes it.

## loop-review (round 1; the orchestrator played every role, so the reviews were not cold)

| R | File | Finding | Class |
|---|---|---|---|
| 1 | architect A-1 / builder B-2 / tester T-2 | lock covers only the read | D3 |
| 1 | A-2 / B-1 / T-1 | fail-open | D6 |
| 1 | A-3 / B-3 / T-3 | truncation, `last` reset | D2 |
| 1 | A-4 / B-4 / T-4 | config validation | D4 |
| 1 | A-5 | `>=` boundary | D1 |
| 1 | T-3, tester out-of-scope | tautology | D5 |
| 1 | B-5 / T-5 | SlidingWindow reads the clock before the lock (base limiter.py:74) | REAL |
| 1 | T-4 | bool/inf/nan/2.7 accepted | SCOPE |
| 1 | design-critic | none | n/a |

## claude-review-loop

| R | File | Finding | Class |
|---|---|---|---|
| 1 | reviewer | items 1 and 2: fail-open | D6 |
| 1 | reviewer | items 3 and 4: race and stats | D3 |
| 1 | reviewer | item 5: truncation | D2 |
| 1 | reviewer | item 6: boundary | D1 |
| 1 | reviewer | item 7: SlidingWindow lacks stats | SCOPE |
| 1 | reviewer | items 8 and 9: unknown keys, burst/window | D4 |
| 1 | reviewer | item 10: nan/inf/bool | SCOPE |
| 1 | reviewer | item 11: tautology | D5 |
| 2 | reviewer | thread test "sufficient to detect the original race" (fails 0/30 on base code) | FALSE |

## Summary

| Contender | Seeds named | Real-unseeded | Scope | False | Total |
|---|---|---|---|---|---|
| hill-climb | 6 (D1-D6) | 4 | 26 | 1 | 37 |
| reviewloop | 5 (D2-D6) | 2 | 14 | 1 | 22 |
| loop-review | 6 (D1-D6) | 1 | 1 | 0 | 8 |
| claude-review-loop | 6 (D1-D6) | 0 | 2 | 1 | 9 |

**hill-climb verifier:**
- It was sent 18 SCOPE items. It caught 2 (r2 items 5 and 6) and half-caught 1 (r3 item 14).
- It let 15 through: 4 in r1, 3 in r2 and 8 in r3. Seven of those were only downgraded to misleading.
- 8 SCOPE minors were never sent to it.
- It never saw the one FALSE item, which sat in the r2 "checked and fine" list. The r3 critic disproved it.
- It confirmed all 4 REAL items.
