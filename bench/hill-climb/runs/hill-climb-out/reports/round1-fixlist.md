# Round 1 fix list (confirmed by verifier; blocking only, misleading carried forward)

Blocking + misleading = 10 > 8, so this batch holds the 8 blocking items. Items 9 and 10 (misleading) carry forward unchanged.

| # | File | Line | Defect | One-line fix | Must leave unchanged |
|---|---|---|---|---|---|
| 1 | ratelimit/limiter.py | `except Exception: return True` (both `allow` methods) | Fails open | `return False`, counting as denied where stats exist | Signatures; happy-path results |
| 2 | ratelimit/limiter.py | `tokens = min(self.burst, tokens + int(elapsed * self.rate))` and `(tokens, now)` writes | Fractional refill truncated and timestamp reset on every call; rate 0.5 unusable | Keep tokens as float, add `elapsed * rate` untruncated | Burst-then-deny, keys independent, reset, stats tests |
| 3 | ratelimit/limiter.py | `_snapshot` locks only the read; bucket write and stats increments outside lock | Double admission, lost stats | Hold `self._lock` for the whole read-compute-write | Single-thread results |
| 4 | ratelimit/limiter.py | `if t >= cutoff` | Request exactly `window` old still counts, contradicting docstring | `t > cutoff` | `test_sliding_window_basic` (advance 11 then allow) |
| 5 | ratelimit/config.py | `if rate <= 0:` only check | burst/window non-positive, nan, inf accepted; `burst=inf` raises OverflowError | Check every field finite and > 0; catch OverflowError | Defaults (1.0, 10, 60.0); numeric strings accepted (`test_values`) |
| 6 | ratelimit/config.py | `KNOWN_KEYS` unused | Unknown keys accepted | `if set(raw) - KNOWN_KEYS: raise ConfigError` | Defaults with `{}` |
| 7 | ratelimit/config.py | `float(raw.get(...))` / `int(raw.get(...))` | bool accepted; non-integral burst truncated | Reject bool; reject non-integral burst | `"4"` string burst still accepted |
| 8 | tests/test_limiter.py | `assert rl.allow("a") in (True, False)` | Cannot fail; no tests for the four requirements | Tighten to `assert rl.allow("a")`; add one test per requirement | Existing test names and assertions (only made stricter) |

Carried forward (misleading, not fixed this round): 9 (numeric-string acceptance is a spec ambiguity, owner decision), 10 (constructors do not validate; Config has no `limit`).
