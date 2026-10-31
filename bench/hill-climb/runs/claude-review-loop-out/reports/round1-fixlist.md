# Round 1 — triage

| # | Finding | Severity | Decision | Reason |
|---|---------|----------|----------|--------|
| 1 | `RateLimiter.allow` fails open on exception | HIGH | Fix | README requirement 3 |
| 2 | `SlidingWindow.allow` fails open on exception | HIGH | Fix | README requirement 3 |
| 3 | Token bucket read-modify-write outside lock | HIGH | Fix | README requirement 1 |
| 4 | `stats` increments unsynchronised | MEDIUM | Fix | Same lock as #3; trivial once #3 is done |
| 5 | Integer truncation + `last=now` on every call starves fractional/slow refill | HIGH | Fix | README requirement 2 |
| 6 | `t >= cutoff` keeps a stamp exactly `window` old | MEDIUM | Fix | Contradicts the documented contract; one-character change |
| 7 | `SlidingWindow` lacks `stats` | LOW | Skip | Not in README; `stats` is frozen as it exists today and nothing requires it on `SlidingWindow`. Scope creep. |
| 8 | Unknown config keys silently ignored | HIGH | Fix | README requirement 4 |
| 9 | Non-positive `burst`/`window` accepted | HIGH | Fix | README requirement 4 |
| 10 | NaN/inf, bool, non-integral burst accepted | MEDIUM | Fix (NaN/inf and bool, non-integral burst) | "wrong types" and "non-positive" are explicit in README; NaN defeats the positivity check. |
| 11 | `test_refill` cannot fail | LOW | Fix (add a stricter test alongside; frozen test untouched) | Brief allows adding tests; needed to verify #5 |

Fix items: 1, 2, 3, 4, 5, 6, 8, 9, 10, 11. Skipped: 7.
