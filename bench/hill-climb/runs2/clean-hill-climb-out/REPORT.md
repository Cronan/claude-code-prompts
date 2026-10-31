# Hill-climb report: ratelimit

Repository: /home/claude/bench/runs2/clean-hill-climb, branch `master`, commits left local. Skill: /home/claude/bench/skills/hill-climb.md. Verifier: `python3 -m pytest -q` (substituted for the skill's npm commands, as the brief directs).

## Resumption

The run was resumed after the original agent died. State found at resumption:

- Commits `12f2fd5` (v1) and `59dba6a` (fix batch 1) on `master`; working tree clean.
- Saved reports: round1-critic, round1-verifier, round1-fixlist, round2-critic (plus an aborted round-2 critic that was given the wrong prompt and produced no review), round2-verifier.
- Round 2's fix list had not been written and its fix batch had not been applied (no diff, no third commit).

The climb resumed at Step 2 of round 2: writing round2-fixlist.md from the round-2 verifier's confirmed findings, applying the batch, committing, then running round 3. The contract set by the first agent was kept: objective "verifier passes and a cold reviewer knowing the README's four requirements finds no correctness defect"; frozen behaviour as the brief lists it; verifier pytest; cap 3 critic calls (brief). The round-1 critic reported 10 blocking (8 confirmed), so the reduced-cap rule for a zero-blocking first read did not apply.

## Contract

- Objective: `python3 -m pytest -q` passes and a cold reviewer, knowing the four README requirements, finds no correctness defect.
- Frozen: `RateLimiter(rate, burst, clock=)`, `SlidingWindow(limit, window, clock=)`, `allow(key) -> bool`, `reset(key)`, `stats`, `load_config(dict) -> Config`, `ConfigError`, every test present on `12f2fd5`. Tests may be added or made stricter.
- Verifier: `python3 -m pytest -q` in the repository.
- Stopping rules 1 to 3; cap 3 critic calls (rule 4).

## Which rule stopped the climb

Rule 4, the cap: three critic calls were made. Rule 1 did not fire because the third cold read reported two confirmed blocking items (both fixed afterwards under the skill's final-call rule, since the pytest verifier covers them). Rule 3 did not fire because no read reported zero confirmed blocking.

## Trajectory

Counts are confirmed findings after Step 1b, at the verifier's rank. Minor counts are the critic's, unverified. Disputed is 0 throughout: every claim was confirmed, several at a lower rank.

| Round | Reviewed | Critic | Blocking | Misleading | Minor | Disputed |
|---|---|---|---|---|---|---|
| 1 | 12f2fd5 | opus | 8 | 10 | 2 | 0 |
| 2 | 59dba6a | opus | 2 | 9 | 3 | 0 |
| 3 | cbe7a96 | opus | 2 | 7 | 3 | 0 |

Per-round findings in detail are in `reports/round<N>-critic.md`, `round<N>-verifier.md` and `round<N>-fixlist.md`.

Round 1 (by the first agent): critic found 10 blocking / 8 misleading / 2 minor; verifier confirmed 8 blocking (clock read outside the lock in `SlidingWindow.allow`; NaN/inf config values accepted; `OverflowError` escaping `load_config`; bool and non-integral burst accepted; no tests for threads, fractional rate, fail-closed, or invalid config) and downgraded two (NaN/inf passed directly to constructors) to misleading. Blocking plus misleading exceeded eight, so only the eight blocking were fixed and the ten misleading carried forward. The round-1 critic could not run the verifier (approval prompt); the verifier did.

Round 2: critic found 2 blocking / 7 misleading / 1 minor; verifier confirmed 2 blocking (`sorted(unknown)` raising `TypeError` for mixed-type unknown keys; the concurrency tests passing with the lock removed, upgraded from misleading), 9 misleading, downgraded two to minor. Again more than eight confirmed, so only the two blocking were fixed.

Round 3 (final call): critic found 3 blocking / 6 misleading / 3 minor; verifier confirmed 2 blocking (Decimal/Fraction burst silently truncated; bytes and underscore strings accepted) and downgraded constructor validation to misleading; 7 misleading confirmed. Under the final-call rule, items were applied only where pytest covers the edit: both blocking items, plus the backwards-clock drain and the exact-window edge test. The rest went to the owner's list.

## Reviewer processes run

Seven `claude -p --no-session-persistence` processes in total, six of which produced a usable report:

| Round | Role | Model | Notes |
|---|---|---|---|
| 1 | critic | opus | by the first agent; could not run the verifier |
| 1 | verifier | sonnet (per brief; the saved report does not record it) | by the first agent |
| 2 | critic (aborted) | opus | by the first agent; wrong prompt (pointed at another run's file), produced no review; not counted against the cap |
| 2 | critic | opus | by the first agent |
| 2 | verifier | sonnet (per brief) | by the first agent |
| 3 | critic | opus | this run; `--disallowedTools Edit,Write`, Bash restricted to `python3` so it could run the verifier |
| 3 | verifier | sonnet | this run; `--disallowedTools Edit,Write`, Bash restricted to `python3`, `cp`, `mkdir`, `sed` for scratch-copy probes |

Three critic calls count against the cap. All critics were opus, the same family as the author model; the brief fixed this, so it is noted rather than varied. Memory describes the user's engineering role but not this library, so the critics were not primed on the subject.

## What changed, file by file (12f2fd5 to dd3e584)

`ratelimit/limiter.py`
- `SlidingWindow.allow`: `now = self.clock()` and `cutoff` moved inside `with self._lock:` (batch 1). Previously a preempted thread could log a stale timestamp that left the window early.
- `RateLimiter.allow`: `elapsed = max(0.0, now - last)` and the stored timestamp is `max(now, last)`, so a clock stepping backwards neither drains tokens nor moves the refill point back (batch 3).

`ratelimit/config.py`
- Unknown-key message uses `sorted(map(repr, unknown))` so mixed-type keys raise `ConfigError`, not `TypeError` (batch 2).
- bool rejected for all three keys; `OverflowError` caught; `math.isfinite` checks on rate and window; non-integral float burst rejected (batch 1).
- `ACCEPTED_TYPES = (int, float, str, Decimal, Fraction)`: any other type (bytes, bytearray, None, list, dict) raises `ConfigError` before conversion; the whole-number check for burst is `raw_burst != int(raw_burst)` for every non-string type, so `Decimal("2.9")` and `Fraction(5, 2)` are rejected (batch 3). Numeric strings remain accepted because `test_values` freezes them.

`tests/test_config.py`
- Added: `test_unknown_key`, `test_unknown_keys_of_mixed_types`, a 30-case parametrised `test_invalid_values_rejected` (negative/zero values, bool, None, list, dict, nan/inf as float and string, overflow, non-integral float/Decimal/Fraction burst, bytes, bytearray), `test_integral_float_burst_accepted`, `test_integral_decimal_and_fraction_burst_accepted`.

`tests/test_limiter.py`
- Added: `test_fractional_rate` (0.5/s), `test_fail_closed_on_clock_error`, `_hammer` helper with two fixed-clock concurrency tests (batch 1); `YieldingKey` (a key whose `__hash__` sleeps) with two concurrency tests that fail when the lock is replaced by a no-op (confirmed on a scratch copy, 3 of 3 runs), and `TickingClock` with two tests of refill under contention bounding admissions by the time budget (batch 2); `test_sliding_window_exact_edge_has_left_window` and `test_clock_going_backwards_does_not_drain_or_lock_out` (batch 3).

Not changed: `README.md`, `pytest.ini`, `ratelimit/__init__.py`, all public signatures, all tests present on v1. Tracked `__pycache__` files from v1 were left as committed.

## What remains (owner's list)

Confirmed in round 3, not applied because no verifier covers the edit or the owner must decide:

1. Constructors validate nothing. `RateLimiter(float("nan"), 2)` admits every call (`min(burst, nan)` returns `burst`); `RateLimiter(-1, 3)` and `SlidingWindow(2.5, 10)` misbehave. Decision needed: does README requirement 4 apply to direct construction, and should the constructors raise `ConfigError`? Round-3 verifier rank: misleading.
2. `except Exception: return False` in both `allow` methods logs nothing and does not count the denial in `stats`. Adding an `errors` key to `stats` would break the frozen equality assertions in `test_stats_counts` and `test_token_bucket_concurrent_never_exceeds_burst`, so the shape of `stats` is the owner's call. Misleading.
3. `SlidingWindow` has no `stats`; the frozen interface lists `stats` without naming the class. Decision needed. Misleading.
4. `stats` on `RateLimiter` is the live mutable dict read without the lock; no snapshot accessor. Misleading (round 2).
5. The four fixed-clock and ticking-clock concurrency tests do not detect a missing lock (only the two `YieldingKey` tests do). They stand as count regressions; a docstring saying so is not verifier-covered. Misleading.
6. `_buckets` and `_log` keep every key ever seen, including empty stamp lists; memory grows without bound. Design change. Misleading.
7. `reset` is not wrapped like `allow`: `reset([])` raises `TypeError` while `allow([])` returns False. Minor (round 3), misleading (round 1).
8. Numeric strings (`"2.5"`, `" 2 "`, `" 1_0 "`) are accepted as config values while README says wrong types are rejected; `test_values` freezes `"2.5"` and `"4"`. `"4.0"` is rejected for burst while `4.0` is accepted. Policy question for the owner: write the accepted string forms into the README or drop string acceptance (which would require un-freezing `test_values`).
9. `Config` has no `limit` field, so nothing documents how a `SlidingWindow` is built from config. Minor.
10. `isinstance(raw, dict)` rejects non-dict `Mapping`s although the docstring says "mapping". Minor; rejection is the safe direction.
11. Fail-closed is tested only for a raising clock. Misleading (round 2, 9c).
12. Floating-point edge for the exact-window rule at fractional windows: with `now=0.3, window=0.1`, `cutoff` is `0.19999999999999998`, so a stamp at `0.2` still counts although it was exactly one window ago. Confirmed by the round-1 verifier; the integer-window edge is now pinned by a test but this fractional case is not fixable without a tolerance decision. Misleading.
13. Noticed during the run, not from a critic: `SlidingWindow.allow` rebuilds the full stamp list on every call under the lock; a `deque` with `popleft` would be O(expired) rather than O(n). Round-2 critic ranked it minor.

## Final verifier output

```
$ python3 -m pytest -q
........................................................                 [100%]
56 passed in 0.16s
```

Commit range: `12f2fd5..dd3e584` on `master` (three fix commits: `59dba6a`, `cbe7a96`, `dd3e584`). Nothing pushed; no branches created.
