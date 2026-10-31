# Round 1 fix list

Source: reports/round1-reviewer.md (sonnet, read-only). All findings addressed.

1. config.py bool accepted -> explicit type check: bool rejected; only int/float (numbers.Real, not bool) and numeric strings accepted.
2. config.py NaN/inf accepted -> require math.isfinite on every parsed number.
3. config.py non-integral burst truncated -> burst parsed as float, rejected unless .is_integer(), then converted to int.
4. config.py bare OverflowError -> single `_number()` helper catches (TypeError, ValueError, OverflowError) and re-raises ConfigError.
5. config.py sorted(unknown) TypeError on mixed-type keys -> sort by repr().
6. limiter.py SlidingWindow clock read outside lock -> `now`/`cutoff` moved inside `with self._lock`.
7. limiter.py NaN clock/window fails open in SlidingWindow -> constructor validates limit/window (finite, positive) and raises ConfigError; allow() denies if clock value is non-finite.
8. limiter.py NaN clock / inf rate poisons RateLimiter -> constructor validates rate/burst (finite, positive); allow() denies without touching the bucket if clock value is non-finite.
9. limiter.py reset() unspecified for unhashable key -> specified in docstring (raises TypeError, admits nothing) and pinned by a test; the exception is not swallowed because reset is not a request path and hiding it would be catch-and-ignore.
10. limiter.py exception-path denials uncounted and silent -> except path increments stats["denied"] under the lock and logs the traceback at WARNING via the module logger.
11. No tests for items 1-4 -> added: concurrency (RateLimiter and SlidingWindow, barrier-started threads, fixed clock), clock-read-under-lock assertion, rate=0.5 timeline, load_config rate 0.5, clock raising, unhashable key, NaN clock, constructor rejection, exception-path stats, and a parametrised config rejection matrix (bool, None, list, dict, bad string, non-positive, nan, inf, overflow, non-integral burst, unknown keys, mixed-type unknown keys).
12. No action (summary finding).
13. Unbounded state: no action; reviewer marks it as pre-existing and outside the acceptance list, and changing it would be scope creep.
