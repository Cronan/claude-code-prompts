# loop-review benchmark report

Repository: /home/claude/bench/runs/loop-review (revision aa358df, clean tree at start). Skill: /home/claude/bench/skills/loop-review.md. Arguments: goal "harden the ratelimit library so it meets the four README requirements"; scope=ratelimit,tests; max_rounds=3; checks=python3 -m pytest -q; confirm=yes.

## Which rule stopped the loop

**Done**, after round 1 (cap was 3). All four definition-of-done conditions are demonstrated by tests that now pass, and no confirmed in-scope finding of medium severity or above remains. The one open item (A-5, low) is an Ask, not a defect against the four requirements. Per the skill's hard rule 4, no further round was started.

Consequence the skill requires me to state: the round 1 fixes were not seen by any reviewer. They are verified by the check and by the regression tests listed below, not by a second review.

## Rounds

| Round | Reviewers run | Findings raised | Deduplicated root causes | Accepted | Rejected | Ask | Backlog |
|---|---|---|---|---|---|---|---|
| 1 | tester (5), builder (5), architect (5), design critic (0) | 15 | 6 | 5 | 0 | 1 (A-5) | 0 |

## Agent (subagent) calls

**Zero.** No Agent or Task tool exists in this session (ToolSearch for "Agent", "subagent", "spawn" returned only SendMessage, TaskStop, EnterWorktree; no `claude -p` or `codex` CLI either). The skill's hard rule 5 says never claim a review ran if it did not, so: the four reviewer roles were performed by the orchestrator itself (model claude-fable-5-1), each written up in that role's required output format using only Read, Grep and Glob of the repository as evidence, and each saved verbatim under reports/ with a header stating this substitution. The models the agent definitions name (sonnet for tester/builder/design-critic, opus for architect) were therefore not used. The reviews were not independent of the orchestrator, which weakens the "fresh eyes" property the skill relies on; findings were nonetheless each reproduced by running the code before any fix was applied (see reports/round1-fixlist.md).

Reports: reports/round1-tester.md, round1-builder.md, round1-architect.md, round1-design-critic.md, round1-fixlist.md.

## What was fixed, file by file

ratelimit/limiter.py
- `RateLimiter.allow`: `except Exception: return True` -> `return False` (T-1/B-1/A-2, fail closed).
- `RateLimiter.allow`: whole read-modify-write, the clock call and both `stats` increments are now inside one `with self._lock:` block; private `_snapshot` removed (T-2/B-2/A-1, thread safety).
- `RateLimiter.allow`: tokens kept as float, `int(elapsed * rate)` truncation removed, admit at `tokens >= 1`, bucket not rewritten on deny so fractional credit accrues from the last admit as one multiplication (T-3/B-3/A-3, sub-1/s rates; also avoids the float-drift failure that the first attempt, which stored the fraction on each deny, produced in `test_fractional_credit_survives_frequent_polling`).
- `SlidingWindow.allow`: `except Exception: return True` -> `return False` (T-1); clock call moved inside the lock (T-5/B-5).

ratelimit/config.py
- `load_config`: rejects unknown keys (KNOWN_KEYS now actually consulted), bool values, non-integral float `burst`, non-finite or non-positive `rate` and `window`, non-positive `burst`; all with `ConfigError`. String coercion kept so the frozen `test_values` still passes (T-4/B-4/A-4). `import math` added.

tests/test_limiter.py (added, none edited)
- `test_rate_limiter_fails_closed_on_clock_error`, `test_sliding_window_fails_closed_on_clock_error`
- `test_sub_one_per_second_refill` (rate 0.5: deny at t=1, admit at t=2), `test_fractional_credit_survives_frequent_polling` (rate 0.1 polled every second, admits on the tenth), `test_refill_strict` (strict sibling of the frozen tautological `test_refill`)
- `test_rate_limiter_never_over_admits_under_contention` and `test_sliding_window_never_over_admits_under_contention` (16 threads x 50 calls behind a barrier; exactly 5 admits, stats consistent)

tests/test_config.py (added, none edited)
- `test_invalid_config_rejected` parametrised over 18 invalid inputs; `test_sub_one_per_second_rate_accepted`; `test_integral_float_burst_accepted`.

Frozen public signatures unchanged. No existing test edited. Nothing committed; `git diff` shows every change. Pytest cache directories created by the runs were removed so the tree shows only the four modified files.

## What remains unfixed and why

- **A-5 (low, Ask):** `SlidingWindow` docstring says a stamp exactly `window` seconds old no longer counts; the code keeps `t >= cutoff`, so it does. Traced example: `SlidingWindow(1, 10.0)`, allow at t=0, advance 10.0, allow -> False. Either changing `>=` to `>` or rewording the docstring is caller-observable and outside the four README requirements, so under hard rule 8 it needs a product decision.
- **Thread tests are probabilistic.** They pass consistently (3 of 3 full runs) and the deterministic argument is inspection that the entire `allow` body is under the lock, but a scheduler could in principle fail to interleave. This is a limit of the verifier, not an open defect.
- **Constructor validation out of scope.** `RateLimiter(0, -1)` is still accepted directly; README requirement 4 is about `load_config`, so this was not changed (builder's out-of-scope note).
- **Config to limiter wiring absent.** `Config.window` is loaded but nothing consumes a `Config`; a feature, not in scope (architect's out-of-scope note).

## Final verifier output

```
$ cd /home/claude/bench/runs/loop-review && python3 -m pytest -q
.......................................                                  [100%]
39 passed in 0.07s
```

Baseline before fixes: 12 passed. After: 39 passed (12 original + 27 added), run three times to exercise the thread tests.
