1. **CONFIRMED.** `load_config({1: 2, "x": 3})` raises `TypeError` ("'<' not supported between 'str' and 'int'"), not `ConfigError`. That breaks "unknown keys → ConfigError", so I rank it blocking.

2. **CONFIRMED AT misleading.** `Fraction(5,2)` and `Decimal('2.9')` both give `burst=2`, while float `2.9` raises `ConfigError`. Parsed JSON or YAML never produces those types, so the path is exotic and I'm downgrading from blocking.

3. **CONFIRMED AT misleading.** `"2.5"`, `" 2 "` and `b"1.5"` are all accepted as `rate`. Burst `"4.0"` raises `ConfigError` while `4.0` is accepted. `test_config.py:11` locks in `"2.5"` and `"4"`.

4. **CONFIRMED AT misleading.**
   - `RateLimiter("1", 5)` denies everything. The `TypeError` is swallowed on the second call.
   - `RateLimiter(-1, 5)` admits 5, then denies.
   - `SlidingWindow(2.5, 10)` admits 3.

5. **CONFIRMED AT misleading.** `RateLimiter(1, 5).allow([1])` returns `False` with no log and `stats` stays at 0/0. Failing closed is the requirement, but the error is invisible.

6. **CONFIRMED AT misleading.** `self.stats` is the live dict, read and written without a snapshot accessor. `SlidingWindow` has no `stats` at all. Reads are unlocked, though not wrong today.

7. **CONFIRMED AT minor.** `Config` has `rate`, `burst` and `window` but no `limit`, so nothing maps config to `SlidingWindow`. No README requirement covers this.

8. **CONFIRMED AT blocking.** I probed a scratch copy of `limiter.py` with the lock replaced by `if True:`. I also set the switch interval to 1e-6 and ran it 5 times with the repo's own `_hammer`. Both concurrency tests still pass and the count is always exactly 50. `FakeClock` never advances in either test. The race-safety requirement therefore has no effective test, which I'm ranking as a missing test, hence blocking rather than the claimed misleading.

9a. **CONFIRMED AT misleading.** `test_sliding_window_basic` advances by 11.0 against a 10.0 window and never tests exactly 10.0, so the `>` boundary is unpinned.

9b. **CONFIRMED AT misleading.** No test moves the clock backwards.

9c. **CONFIRMED AT misleading.** `test_fail_closed_on_clock_error` is the only fail-closed test. It only covers a clock that raises.

9d. **CONFIRMED AT misleading, with a correction.** `inf` admits everything as claimed. `nan` does not deny everything: `min(1.0, nan)` returns `1.0`, so nan also admits everything. Neither case is tested.

9e. **CONFIRMED AT minor.** `isinstance(raw, dict)` rejects a `UserDict` with `ConfigError`, although the docstring says "mapping". No test covers non-dict mappings or nested-mapping burst. Rejection is the safe direction.
