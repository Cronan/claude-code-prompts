I found no real defects in the newly changed lines. I read `limiter.py` and `config.py` for context but didn't run the tests, so the test cases below are traced by hand.

**`ratelimit/config.py`**
- `nan`, `±inf` and `1e999` are all rejected with `ConfigError`. For `burst`, the `is_integer()` guard catches them first. For `rate` and `window`, the `isfinite` checks catch them.
- `OverflowError` is caught, so a huge int such as `10**400` for `rate` or `window` no longer escapes as a raw exception.
- `True`/`False` are rejected before coercion, and `sorted(..., key=repr)` no longer fails on mixed-type unknown keys.

**`ratelimit/limiter.py`**
- `_count_failed_denial` can't double-count. Nothing in `allow` can raise after it increments `stats`, so the counter only moves on the failure path. It doesn't deadlock either, because the `with self._lock` block has already released the lock when the exception reaches the `except`.
- In `SlidingWindow.allow`, reading the clock under the lock keeps timestamps in the same order as the log writes, so concurrent callers can't append out of order.

**Tests**
- `test_fractional_rate` is correct. The denied call at t=1 still stores the new `last` timestamp, so tokens reach exactly 1.0 at t=2.
- The thread-safety tests are deterministic because `FakeClock` doesn't advance during the run.

**Not worth raising:** a non-JSON type such as `Decimal("2.9")` for `burst` would be truncated silently, since it skips the `float`-only fractional check. Parsed JSON and YAML never produce it, so I left it out.
