# Hill-climb report: ratelimit library

Repository: /home/claude/bench/runs/hill-climb (branch `master`). Commits are local only; nothing pushed, no branches created.
SHA range: aa358df (v1, original) .. 374c051. Fix batches: d1ca561 (round 1), 6073574 (round 2), 824db6a (round 3). 374c051 only untracks `__pycache__` files that `git add -A` had tracked by mistake in d1ca561; it changes no source.

Note on the brief: the brief's report path is written as `/home/claude/bench/runs/hill-climb-out//home/claude/bench/runs/hill-climbRT.md`, which looks like a template substitution error for `REPORT.md`; the report is written as `/home/claude/bench/runs/hill-climb-out/REPORT.md` as the task instruction specified.

## Step 0 contract

- Objective: `python3 -m pytest -q` passes and a reviewer reading the whole library cold, knowing the four README requirements, finds no correctness defect.
- Frozen: `RateLimiter(rate, burst, clock=)`, `SlidingWindow(limit, window, clock=)`, `allow(key) -> bool`, `reset(key)`, `stats`, `load_config(dict) -> Config`, `ConfigError`, and all twelve original tests (tests may be added or tightened). Base is the single commit aa358df; the whole tree is the change.
- Verifier: `cd /home/claude/bench/runs/hill-climb && python3 -m pytest -q` (Python 3.13, pytest 9.1.1).
- Stopping rules 1 to 3 apply; cap three critic calls (user-named). Critics on opus, verifier on sonnet (author model is fable, a different family).

## Which rule stopped the climb

Rule 4, the cap of three critic calls. Rule 1 never fired: every cold read reported confirmed blocking findings (8, 2, 6). The final critic's confirmed blocking and misleading findings were applied only where the verifier covers the edit (a test was added for each), per the skill's rule 2; the two owner-decision items were not fixed.

Because the cap was already reached, the final call was a single critic rather than the two parallel critics the skill prefers for the delivered version; a second persona prompt was prepared (`prompts/critic-round3b.md`) but not run.

## Trajectory table

Counts are confirmed findings after the verifier step; Disputed holds items the verifier did not confirm.

| Round | Reviewed | Critic | Blocking | Misleading | Minor | Disputed |
|---|---|---|---|---|---|---|
| 1 | aa358df | opus (via `claude -p`) | 8 | 2 | 1 | 0 |
| 2 | d1ca561 | opus (via `claude -p`) | 2 | 2 | 4 | 2 |
| 3 | 6073574 | opus (via `claude -p`) | 6 | 4 | 3 | 1 |

Round 2 note: the critic ranked constructor validation (item 2) and the NaN clock (item 4) blocking; the verifier confirmed both at misleading, and the verifier's rank stands. Round 3 note: the critic ranked item 11 (bucket contention test cannot detect a missing lock) blocking; the verifier confirmed it for the token-bucket test only and refuted it for the sliding-window test, so it is recorded as disputed. Minor counts are critic counts (minors were not sent to the verifier).

What changed per round (design and claims; wording fixes omitted):

- Round 1: `allow` fails closed instead of open; token bucket refills as a float with the timestamp only advanced on refill (rate 0.5 and sub-second polling now work); the whole read-compute-write is under the lock; sliding window boundary uses strict comparison; `load_config` validates every field (finite, positive, not bool, integral burst) and rejects unknown keys; 29 tests added, one vacuous assertion tightened.
- Round 2: sliding-window boundary made robust to float rounding; constructors validate their arguments and raise `ConfigError`; a NaN clock denies; contention tests that actually detect a removed lock (verified: 10/10 failures with the lock removed); 23 tests added.
- Round 3: clock read inside the lock (a stale read after waiting on the lock caused double admission); token comparison tolerates 1e-9 accumulated rounding (rate 0.1 now admits at t=10, not t=11); huge-int constructor args raise `ConfigError` not `OverflowError`; window tolerance is `4*ulp(now)` absolute rather than relative to the window; failure paths count a denial in `stats`; `load_config` accepts only int, float and str (bytes and `"1_0"` rejected, `"4.0"` accepted) and any `collections.abc.Mapping`; 11 tests added, each shown to fail on the previous commit.

## Subagent calls

The Agent tool was not available in this session (ToolSearch found no Agent, Task or similar tool). Applying the brief's substitution rule in reverse, each cold agent was run as a fresh `claude -p` process (Claude Code 2.1.316, installed locally) with the same prompt and tools restricted to `Read,Bash,Glob,Grep`, told to edit nothing and not read git history. Six calls in total:

| Call | Role | Model | Prompt file | Report file |
|---|---|---|---|---|
| 1 | Critic, round 1 | opus | prompts/critic-round1.md | reports/round1-critic.md |
| 2 | Verifier, round 1 | sonnet | prompts/verifier-round1.md | reports/round1-verifier.md |
| 3 | Critic, round 2 | opus | prompts/critic-round2.md | reports/round2-critic.md |
| 4 | Verifier, round 2 | sonnet | prompts/verifier-round2.md | reports/round2-verifier.md |
| 5 | Critic, round 3 | opus | prompts/critic-round3a.md | reports/round3-critic.md |
| 6 | Verifier, round 3 | sonnet | prompts/verifier-round3.md | reports/round3-verifier.md |

