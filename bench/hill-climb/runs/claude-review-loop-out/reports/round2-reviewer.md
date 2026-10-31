# Round 2 — re-review of changed lines only

Reviewer: substitute (same arrangement as round 1: no `claude -p` and no Agent tool available; read-only pass by the running agent with the skill's prompt, scoped to `git diff` of the round-1 fixes). Skipped item #7 (SlidingWindow.stats) not re-raised.

## Findings

1. `ratelimit/limiter.py:34-37` — LOW — When `self.rate` is not numeric (e.g. a string passed directly to the constructor), `elapsed * self.rate` raises `TypeError`, which is caught and the request is denied. This is correct fail-closed behaviour; noted only to confirm, not a defect.

2. `ratelimit/limiter.py:35` — LOW — `max(0.0, now - last)` guards against a clock that runs backwards (monotonic clocks should not, but the clock is injectable). Behaviour: no refill, `last` unchanged until next admit. Acceptable.

3. `ratelimit/limiter.py:40-44` — INFO — On denial the bucket entry is no longer written, so a key denied before ever being admitted (only possible when `burst < 1`) has no entry at all; `self._buckets.get` then recreates it fresh each call. No correctness impact.

4. `ratelimit/config.py:40-45` — LOW — `_positive_int` accepts numeric strings such as `"4"` (frozen `test_values` requires this) but also accepts `"4.0"`? No: `int("4.0")` raises `ValueError`, which becomes `ConfigError`. Consistent with JSON/YAML string input expectations. Not a defect.

5. `tests/test_limiter.py` (thread test) — INFO — With a fixed FakeClock the test exercises contention on the lock but not time progression under threads; it is sufficient to detect the original race (two threads both seeing one token). Adequate.

No new Fix items.
