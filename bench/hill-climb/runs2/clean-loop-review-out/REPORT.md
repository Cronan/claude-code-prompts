# /loop-review report

**Goal:** harden the ratelimit library so it meets the four README requirements: thread-safe, sub-1/s rates, fail closed, invalid config rejected with ConfigError
**Scope:** ratelimit/, tests/
**Rounds:** 1 of 3, stopped because: **Done** (definition of done met; no confirmed in-scope finding of medium severity or above remains). Hard rule 4 forbids starting another round just to justify it.

## Stopping rule
Done. After round 1 all accepted findings were fixed, each is proven by a test at the layer where the value is produced, and the verifier passes (64/64). No Ask items, no stall, no degraded round.

## Baseline
- Revision 12f2fd5 on master, baseline dirty list: empty.
- No CLAUDE.md or AGENTS.md.
- Checks: `python3 -m pytest -q` (from `checks=`; the skill's npm commands substituted with the pytest verifier) -> 12 passed.
- UI present: no. UI reviewed from source only: no browser tool.
- Definition of done: (1) concurrent calls from many threads never admit more than burst/limit per key, proven by a test; (2) fractional rates such as 0.5 refill correctly, proven by a test; (3) any internal exception in allow() yields False without propagating or corrupting state, and load_config rejects wrong types, non-positive numbers, unknown keys and bool/None/NaN/inf with ConfigError, proven by tests.
- Cost gate: confirm=yes passed; estimate printed as ~$2-3 and ~10-15 minutes per round for this 5-file scope.

## Rounds and findings
### Round 1
Reviewer processes run: 4 (`claude -p --no-session-persistence`, tools Edit/Write/Bash/NotebookEdit/WebFetch/WebSearch disallowed):
- loop-tester: sonnet, 5 findings (T-1..T-5)
- loop-builder: sonnet, 5 findings (B-1..B-5)
- loop-architect: opus, 5 findings (A-1..A-5)
- loop-design-critic: sonnet, 0 findings (no UI in scope)

Synthesis (after dedup, each challenged by running the cited inputs against the repo):

| ID(s) | severity | decision | reason |
|---|---|---|---|
| A-2, B-1, T-1 | high | Accept | Confirmed: load_config accepted NaN, inf, "inf", bool, bytes; truncated burst 2.7 to 2; burst=inf and rate=10**400 escaped as OverflowError. |
| T-2 (part of B-1) | medium | Accept | Confirmed: `load_config({1: 1, "x": 2})` raised TypeError from `sorted()`. |
| A-1, B-3, T-3 | high | Accept | Confirmed: `RateLimiter(nan, 1)`, `SlidingWindow(1, nan)`, `SlidingWindow(1, -5)` admitted every call (fail open); `RateLimiter("x", 1)` denied forever silently. Rejecting invalid input is a defect fix (hard rule 8), signatures unchanged. |
| A-3, T-4 | medium | Accept | Confirmed: rate=0.1, burst=1, polled once a second, denied at t=10 (sum 0.9999999999999999). |
| A-4, B-4 | medium | Accept | Confirmed: clock sequence 0, nan, 1, 2, 3 made RateLimiter admit every call; SlidingWindow logged [nan]. |
| B-2, T-5 | medium, downgraded to low | Accept | Clock read outside the lock in SlidingWindow.allow confirmed, but the claimed over-admission is NOT confirmed: a stale (older) cutoff retains more stamps and can only deny more. Accepted as a no-behaviour-change two-line move matching RateLimiter. |
| A-5 | low | Accept | Confirmed: raising clock -> allow() False with stats unchanged. Best-effort denied count in the except path. "stats as copying property" variant rejected (callers may assign to stats; frozen API). |
| B-5, T-5 (tests) | medium | Accept | Confirmed: no concurrency, fractional-rate, fail-closed or config edge-case tests existed. |
| Tester IDEA / A-5 part: stats on SlidingWindow | low | Backlog | New public attribute, not needed by the four requirements. |
| B-1 variant: burst int-only (reject "4" and 4.0) | - | Reject | Frozen test_values requires numeric strings for burst. |
| Out of scope notes: key eviction, Config.limit field, Mapping vs dict, reset without try/except | - | Backlog / Reject | Not required by the goal; widening dict to Mapping would change what load_config accepts (hard rule 8). |

Counts: accepted 8 (merged root causes), rejected 2, asked 0, backlogged 4.

## Changes (file by file)
- `ratelimit/config.py`: added `_positive_number(name, value)` (accepts int/float/numeric str; rejects bool, bytes, None and other types; catches TypeError/ValueError/OverflowError; requires finite and > 0) and `_positive_int` (additionally requires a whole value, no truncation); `load_config` uses them in place of bare float()/int() coercion; unknown-key message uses `sorted(unknown, key=repr)` so mixed-type keys raise ConfigError. (A-2, B-1, T-1, T-2)
- `ratelimit/limiter.py`: both constructors validate through the shared helpers and raise ConfigError on invalid rate/burst/limit/window (A-1, B-3, T-3); `allow()` rejects a non-finite clock reading before writing any state and clamps negative elapsed to 0 (A-4, B-4); on deny the bucket is no longer written back, so refill is one multiplication from the last admission and fractional rates do not drift (A-3, T-4); stats increment moved before the bucket write and a best-effort denied increment added in the except path (B-4, A-5); SlidingWindow reads the clock inside the lock (B-2, T-5). 36 lines changed in this file; config.py 49 lines, mostly the two helpers, which the three reviewers all asked for as one shared validator.
- `tests/test_hardening.py` (new): 52 tests covering concurrency (32 threads x 50 calls, barrier-started, exactly burst/limit admitted for both limiters), 0.5 and 0.1 rates with no drift, backwards clock, raising clock, unhashable key, NaN clock reading, 28 invalid config inputs, 13 invalid constructor inputs, and the still-accepted valid forms.
- Frozen files untouched: `tests/test_limiter.py`, `tests/test_config.py`, `ratelimit/__init__.py`, `README.md`, `pytest.ini`.

## Verification
- Checks before: 12 passed. Checks after: 64 passed (12 original + 52 new), concurrency tests re-run 5 times, all green.
- Rendered evidence: source only (pure Python library, no UI).
- Not run: nothing.
- Fixes not seen by any reviewer: all round-1 fixes, because the Done rule fired after round 1 and no round 2 reviewed them.

## Remaining issues
- None confirmed at medium or above. The SlidingWindow race claimed in B-2/T-5 was not reproducible by reasoning (stale cutoff only over-denies); the fix was applied as a no-behaviour-change tidy-up, not as a confirmed defect.

## Needs your decision
- None. No fix changed a frozen signature or the result of a frozen test. Note for awareness: constructors now raise ConfigError for invalid arguments where they previously accepted anything; this is the README requirement, not a semantics change under hard rule 8.

## Rejected suggestions
- Burst as int-only (B-1): frozen `test_values` passes `"4"` for burst.
- `stats` as a property returning a copy (A-5): callers may assign to `rl.stats`; `stats` is a frozen public attribute.
- `isinstance(raw, Mapping)` (architect out of scope): widens accepted input (hard rule 8).

## Feature backlog
- `stats` on SlidingWindow for metric parity.
- Eviction of idle keys from `_buckets` / `_log`.
- `Config.limit` field so a SlidingWindow can be built from a loaded config.
- `reset()` wrapped in try/except for symmetry.

## Final verifier output
```
$ python3 -m pytest -q
................................................................         [100%]
64 passed in 0.09s
```

Nothing was committed; `git diff` (plus the untracked `tests/test_hardening.py`) shows every change. `git status --porcelain`: ` M ratelimit/config.py`, ` M ratelimit/limiter.py`, `?? tests/test_hardening.py`.
