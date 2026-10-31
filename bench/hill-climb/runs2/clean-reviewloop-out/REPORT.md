# Reviewloop report: ratelimit

Repository: /home/claude/bench/runs2/clean-reviewloop (branch `master`, one commit `12f2fd5 ratelimit v1`; the whole tree was the change under review).
Skill: /home/claude/bench/skills/reviewloop.md with reviewloop-REFERENCE.md. Verifier: `python3 -m pytest -q` (substituted for the skill's npm commands).

## Resumption note

The original run died after writing `reports/round3-fixlist.md` and before writing this report. A second agent resumed at that point. It read the brief, both skill files, all six saved reports and the working tree, confirmed that the round-3 fix list was (by design) not applied and that the tree is in the round-2 state, re-ran the verifier, and wrote this report. No further review rounds were run and no code was changed during the resumption. Two untracked `__pycache__` directories left by earlier pytest runs were removed.

## Stopping rule

**Iteration cap.** The brief set the cap at 3. Round 3's reviewer pass returned eight findings, so the loop did not converge; per the skill's guard ("At the cap, stop and hand the user the open findings with what was tried") the loop stopped and the round-3 findings are handed over below, unfixed.

A secondary guard also fired: **oscillation**. Round 2 reversed round 1 on constructor validation and logging, and round 3 reversed round 2 on `MappingProxyType` and `Decimal` acceptance. The skill says to ask the user rather than iterate; the brief said to treat confirmation as given, so the operator took the resolution both reviewers could accept (details under round 2).

## Rounds

Reviewer processes run: **3**, one per round, each `claude -p --no-session-persistence --model sonnet --disallowedTools Edit,Write,Bash` given only the acceptance list and the diff scope (read-only, verifier not run by the reviewer). Reports saved verbatim in `reports/`.

| Round | Reviewer report | Findings | Fix list | Applied |
|---|---|---|---|---|
| 1 | round1-reviewer.md | 13 (11 actionable, 2 noted) | round1-fixlist.md | yes |
| 2 | round2-reviewer.md | 7 | round2-fixlist.md | yes (with the oscillation resolution below) |
| 3 | round3-reviewer.md | 8 (low severity, none breaking README items 1-4) | round3-fixlist.md | no: cap fired |

### Round 1: 13 findings
config.py: bool accepted; NaN/inf accepted; non-integral `burst` truncated; bare `OverflowError`; bare `TypeError` on mixed-type unknown keys. limiter.py: `SlidingWindow` clock read outside the lock; NaN clock or window fails open in `SlidingWindow`; NaN clock / inf rate poisons `RateLimiter`; `reset()` behaviour on unhashable key unspecified; exception-path denials uncounted and silent. Tests: nothing for README items 1-4. Plus two summary/pre-existing notes (unbounded per-key state, not in scope). All actionable items fixed.

### Round 2: 7 findings
Logging in the except handler can itself raise; constructor validation is scope creep against the frozen constructors; `_number` rejects `Decimal`; `isinstance(raw, dict)` rejects other mappings; `stats` is a live public dict read without the lock; per-key state never evicted (pre-existing); test coverage and import-placement gaps. Resolution of the oscillation with round 1: constructors keep their frozen, unvalidated behaviour and `allow()` fails closed on bad parameters at request time (which is what README item 3 asks for); logging removed; error denials still counted in `stats["denied"]` because an uncounted False makes `stats` wrong. `stats` left as is (frozen public attribute compared by equality in existing tests). Eviction out of scope.

### Round 3: 8 findings (open, see "What remains")

## What changed, file by file

Net diff against `12f2fd5`: 4 files, +333/-20. No new files; no branches or pushes.

**ratelimit/config.py**
- Added `_number(name, value)` helper: rejects bool and anything not `numbers.Real`, `Decimal` or `str`; converts via `float()` catching `TypeError`, `ValueError`, `OverflowError` and re-raising `ConfigError`; rejects non-finite and non-positive values.
- `load_config` accepts any `collections.abc.Mapping` instead of only `dict`.
- Unknown keys sorted with `key=repr` so mixed-type keys cannot raise `TypeError`.
- `burst` parsed through `_number`, rejected with `ConfigError` unless `.is_integer()`, then converted to `int`.
- Public signatures `load_config(dict) -> Config` and `ConfigError` unchanged.

**ratelimit/limiter.py**
- `import math`.
- `RateLimiter.allow`: denies (raises into the except path) if the clock value is non-finite or if the computed token count is non-finite; the except path increments `stats["denied"]` under the lock (itself guarded) and returns False. Docstring documents the fail-closed cases.
- `RateLimiter.reset`: docstring specifies `TypeError` for unhashable key and that nothing is admitted.
- `SlidingWindow.allow`: clock read and cutoff computation moved inside `with self._lock`; denies if cutoff is non-finite or not strictly less than `now`; docstring added.
- `SlidingWindow.reset`: docstring as above.
- Constructors untouched; no logging; `_number` not imported across modules (round-1 versions of both were reverted in round 2).

**tests/test_config.py** (+64)
- `test_other_non_mappings_rejected` (None, str, int, set), `test_non_dict_mapping_accepted` (MappingProxyType), `test_decimal_and_lenient_strings_accepted` (Decimal, " 5 ", "1_0"), `test_sub_one_per_second_rate_accepted`, `test_integral_float_burst_accepted`, and a parametrised `test_invalid_config_rejected` matrix (bool, None, list, dict, bad strings, bytes, Decimal NaN/negative, non-positive, nan/inf as float and string, 1e999, 10**400, non-integral burst, unknown keys, mixed-type unknown keys).

**tests/test_limiter.py** (+198)
- Imports at top. `_hammer` helper with barrier-started threads and a fixed `FakeClock`.
- `test_sub_one_per_second_rate` (rate=0.5, burst=1 timeline), `test_rate_limiter_concurrent_never_exceeds_burst`, `test_sliding_window_concurrent_never_exceeds_limit`, `test_clock_read_under_lock`, parametrised `test_fail_closed` (clock raising, clock returning None/str, unhashable key), `test_rate_limiter_exception_denials_counted`, `test_nan_clock_does_not_poison_bucket`, `test_reset_unhashable_raises_and_admits_nothing`, parametrised request-time fail-closed tests for bad `rate`/`burst` (nan, inf, str, None) and bad `limit`/`window` (nan, inf, 0, negative), and `test_rate_limiter_parameter_mutated_after_construction_fails_closed`.
- All 12 pre-existing tests unchanged and passing.

## What remains (round 3, unfixed)

Operator disposition from round3-fixlist.md; nothing below has been changed in the tree.

1. **Concurrency tests would likely pass without the lock** (tests/test_limiter.py). Deterministic pinning needs a yield injected between read and write, which needs a seam in the frozen class. Only `test_clock_read_under_lock` reliably pins the lock. Open.
2. **`cutoff < now` guard denies valid tiny windows against large clocks** (limiter.py `SlidingWindow.allow`): `SlidingWindow(5, 1e-9, clock=time.time)` is denied forever because `now - 1e-9 == now` in float. Agreed, the round-2 guard is too strict. Suggested fix: keep `math.isfinite(cutoff)`, drop `cutoff < now`, deny `window <= 0` with an explicit check. Open.
3. **Non-integral `limit` admits more than the limit**: `SlidingWindow(limit=2.5, window=10)` admits 3. Agreed; needs a fail-closed integrality check on `limit` in `allow()`. Open.
4. **`burst` integrality checked after float conversion**: `load_config({"burst": 2**53 + 1})` returns `2**53`. Agreed; check integrality on the original value. Open.
5. **Accepted/rejected inputs changed beyond the list** (`MappingProxyType`, `"5.0"`, `b"1"`). Partly disputed: MappingProxyType and Decimal acceptance were round-2 findings 3 and 4 from the same reviewer model, so this is the oscillation the skill warns about. Needs a user decision on how wide "mapping" and "number" should be.
6. **Clock going backwards stores negative tokens** in `RateLimiter`. Fail-closed, not unsafe, and outside the four README requirements; clamp `elapsed` at 0 if wanted. Open.
7. **README not updated** for the new rejection rules (NaN/inf, non-integral burst, bool, numeric strings, `reset` raising `TypeError`). Not in the skill argument; cheap to do. Open.
8. **`except Exception` does not catch `BaseException`** (SystemExit, KeyboardInterrupt from the clock). No action recommended: swallowing those would be wrong.

Also carried from round 2 as reported-not-changed: `stats` is a live public dict read without the lock (frozen attribute, cannot be replaced); per-key state is never evicted (pre-existing, out of scope).

## Final verifier output

```
$ cd /home/claude/bench/runs2/clean-reviewloop && python3 -m pytest -q
........................................................................ [ 98%]
.                                                                        [100%]
73 passed in 0.05s
exit=0
```

Run by the resuming agent on 2026-10-31 against the working tree as left by round 2. The repository has no lint or build step.
