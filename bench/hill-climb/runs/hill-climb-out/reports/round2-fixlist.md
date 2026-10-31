# Round 2 fix list (confirmed by verifier)

Confirmed: 2 blocking, 2 misleading (total 4, within the batch limit of 8). Disputed (not fixed, carried to owner's list): critic items 5 (Config has no `limit` for SlidingWindow) and 6 (`stats` only on RateLimiter).

| # | File | Line | Defect | One-line fix | Must leave unchanged |
|---|---|---|---|---|---|
| 1 | ratelimit/limiter.py | `stamps = [t for t in self._log.get(key, []) if t > cutoff]` with `cutoff = now - self.window` | Float rounding: a request exactly `window` old is sometimes still counted (84/999 with fractional stamps) | Keep a stamp only if `now - t < self.window`; add a fractional-timestamp boundary test | Existing sliding-window tests; limit semantics |
| 2 | tests/test_limiter.py | contention tests | Cannot detect a missing lock (0/30 over-admits with lock removed) | Add a test whose key's `__hash__` yields the GIL (`time.sleep(0)`) so a lockless read-modify-write interleaves; assert exact admitted count; confirm it fails with the lock removed | Existing tests |
| 3 | ratelimit/limiter.py | `RateLimiter.__init__`, `SlidingWindow.__init__` store arguments unchecked | Negative/NaN window, NaN rate, string rate admit every request or starve | Validate in `__init__`: numeric (not bool), finite; rate/window > 0; burst/limit a non-negative int; raise `ConfigError` | Signatures; all currently valid constructions (ints/floats) |
| 4 | ratelimit/limiter.py | `cutoff = now - self.window` when clock returns NaN | Log emptied, every call admitted (fails open) | `if not math.isfinite(now): deny` in both limiters | Happy-path results |
