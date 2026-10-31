I found no defects that break items 1–4, and the 73 passing tests are consistent with that. The remaining findings are low severity, most severe first.

1. **tests/test_limiter.py:98-120, 148-155 (item 5, new tests that don't fail without the change)**
   - **Defect:** The concurrency tests would very likely still pass if the lock were removed.
   - **Why:** `_hammer` uses a constant `FakeClock` and the default thread switch interval. The check-then-act window in `allow` is a few bytecodes under the GIL, so unsynchronised code rarely over-admits.
   - **Failure scenario:** Delete the `with self._lock` around the state update. `test_rate_limiter_concurrent_never_exceeds_burst` and `test_sliding_window_concurrent_never_exceeds_limit` still pass in most runs. Only `test_clock_read_under_lock` pins the lock, and it checks the clock read only, not the state update. Item 1 is therefore not pinned by a test that fails reliably without it.

2. **ratelimit/limiter.py:100 (SlidingWindow, valid inputs wrongly denied)**
   - **Defect:** The `cutoff < now` guard turns a float-precision artefact into a permanent deny.
   - **Failure scenario:** `SlidingWindow(limit=5, window=1e-9, clock=time.time)`. `time.time()` is about 1.7e9 and its float spacing is about 2e-7, so `now - window == now`. Every `allow()` raises and returns False, although `load_config({"window": 1e-9})` accepts this window. The same happens with any large clock value and a small window.

3. **ratelimit/limiter.py:103 (item 1: "never admits more than its limit")**
   - **Defect:** A non-integral `limit` is accepted and admits more than the limit.
   - **Failure scenario:** `SlidingWindow(limit=2.5, window=10)` admits 3 requests, because `len(stamps) < 2.5` is true for 0, 1 and 2. The item says request-time parameter problems are handled in `allow()`, but this case is neither denied nor tested. `RateLimiter` does not have this problem, because it caps tokens at `burst`.

4. **ratelimit/config.py:35-38, 60-64 (precision loss and item 6 scope)**
   - **Defect:** `burst` is converted to a float before the integer check, so large integers are silently altered. Rejecting `10**400` as `ConfigError` is a debatable choice.
   - **Failure scenario:** `load_config({"burst": 2**53 + 1})` or `{"burst": "9007199254740993"}` returns `burst=9007199254740992`, a different value from the one given. The integrality check should run on the original value, not on the float conversion.

5. **ratelimit/config.py:54, 35, 62 (item 6: behaviour changes beyond what 1–5 need)**
   - **Defect:** Accepted and rejected inputs changed in ways the acceptance list does not require.
   - **Failure scenario:**
     - `load_config(MappingProxyType(...))` was rejected before and is now accepted. A test pins this.
     - `{"burst": "5.0"}` and `{"burst": " 5 "}` were `ConfigError` or accepted by `int()` before, and are now accepted through float parsing.
     - `{"rate": b"1"}` used to work, because `float(b"1")` succeeds, and is now rejected. Neither change is on the list.

6. **ratelimit/limiter.py:44-48 (RateLimiter, clock regression)**
   - **Defect:** A clock that goes backwards makes `elapsed` negative, so tokens go negative and are stored.
   - **Failure scenario:** burst=1, rate=1. The clock reads 100, then 50, then 100. The step back to 50 stores about -50 tokens. After the clock returns to 100, the key is denied for roughly 50 more seconds. The failure is fail-closed, not unsafe, but a non-monotonic injected clock wrongly starves the key. The code does not clamp `elapsed` at 0, and no test covers it.

7. **README.md:13-14 (item 3 of the checklist, docs)**
   - **Defect:** The README was not updated for the new rejection rules.
   - **Failure scenario:** A reader still sees "wrong types, non-positive numbers, unknown keys". It says nothing about NaN or inf, non-integral `burst`, bool being rejected, or numeric strings being accepted. It also doesn't say that `reset` raises `TypeError` for an unhashable key.

8. **ratelimit/limiter.py:56 and :109 (item 3 wording)**
   - **Defect:** `except Exception` does not catch `BaseException` subclasses.
   - **Failure scenario:** A clock that raises `SystemExit` or `KeyboardInterrupt` makes `allow()` raise instead of returning False. Nothing is admitted, so this is not unsafe, but it is not the "returns False" behaviour the item describes. This is arguably acceptable.

I checked the following and they hold:
- The clock read and all state writes happen under the lock.
- The exception path re-takes the lock without deadlock.
- `rate=0.5, burst=1` behaves as specified.
- Both `reset` methods only pop and never admit a key.
- Hygiene is clean: no debug prints and no scratch files.
