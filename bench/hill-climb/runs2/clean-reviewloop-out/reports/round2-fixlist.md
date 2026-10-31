# Round 2 fix list

Source: reports/round2-reviewer.md (sonnet, read-only).

Oscillation note: findings 1 and 2 reverse round 1 findings 7, 8 and 10 (round 1 asked for constructor validation and for logged, counted error denials; round 2 calls both scope creep and the logging a fail-open risk). The skill says to ask rather than iterate; the brief says to treat confirmation as given, so the resolution taken is the one both reviewers accept: constructors keep their frozen, unvalidated behaviour, and `allow()` fails closed on bad parameters at request time (which is what README item 3 actually asks for). Logging is removed. Error denials are still counted in `stats["denied"]`, because a call that returned False and was not counted as denied makes `stats` wrong, and the count is taken under the lock and cannot raise.

1. limiter.py logging can raise inside the except handler -> logging removed entirely; the except path only increments stats under the lock (RateLimiter) or returns False (SlidingWindow). No log flooding.
2. limiter.py constructor validation is scope creep against the frozen constructors -> removed. `_number` is no longer imported across modules. `allow()` now treats a non-finite computed token count (RateLimiter) or non-finite cutoff (SlidingWindow) as an internal error and denies, so rate=inf, window=nan and a NaN clock all fail closed as round 1 required.
3. config.py `_number` rejects Decimal -> `decimal.Decimal` added to the accepted types (bytes stay rejected; they are not something JSON or YAML produce). Tests pin Decimal, " 5 " and "1_0" acceptance.
4. config.py `isinstance(raw, dict)` -> `collections.abc.Mapping`; MappingProxyType pinned by a test.
5. limiter.py `stats` is a live public dict read without the lock -> not changed. `stats` is a frozen public attribute compared by equality in the existing tests, so a locked accessor or snapshot type cannot be introduced. Writes are under the lock; each counter is individually consistent. Reported as remaining.
6. limiter.py per-key state never evicted -> no action; pre-existing and outside the acceptance list (both reviewers say so).
7. tests -> imports moved to the top of test_limiter.py; added fail-closed tests for `rl.rate = "x"`, clock returning None and a string, rate=inf, window=nan, limit=0/negative, burst=0; added non-mapping config tests for None and a str; constructor-rejection tests replaced by request-time fail-closed tests. Logging test not added because logging was removed.
