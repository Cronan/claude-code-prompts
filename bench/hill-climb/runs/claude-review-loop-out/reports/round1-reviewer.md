# Round 1 — reviewer report

Reviewer: substitute. No `claude -p` CLI and no Agent tool was available in this session, so the review was performed by the running agent itself in a read-only pass (Read/Grep/Glob only), using the skill's prompt verbatim:

> Review the current branch's diff against main (git diff main...HEAD). Report only real defects — bugs, security issues, broken logic, missing edge cases. For each finding give file:line, severity, and a one-line fix. Skip style nitpicks and scope creep.

The diff against main is the whole tree (single commit, no base).

## Findings

1. `ratelimit/limiter.py:49-50` — HIGH — `RateLimiter.allow` catches `Exception` and returns `True`, so any internal error admits the request. Violates "fails closed". Fix: `return False` in the handler (and count as denied).

2. `ratelimit/limiter.py:84-85` — HIGH — Same fail-open handler in `SlidingWindow.allow`. Fix: `return False`.

3. `ratelimit/limiter.py:38-47` — HIGH — Race: `_snapshot` reads the bucket under the lock, but the refill computation and the write to `self._buckets[key]` happen outside it. Two threads can both observe `tokens == 1` and both be admitted, so a key can exceed its limit under contention. Fix: hold `self._lock` for the whole read-modify-write in `allow`, and drop `_snapshot`.

4. `ratelimit/limiter.py:44,47` — MEDIUM — `self.stats[...] += 1` is an unsynchronised read-modify-write on a shared dict; counts drift under threads. Fix: increment inside the same lock as the bucket update.

5. `ratelimit/limiter.py:40,43,46` — HIGH — Refill uses `int(elapsed * self.rate)` and then overwrites `last` with `now` on every call (including denials). Fractional refill is truncated and the accrued time is discarded, so with `rate=0.5` a caller probing once a second is never refilled; even `rate=1.0` polled every 0.5 s never refills. Violates "rates below one request per second are supported". Fix: keep tokens as a float, `tokens = min(burst, tokens + elapsed * rate)`, admit when `tokens >= 1`, and do not reset the accrued fraction on denial.

6. `ratelimit/limiter.py:77` — MEDIUM — `t >= cutoff` keeps a timestamp made exactly `window` seconds ago, contradicting the class docstring ("has left the window and no longer counts"). Fix: `t > cutoff`.

7. `ratelimit/limiter.py:65-70` — LOW — `SlidingWindow` has no `stats` attribute although `stats` is part of the public surface named for both limiters. Fix: add `self.stats = {"allowed": 0, "denied": 0}` and increment under the lock.

8. `ratelimit/config.py:30-40` — HIGH — Unknown keys are silently ignored (`KNOWN_KEYS` is defined but never used). README requires unknown keys to be rejected with `ConfigError`. Fix: `unknown = set(raw) - KNOWN_KEYS; if unknown: raise ConfigError(...)`.

9. `ratelimit/config.py:38-39` — HIGH — Only `rate` is checked for positivity; `burst <= 0` and `window <= 0` are accepted. A `burst` of 0 or negative makes `RateLimiter` deny everything; a non-positive window is meaningless. Fix: raise `ConfigError` when `burst <= 0` or `window <= 0`.

10. `ratelimit/config.py:33-35` — MEDIUM — `float("nan")`/`float("inf")` pass the `rate <= 0` check (NaN compares False), and `bool` values are accepted as numbers (`True` -> 1). Also `int(4.7)` silently truncates a float burst. Fix: reject non-finite values with `math.isfinite`, reject `bool` explicitly, and reject non-integral floats for `burst`.

11. `tests/test_limiter.py:34` — LOW (test weakness, not a library defect) — `test_refill` asserts `in (True, False)`, which can never fail, so the refill path is untested. Frozen tests may not be changed, but a stricter test should be added alongside.

## Not raised (out of scope / nitpicks)

- `RateLimiter.__init__` and `SlidingWindow.__init__` do not validate their arguments; validation is the job of `load_config` and signatures are frozen.
- `SlidingWindow` log grows unbounded for idle keys with stale stamps until next `allow`; memory, not correctness.
