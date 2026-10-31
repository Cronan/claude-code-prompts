# claude-review-loop — run report

Repository: /home/claude/bench/runs/claude-review-loop (single commit `aa358df`, whole tree treated as the diff against `main`).
Skill: /home/claude/bench/skills/claude-review-loop.md, cap 3 iterations.

## Stopping rule

Stopped after round 2 by the rule "no Fix items remain". Round 1 produced 10 Fix items, all applied; the round-2 re-review of the changed lines produced no Fix items. The 3-iteration cap was not reached.

## Substitutions

- `claude -p` is not installed. The brief said to substitute an Agent subagent with the same prompt and tool restrictions. No Agent/Task tool was exposed in this session (ToolSearch for `Agent`, `Task` and related terms returned nothing), so the review was performed by the running agent itself as a read-only pass (Read/Grep/Glob only) using the skill's quoted prompt verbatim. Both reviewer reports in `reports/` state this.
- Verify step: the skill names `npm run lint` and `npm run test`; this is a Python project, so `python3 -m pytest -q` was used instead. No lint step was run (none configured).
- The brief's report path was mangled (`.../claude-review-loop-out//home/claude/bench/runs/claude-review-loopRT.md`); written as `/home/claude/bench/runs/claude-review-loop-out/REPORT.md` per the caller's instruction.

## Rounds

| Round | Reviewer findings | Fix | Skip | Verifier after fixes |
|-------|-------------------|-----|------|----------------------|
| 1 | 11 | 10 | 1 | 29 passed (12 original + 17 added) |
| 2 (re-review of changed lines) | 5 (all LOW/INFO) | 0 | 5 | 29 passed |

Reports: `reports/round1-reviewer.md`, `reports/round1-fixlist.md`, `reports/round2-reviewer.md`, `reports/round2-fixlist.md`.

## Agent (subagent) calls

0. No subagent tool was available; see Substitutions. The running agent is claude-fable-5-1.

## What was fixed

### ratelimit/limiter.py
- `RateLimiter.allow` and `SlidingWindow.allow`: `except Exception: return True` changed to `return False` (fail closed).
- `RateLimiter.allow`: the whole read-refill-write sequence now runs under `self._lock`; `_snapshot` removed. `stats` increments moved inside the lock.
- Token bucket now holds float tokens; refill is `tokens + elapsed * rate` (no `int()` truncation); admit when `tokens >= 1.0`. On denial the bucket entry is left untouched, so refill is always one product from the last admit rather than a sum of small increments (ten increments of 0.1 drift to 0.999... and never admit). `elapsed` clamped at 0.
- `SlidingWindow.allow`: `t >= cutoff` changed to `t > cutoff` so a stamp exactly `window` old no longer counts, matching the docstring.

### ratelimit/config.py
- Unknown keys rejected with `ConfigError` (`KNOWN_KEYS` was defined but unused).
- `burst` and `window` now rejected when non-positive (previously only `rate` was checked).
- `bool` values rejected for all three; NaN/inf rejected for `rate` and `window`; non-integral floats rejected for `burst`. Numeric strings still accepted (frozen `test_values` requires it).

### tests/test_limiter.py (additions only)
`test_refill_strict`, `test_fractional_rate_refills`, `test_slow_rate_polled_often_still_refills`, `test_fail_closed_on_clock_error`, `test_sliding_window_boundary`, `test_thread_safety_never_exceeds_burst` (16 threads x 100 calls, burst 50, asserts exactly 50 admitted and exact stats).

### tests/test_config.py (additions only)
`test_unknown_key`, `test_rejects_bad_values` (10 parametrised cases).

No public signature or existing test was changed.

## Unfixed

- Round 1 #7: `SlidingWindow` has no `stats` attribute. Skipped as scope creep: not among the README requirements, and `stats` as it exists today (on `RateLimiter`) is frozen.
- Round 2 items 1-5: LOW/INFO confirmations of intended behaviour, no action needed.
- Noted, not raised by review: `SlidingWindow` retains stale stamps for idle keys until the next `allow` (memory, not correctness); constructors do not validate arguments (signatures frozen, validation lives in `load_config`).

## Final verifier output

```
$ cd /home/claude/bench/runs/claude-review-loop && python3 -m pytest -q
.............................                                            [100%]
29 passed in 0.04s
```
