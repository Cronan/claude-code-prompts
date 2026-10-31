# Hill-climb head-to-head, 31 October 2026

Four review-and-fix loop skills, each run by a fresh agent following its SKILL.md literally on identical copies of three artefacts. Reviewers were separate `claude -p` processes where the skill asked for a fresh reader (opus critics and sonnet verifiers for hill-climb; sonnet reviewers for the rest, opus for loop-review's architect). Two batch-one runs (loop-review, claude-review-loop) reviewed in-session because those agents did not find the CLI; noted where it matters. Scoring was mechanical where possible (hidden pytest suite) and by a cold opus grader otherwise. One run each; treat differences of one as noise.

## Artefact A: defective code (6 seeded defects, 4 frozen checks)

| Contender | Seeds fixed | Frozen kept | Cold reviewer | Rounds | Lines changed | Findings: seed / real / scope / false |
|---|---|---|---|---|---|---|
| hill-climb | 6/6 | 4/4 | yes | 3 (cap) | +476 / -32 | 6 / 4 / 26 / 1 |
| reviewloop | 6/6 | 4/4 | yes | 3 (cap) | +546 / -38 | 5 / 2 / 14 / 1 |
| loop-review | 4/6 | 4/4 | no | 1 | +160 / -22 | 6 / 1 / 1 / 0 |
| claude-review-loop | 5/6 | 4/4 | no | 2 | +144 / -26 | 6 / 0 / 2 / 1 |

loop-review named all six seeds but parked the window-boundary fix as "needs your decision" under its behaviour-change rule and missed the tautological test. claude-review-loop missed only the tautological test. Both cold-reviewer loops fixed everything and both ran to the cap without converging.

## Artefact B: correct code (same library, seeds fixed; measures corruption and over-editing)

| Contender | Frozen kept | Hidden tests | Rounds | Lines changed | Critic's round-1 blocking | Verifier-confirmed |
|---|---|---|---|---|---|---|
| hill-climb | 4/4 | 15/15 | 3 (cap) | +249 / -10 | 10 | 8 |
| reviewloop | 4/4 | 15/15 | 3 (cap) | +333 / -20 | 13 findings | n/a |
| loop-review | 4/4 | 15/15 | 1 | +62 / -23 | 15 findings | self-challenged |
| claude-review-loop | 4/4 | 15/15 | 2 | +115 / -11 | 9 findings | triage: 7 fix |

No contender broke frozen behaviour. Every contender edited a correct library, and every reviewer reported blocking defects in it (NaN rate, inf burst, bool coercion, OverflowError escaping, clock read before the lock). All are real edge cases; none is in the stated requirements. hill-climb's verifier recorded zero disputed findings across three rounds. reviewloop oscillated: round 2 reverted round 1's constructor validation, round 3 reverted round 2's Mapping acceptance.

## Artefact C: runbook (6 seeded defects; frozen: under 80 lines, section order, numbering)

| Contender | Seeds fixed | Frozen kept | Introduced blockers | Invented facts | Lines / steps |
|---|---|---|---|---|---|
| hill-climb | 6/6 | yes | 0 | 1 | 67 / 15 |
| reviewloop | 6/6 (one fix broken) | yes | 3 | 4 | 65 / 18 |
| loop-review | 6/6 (one fix broken) | yes | 1 | 0 | 68 / 14 |
| claude-review-loop | 6/6 | yes | 0 | 2 | 73 / 15 |

reviewloop's P3 fix sets `NEW_KEY` with `read -rs` and never exports it, so `sudo --preserve-env` passes nothing and rotation can never succeed; it delivered that version at the cap with the blocker listed as open. loop-review records a UTC start time that `journalctl --since` reads as local. hill-climb delivered v3, the version its last critic read, and put round 3's unverifiable fixes on the owner's list.

## What the numbers say about hill-climb

The final-call rule works. hill-climb and claude-review-loop both delivered prose with zero introduced blockers; the two that applied final-round fixes unreviewed shipped broken commands.

The verifier does not. Across code runs it confirmed every finding the critic sent it (0 disputed in six rounds), downgraded some, and caught 2 of 18 out-of-scope items the grader identified. On the correct library it confirmed 8 blocking. A sonnet verifier checking an opus critic's claims one by one is asking "could this be true", and almost anything can; it is not asking "is this in the contract" or "can I make it fail".

The reduced-cap rule never fires. It triggers on "first critic reports zero blocking", and no critic in twelve runs reported zero blocking on anything, including the correct library. The trigger has to be on confirmed in-scope blocking, after a scope gate.

Scope inflation is the dominant cost. 26 of hill-climb's 37 findings on the defective library were out-of-scope hardening; it changed 476 lines where claude-review-loop changed 144 for one fewer seed. The critic's brief says "report only what would change a reader's action or a stated requirement", but the ranking row for code ("incorrect behaviour against the stated intent") is read by critics as "any incorrect behaviour". The scope test has to be applied by the verifier, mechanically, against the Step 0 objective.

Findings against the climb's own additions. hill-climb's round 3 on the defective library reported 6 blocking, mostly against tests added in rounds 1 and 2 (contention tests that could not detect a missing lock, a tolerance that admits early). That is the skill working as designed, tests added are in scope, but it means test volume is a direct driver of later rounds.

Cold critics need a working verifier. The round-1 critic on the clean library could not run pytest because `claude -p` stopped at an approval prompt; it reviewed from reading alone. The skill's CLI fallback has to pass the verifier command as an allowed tool.

## What the others do better

loop-review's "Done" rule stopped it after one round on the correct library with the smallest diff of the four; its rule that the final round makes no behaviour change unless the finding is a blocker is the same instinct as hill-climb's final-call rule, and its "challenge each finding, mark confirmed, unconfirmed or wrong" is done by the orchestrator against the code rather than by a second reader, which on this evidence filtered better than hill-climb's verifier (1 scope finding versus 26).

claude-review-loop's "re-review only the newly changed lines" in later rounds is why its rounds 2 and 3 produced almost nothing; hill-climb's full re-read regenerates scope findings every round.

reviewloop's acceptance list (one checkable line per requirement, re-checked every pass) is a cleaner statement of scope than hill-climb's objective sentence, and its "never launder a finding" guard has no counterpart in hill-climb.

Nothing in the others matches the trajectory table, versioned rounds, or the owner's list; reviewloop delivered a known-broken runbook because it has no equivalent of the final-call rule.

## Changes to make, in order

1. Scope gate in the verifier. Each confirmed finding is also classed in-scope (breaks a stated requirement, the frozen behaviour, or the artefact's own stated contract such as a docstring) or out-of-scope. Only in-scope findings enter the fix batch; out-of-scope ones go to the owner's list whatever their rank. The verifier gets the Step 0 objective and frozen behaviour as the test, and is told that on a sound artefact most findings will be out of scope.
2. Verifier must reproduce, not reason. For code: a blocking claim is confirmed only by a failing test or a run that shows the behaviour; for a document: by quoting the two sentences that contradict or the step that cannot be taken. "Plausible" is not confirmed. The verifier runs on a model at least as capable as the critic, briefed as the author's advocate.
3. Reduced cap triggers on zero confirmed in-scope blocking in round 1, not on the critic's raw tally.
4. Cold-critic ladder: Agent tool; then `claude -p --no-session-persistence --model M --allowedTools "Read,Grep,Glob,Bash(VERIFIER)"`; then same-session labelled "not cold". Record the rung in the trajectory table.
5. Cost columns in the trajectory table: lines changed and reviewer processes, so the owner can see 476 lines for 6 seeds.
6. One test per confirmed finding, no more; tests the climb adds are in scope but a round-3 finding against a round-1 test that the verifier cannot make fail is minor.
7. Executable documents: a fix may not introduce a fact about the environment that the original does not state (a log line, a validity period, a URL); use a named placeholder. Add to frozen behaviour for that artefact type.
8. Later-round critics get the diff from the previous version alongside the full artefact, and are told that findings outside the diff must be blocking to be reported. This keeps the "no knowledge of what changed" rule's intent (no fix list, no previous report) while stopping full-file scope regeneration.

Not changed: the final-call rule, versioning, the owner's list, the ranking table, "no rewriting". The evidence supports all of them.

## Caveats

One run per cell; variance across runs was not measured. The hidden tests cover the six seeds and four frozen behaviours only; "no corruption" means none detected by them. Two batch-one runs were not cold. The grader is itself an LLM; its FALSE classifications rest on a simulation, not a threaded reproduction, and it says so. All reviewers were Anthropic models.
