# claude-review-loop run report

Repository: /home/claude/bench/runs2/clean-claude-review-loop (commit 12f2fd5, master). Whole tree treated as the diff against main.
Verifier substitution: the skill names `npm run lint` and `npm run test`; neither exists here, so `python3 -m pytest -q` was used (no lint step).

## Stopping rule

Stopped by "no Fix items remain" after round 2 (cap of 3 not reached). Round 2's re-review of the changed lines reported no defects.

## Rounds and findings

Round 1 (full tree): 9 findings. Fix: 7 (#1 partial, #2, #3, #4, #7, #8, #9). Skip: 2 (#5 constructor validation, #6 key eviction; both scope creep). Part of #1 skipped: numeric-string coercion is required by the frozen test `test_values`.
Round 2 (changed lines only): 0 defects; one "not worth raising" note (Decimal burst) skipped.

## Reviewer processes

2 processes, both `claude -p --no-session-persistence --permission-mode default --model sonnet --disallowedTools Bash,Edit,Write`. Bash disallowed because the skill does not tell the reviewer to run the verifier.
- reports/round1-reviewer.md (sonnet)
- reports/round2-reviewer.md (sonnet)

## Changes by file

ratelimit/config.py
- import math.
- Unknown-key error sorts with key=repr so mixed-type keys raise ConfigError, not TypeError.
- bool values for rate/burst/window rejected before coercion.
- Non-integral float burst (e.g. 2.9) rejected instead of truncated.
- OverflowError added to the caught conversion errors (int(inf), 1e999).
- rate and window must be finite (math.isfinite) as well as positive.

ratelimit/limiter.py
- RateLimiter.allow: the fail-closed except path now increments stats["denied"] via a new _count_failed_denial helper that takes the lock and cannot itself raise.
- SlidingWindow.allow: clock read and cutoff computed inside the lock (was outside), so timestamps cannot be appended out of order under contention.

tests/test_config.py (added)
- parametrised nan/inf/-inf/True/False rejection for each key; fractional burst; 1e999 burst; unknown keys; mixed-type unknown keys.

tests/test_limiter.py (added)
- fractional rate 0.5; fail-closed with a raising clock for both limiters (and stats counts the denial); 8-thread hammer tests asserting exactly `burst`/`limit` admissions for RateLimiter and SlidingWindow.

Public signatures unchanged; all 12 original tests still pass unchanged.

## What remains (skipped, not fixed)

- Limiter constructors accept invalid numbers without validation (bad values deny every request, which is fail-closed but silent).
- Per-key state in _buckets/_log is never evicted; unbounded key cardinality grows memory.
- load_config still accepts numeric strings ("2.5", "4") because the frozen test requires it.
- Decimal burst values would be truncated silently (not JSON/YAML-producible).

## Final verifier output

```
$ python3 -m pytest -q
...................................                                      [100%]
35 passed in 0.04s
```
