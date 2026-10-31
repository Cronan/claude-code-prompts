# Round 2 fix list (confirmed blocking only; 2 blocking + 9 misleading this round + 10 misleading carried from round 1 > 8, so misleading carried forward unchanged)

Ranks are the round-2 verifier's.

| # | File | Line | Defect | One-line fix | Must leave unchanged |
|---|---|---|---|---|---|
| B1 | ratelimit/config.py | 35 | `sorted(unknown)` raises TypeError when unknown keys mix types (e.g. `{1: 2, "x": 3}`), so caller gets TypeError not ConfigError | `sorted(map(repr, unknown))`; add a test with mixed-type unknown keys | `test_unknown_key` and all other config tests; ConfigError still raised for unknown keys |
| B2 | tests/test_limiter.py | 120-130 | Both concurrency tests use a clock that never moves and pass with the lock removed, so requirement 1 has no effective test | Add tests whose clock yields the GIL inside the critical section and one whose clock advances from another thread; confirm the yielding test fails on a lock-less scratch copy | Existing tests; ratelimit/limiter.py untouched |

Carried forward (confirmed misleading, not fixed this round), round-2 numbering, with round-1 carry-overs folded in:

- M2 Fraction/Decimal burst silently truncated (config.py:39-44)
- M3 numeric strings accepted as config values; `"4.0"` rejected for burst while `4.0` accepted; README says "wrong types" rejected (policy: owner must say which is right; `test_values` freezes string acceptance)
- M4 `RateLimiter`/`SlidingWindow` constructors validate nothing (policy: does requirement 4 apply to constructors?)
- M5 `except Exception: return False` swallows caller bugs silently; no log, stats not updated (= round-1 M3/M5)
- M6 `stats` is the live dict with no snapshot accessor; `SlidingWindow` has no `stats` (= round-1 M3/M4; policy on which class owns `stats`)
- M9a exact-window boundary (`t > cutoff`) untested (= round-1 M8)
- M9b backwards clock untested (= round-1 M7)
- M9c fail-closed tested only for a raising clock
- M9d `rate=inf`/`nan` passed directly to `RateLimiter` admits everything; untested (= round-1 M1/M2)
- round-1 M6 `reset` not wrapped like `allow` (unhashable key raises in `reset`, returns False in `allow`)

Downgraded to minor by the round-2 verifier (wait for stopping rule): M7 `Config` has no `limit` field (= round-1 M10); M9e `isinstance(raw, dict)` rejects non-dict Mappings; M10 unbounded key growth and list rebuild per call (= round-1 M9).
