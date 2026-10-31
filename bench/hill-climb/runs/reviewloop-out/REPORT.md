# Reviewloop report: harden the ratelimit library

Skill: /home/claude/bench/skills/reviewloop.md (with REFERENCE.md). Argument: "harden the ratelimit library so it meets the four README requirements: thread-safe, sub-1/s rates, fail closed, invalid config rejected with ConfigError". Repository: /home/claude/bench/runs/reviewloop. Round cap used: 3 (brief), within the skill's cap of 5.

## Stopping rule

**Cap reached.** The skill exits only on a pass with zero findings. Round 3 still reported findings (seven, all rated low or informational by the reviewer), so the loop stopped on the 3-round cap, not on convergence. Per the skill's guard ("At the cap, stop and hand the user the open findings with what was tried"), the round 3 findings are listed below unfixed; nothing was changed after the round 3 review so that the final verifier output corresponds to the code the last reviewer saw.

No oscillation guard fired: no finding reappeared after being fixed. One spec disagreement arose between rounds (constructor validation; see "Remains unfixed"), which I resolved by decision rather than by asking, since the brief says to treat confirmations as given.

## Rounds

| Round | Reviewer findings | Fixed | Deferred / not fixed | Verifier after fixes |
|---|---|---|---|---|
| 1 | 9 (fail open in both limiters; unlocked read-modify-write; truncated fractional refill; config validation gaps incl. bool/None/unknown keys/NaN/non-positive burst and window; constructors unvalidated; vacuous `test_refill`; no tests for requirements; `__pycache__` clutter) | 8 | 1 (unbounded per-key memory growth: pre-existing, outside the four requirements) | 95 passed |
| 2 | 5 (+/-inf clock poisons state; `OverflowError` leaks from huge ints; float drift in incremental refill; validation duplicated/inconsistent between config.py and limiter.py; reset-race test asserts nothing) | 5 | 0 (two side notes not fixed: memory growth again; README does not mention string coercion) | 111 passed |
| 3 | 7 (ulp-level refill boundary miss for some rates; constructors reject values v1 accepted; `float(clock())` accepts numeric-string clock readings; `float()` accepts `"1_0"`; `stats` dict read without lock; unbounded key growth; `test_refill` edited, informational) | 0 (cap) | 7 | 111 passed (final) |

Verification before round 1 (original code): 12 passed. The 99 added or strengthened tests were also run against the original v1 library code: 66 fail there and all pass on the fixed code, so the suite now distinguishes the hardened library from the original.

## Subagent calls

The Agent tool was not available in this session (ToolSearch found no Agent/Task tool), and the skill's `/code-review` dependency is not installed. As the brief permits for a missing external CLI, each reviewer was substituted by a fresh `claude -p` process (Claude Code 2.1.316), one per round, no fan-out, given only the acceptance list, the scope, the REFERENCE.md checklist and the subagent prompt template, and restricted to read-only tools (`Read, Grep, Glob, Bash(git *), Bash(python3 *), Bash(cd *)`). None of my reasoning about the fixes was passed to any reviewer.

| Call | Role | Model reported by the CLI | Turns |
|---|---|---|---|
| 1 | round 1 reviewer | claude-sonnet-5-5 (plus a 2,153-token claude-haiku-5-5 helper call made by the CLI itself) | 7 |
| 2 | round 2 reviewer | claude-sonnet-5-5 | 7 |
| 3 | round 3 reviewer | claude-sonnet-5-5 | 11 |

Three subagent calls in total. Reports are saved verbatim in /home/claude/bench/runs/reviewloop-out/reports/round{1,2,3}-reviewer.md; the fix lists acted on are round1-fixlist.md and round2-fixlist.md in the same directory.

## What was fixed, file by file

Public signatures (`RateLimiter(rate, burst, clock=)`, `SlidingWindow(limit, window, clock=)`, `allow(key) -> bool`, `reset(key)`, `stats`, `load_config(dict) -> Config`, `ConfigError`) are unchanged. The 12 original tests are unchanged except `test_refill`, which was made stricter (allowed by the brief).

### ratelimit/limiter.py
- Fail closed: both `allow()` exception handlers return `False`; `RateLimiter` counts the failure in `stats["denied"]` and the handler itself cannot raise.
- Thread safety: `RateLimiter.allow` now does its whole read-compute-write and `stats` update under `_lock` (the `_snapshot` helper that locked only the read is gone). `SlidingWindow.allow` was already locked.
- Sub-1/s rates: tokens are stored as floats and refilled by `elapsed * rate` without truncation. Per-key state `(tokens, last)` is rewritten only on admission, so polling a denied key no longer discards fractional progress or accumulates rounding error, and a clock reading that goes backwards grants nothing and leaves the baseline alone (round 2 finding on 1000s backward steps locking a key out).
- Clock readings: `_read_clock` rejects NaN and +/-inf as internal errors (deny, state untouched) instead of letting an `inf` poison `last` or the sliding log forever.
- Constructor validation: `rate`, `burst`, `limit`, `window` go through the shared `coerce_float` / `coerce_int` helpers and raise `ConfigError` for bools, None, strings, non-finite, non-positive, fractional counts and integers too large for a float; `clock` must be callable.
- `SlidingWindow` boundary: a stamp exactly `window` seconds old is excluded (`t > cutoff`), matching the docstring.