Fix lists acted on: reports/round1-fixlist.md, round2-fixlist.md, round3-fixlist.md. Full-tree diffs handed to critics: diff-v1.patch, diff-v2.patch, diff-v3.patch (all under /home/claude/bench/runs/hill-climb-out/).

Coldness caveat: each `claude -p` process may have loaded the user's memory; nothing in memory describes this library, so the critics were not primed on the subject.

## What was fixed, file by file

ratelimit/limiter.py
- `except Exception: return True` -> `return False` in both limiters (fail closed), with the denial counted in `stats`.
- Token bucket: tokens stored as float; refill `tokens + elapsed * rate` without `int()`; `last` advanced only when elapsed > 0; admit when `tokens >= 1.0 - 1e-9`.
- Whole read-compute-write under `self._lock`, including the clock read; `_snapshot` removed.
- Non-finite clock value denies in both limiters.
- Sliding window: a stamp counts only if its age is strictly less than `window`, with ages within `4*math.ulp(now)` of `window` treated as expired (`_in_window`).
- Constructors validate: numeric (not bool), finite, `rate`/`window` > 0, `burst`/`limit` whole and >= 0; `OverflowError` on huge ints mapped to `ConfigError`.
- `_count_denied` helper so the `except` path updates `stats` under the lock.

ratelimit/config.py
- Unknown keys rejected using `KNOWN_KEYS`.
- Shared `_to_float`: accepts int, float, str only; rejects bool, bytes, strings containing `_`, non-finite values; `OverflowError` caught.
- `_positive_float` (rate, window) requires > 0; `_positive_int` (burst) requires whole and > 0, accepting `4.0` and `"4.0"`, rejecting `2.9`.
- `isinstance(raw, Mapping)` instead of `dict`.
- Docstring states the accepted type set.

tests/test_limiter.py
- `test_refill` tightened from `in (True, False)` to `assert rl.allow("a")`.
- Added: fractional rate (0.5 and 0.1) refill timing; sub-second polling; burst cap; fail-closed on raising clock, NaN clock and unhashable key; exact-window boundary with whole and fractional timestamps; 30-day window not expiring early; contention tests with a plain key and with a GIL-yielding key (the latter fails deterministically with the lock removed); clock-read-under-lock test; constructor validation tables; huge-int rejection; zero burst/limit deny everything; stats on failure paths.

tests/test_config.py
- Added: parametrised invalid-config table (unknown keys, non-positive, nan/inf, bool, non-integral burst, None, list, dict, bytes, underscore strings); integral float and `"4.0"` burst accepted; `UserDict` accepted.

## What remains unfixed and why (owner's list)

Owner decisions (confirmed misleading, final call; not the author's call to make):
1. `stats` exists only on `RateLimiter`. The frozen API lists `stats` without naming a class. Either add `stats` to `SlidingWindow` or state in the README that it is token-bucket only. Also, `stats` is a live dict: a reader can see one counter updated before the other; a `stats` property returning a copy taken under the lock would fix that but changes the frozen attribute's type from dict to property, so it is left to the owner.
2. Zero `burst`/`limit` is accepted by the constructors (deny everything) but `load_config` rejects `burst: 0`, and the README says non-positive values are rejected. Decide whether zero is legal, then align constructors, `load_config` and README. A test currently pins the constructor behaviour (`test_zero_burst_and_zero_limit_deny_everything`, added in round 2); it may be changed if the decision goes the other way.

Still disputed at the end:
3. Round 2 critic: `Config` has no `limit` field, so nothing configures `SlidingWindow`. Verifier: a missing feature, not a defect; the README does not require the mapping. Owner to decide whether `Config` should drive `SlidingWindow`.
4. Round 3 critic: `test_token_bucket_never_over_admits_under_contention` cannot detect a missing lock. Verifier: true for the token-bucket test, false for the sliding-window one. The `_YieldingKey` tests cover the lock deterministically, so the plain-key test is redundant rather than wrong; left in place.

Minors not covered by a verifier (from the round 3 critic):
5. `_positive_int` reports `2**53+1` as "must be a whole number"; the rejection is right, the message is misleading.
6. `Config` does not validate itself: `Config(rate=-1, burst=0, window=nan)` constructs. A `__post_init__` check would fix it; left because `Config`'s construction path is frozen API and the choice to validate there is the owner's.
7. `_buckets` and `_log` grow one entry per distinct key and never evict; `SlidingWindow` stores an empty list even for denied keys. Eviction policy is a design decision.

Spec ambiguity carried from round 1 (misleading, confirmed):
8. The frozen test `test_values` requires numeric strings (`"2.5"`, `"4"`) to be accepted while the README says wrong types are rejected. The code now documents the accepted set (int, float, numeric str; not bool, bytes or underscore strings). The README itself was not edited; the owner should state the type set there.

Assumptions no cold reader could check:
9. The GIL-yielding contention tests rely on `time.sleep(0)` inside `__hash__` forcing a thread switch under CPython; they were shown to fail 10/10 with the lock removed on CPython 3.13 but may be weaker on a free-threaded or alternative interpreter.
10. The window tolerance of `4*math.ulp(now)` assumes the clock returns values whose subtraction error is a few ulps; a clock with coarser internal rounding could still land stamps on the boundary.

## Final verifier output

```
$ cd /home/claude/bench/runs/hill-climb && python3 -m pytest -q
........................................................................ [ 96%]
...                                                                      [100%]
75 passed in 1.09s
```