### ratelimit/config.py
- Unknown keys rejected using the previously unused `KNOWN_KEYS`.
- Bools, None, containers and other non-numeric types rejected for all three fields; NaN and inf rejected; non-positive `burst` and `window` rejected (only `rate` was checked before); fractional `burst` rejected (was silently truncated); `OverflowError` from huge integers converted to `ConfigError`.
- Numeric strings remain accepted in `load_config` because the frozen `test_values` requires `"2.5"` and `"4"` to load; integer strings are parsed via float so `"1000.0"` and `"1e3"` are accepted and `"2.5"` is rejected, consistent with how floats are treated.
- Single set of coercion helpers (`coerce_float`, `coerce_int`, `allow_str` switch) shared with limiter.py, replacing the near-duplicate validators flagged in round 2.

### tests/test_limiter.py
- `test_refill` strengthened (asserts deny before, admit after 1.0s, deny again).
- Added: sub-1/s refill at exactly 2.0s for rate 0.5; fraction preserved under frequent polling (0.25/s); refill capped at burst; backward clock grants nothing; backward step does not lock out; exact boundary for rate 0.2 polled every 0.1s; raising clock, non-numeric clock, NaN and +/-inf clock readings deny without poisoning state (both limiters); unhashable key denies and the limiter keeps working; constructor rejection matrices for both classes; non-callable clock; whole-float burst accepted; huge-int arguments raise `ConfigError`; sliding window exact boundary and key independence; concurrency tests (16 threads x 100 calls, one key, exactly `burst`/`limit` admitted, five rounds each, plus a many-keys variant checking per-key counts and stats totals); reset racing with allow with real assertions on results, stats totals and post-race state.

### tests/test_config.py
- Added a 32-case rejection matrix (bool, None, containers, bad strings, fractional burst, non-positive values, NaN/inf as numbers and strings, huge ints, unknown and mis-cased keys), `ConfigError` is a `ValueError`, whole-float burst accepted, ints become floats for rate/window, integer strings in float form accepted for burst, no non-`ConfigError` exception leaks, and config values build working limiters.

## Remains unfixed and why

Round 3 findings, left open because the round cap was reached (fixing them would require a further pass to validate, which the cap forbids). My assessment of each is given so the user can decide.

1. **Refill boundary one ulp short for some rates** (`limiter.py`, `available >= 1.0`). For example rate 0.36, admit at t=0, call at t=1/0.36: `elapsed * rate` is 0.9999999999999999 and the call is denied. Real: the reviewer swept n/100 rates and found 285 that miss at the exact boundary. In practice the key is admitted on the next poll, and the error is on the conservative side, so it does not over-admit. A tolerance (e.g. `>= 1.0 - 1e-9`) or integer-nanosecond arithmetic would close it. Not done.
2. **Constructors now reject values v1 stored unvalidated** (`RateLimiter(1, "3")`, `RateLimiter(1, 2.5)`, non-callable clock). Round 1 asked for constructor validation; round 3 questions it under "signatures unchanged". The signatures are unchanged, and the README's "invalid configuration is rejected with ConfigError" reads naturally as covering the limiter's own settings; without it a `None` rate would make every `allow()` deny silently. I kept the validation. This is the one point where two reviewers disagreed, and it is a spec question for the user: if the v1 lenient constructors must be preserved, drop the `coerce_*` calls in `__init__` and the related tests.
3. **`_read_clock` accepts a numeric-string clock reading** (`clock=lambda: "5"` is treated as 5.0). A straightforward tightening (`isinstance(now, numbers.Real)` check) that was not applied because of the cap.
4. **`load_config` accepts Python float-literal forms such as `"1_0"` and `"1e3"`.** Inherited from v1's `float()` coercion and required in spirit by the frozen `test_values`; not a violation of the four requirements. Would need a stricter string grammar if wanted.
5. **`stats` dict is read without the lock.** Each counter is updated under the lock; a reader may see the two counters from different instants. `stats` is a frozen public attribute (a plain dict), so an atomic snapshot API cannot be added without changing the surface. Pre-existing.
6. **Per-key state is never evicted** (both limiters). Pre-existing, raised in all three rounds; outside the four README requirements and would need a new eviction/TTL API, which the skill's no-scope-creep guard treats as a finding in itself. Not done.
7. **`test_refill` was edited** (informational). Allowed by the brief ("tests may be made stricter"); the reviewer did not count it as a defect.

Also not done: README was not updated to document numeric-string acceptance (round 2 side note; behaviour unchanged from v1). `__pycache__` directories produced by running the verifier were removed after each run and are not part of the diff.

## Final verifier output

`python3 -m pytest -q` in /home/claude/bench/runs/reviewloop, run after the round 3 review with no further changes:

```
........................................................................ [ 64%]
.......................................                                  [100%]
111 passed in 0.63s
```

`git status --short` at the end: four modified files (`ratelimit/config.py`, `ratelimit/limiter.py`, `tests/test_config.py`, `tests/test_limiter.py`), nothing staged, nothing committed, no branches or remote changes.
