# /hill-climb

Improves a finished draft in rounds until a stopping rule agreed in advance fires. The draft can be code, a runbook, an essay, an HTML page, a proposal, a prompt or another skill. Each round is one cold critic read, a check of every finding by a second agent, one batch of fixes, and a new saved version. You get back the last version a critic actually read, a table of what each round found, and a list of everything the climb chose not to fix and why.

## Why it is built this way

Three observations shape the design.

1. **Self-review misses most of what matters.** Models fail to correct their own errors about two thirds of the time, yet fix the identical error when it arrives from outside [1, 2]. The critic must not have seen the work being produced.
2. **Fixes introduce defects.** A revision round improves net quality only when its correction rate exceeds its corruption rate multiplied by baseline/(1 - baseline) [3, 4]. At 95% baseline quality the multiplier is 19, so further rounds on a clean artefact tend to do harm. Extra context handed to the fixer is itself a source of corruption [3], so the fixer gets a list of findings, not the critic's prose. Nothing is delivered that no critic has read.
3. **A critic reports blocking defects in a correct artefact.** Longer, harsher critiques carry more invented defects [5]. In the benchmark below, every reviewer, this one included, reported a list of blocking defects in a library that met almost all of its stated requirements, and every loop changed far more code than the few real defects needed. Most of the edge cases were real but outside the requirements. The gate that holds is scope: a finding is fixed only if a second agent reproduces it and ties it to a numbered requirement, to frozen behaviour, or to a contract the artefact states about itself. Everything else goes to the owner.

## How it works

1. **Contract.** Before the first round, the skill writes at most eight lines in the conversation: the objective as numbered requirements, the behaviour no fix may change, the mechanical checks (tests, linters, word counts), a one-line scope test, and the stopping rules and cap.
2. **Cold critic.** A fresh context reads the artefact as the person who will have to live with it: the engineer executing the runbook, the reviewer before merge, the committee member. It is reached through the Agent tool, then a fresh `claude -p` process, then, as a last resort, a same-session review labelled "not cold". Where a model choice exists, the critic runs on a different model from the author, because judges favour text from their own model family even in a fresh context [6, 7]. Findings are ranked blocking, misleading or minor against a definition specific to the artefact type.
3. **Checker.** A second cold agent on the strongest model available, briefed as the author's advocate. For each finding it returns two verdicts: reproduced or not (a failing test, or the two sentences that contradict), and in scope or not. Plausible is not confirmed.
4. **Fix batch.** Only confirmed, in-scope blocking and misleading findings are fixed, with at most one test per finding. Every round is saved as a new version (`name-vN.md`, or one commit per batch) and never overwrites the last.
5. **Next round.** The next critic reads the new version and the diff from the previous one. Outside the diff it reports only blocking findings, so each round does not regenerate the same list. A quality document still failing its brief after two reads gets a fresh parallel draft rather than a third revision [8].
6. **Stop.** The climb stops on a rule that can be read off the trajectory table, never on "zero findings", which a cold reader never reports. The cap is three critic calls for prose and five for code or documents containing shell commands, dropping to two when round 1 finds nothing confirmed, in scope and blocking. Findings from the final critic call are applied only where a mechanical check covers the edit.

Full specification: [`SKILL.md`](SKILL.md).

## What you get back

- The final version, always one a critic has read.
- A trajectory table, one row per round:

| Round | Reviewed | Critic | Blocking | Misleading | Minor | Out of scope | Disputed | Lines |
|---|---|---|---|---|---|---|---|---|
| 1 | v1 | opus/cli | 5 | 3 | 5 | 11 | 2 | +84/-12 |
| 2 | v2 | opus/cli | 1 | 2 | 8 | 4 | 1 | +19/-3 |

- One line per round on what changed the design or the claims.
- The rule that stopped the climb.
- An owner's list: unfixed findings from the final round, out-of-scope hardening suggestions grouped by the requirement each would add, findings still disputed, placeholders for facts only the owner can supply, and anything the artefact assumes that no cold reader could check.

A large out-of-scope column beside a small blocking column means a sound artefact being hardened. The table is laid out so the owner sees that, rather than a tally that looks like a defective one.

## Benchmark

On 31 October 2026 the previous version of this skill was run against three published Claude Code review loops. The current version was then run twice more on the correct library; those results follow the main tables. Each skill was run from its SKILL.md by a fresh agent following it literally, on identical copies of three artefacts. None of the other skills' authors was involved.

| Skill | Source |
|---|---|
| reviewloop | [tomek7667/reviewloop](https://github.com/tomek7667/reviewloop) |
| loop-review | [gcostudiobusiness-cell/loop-review-skill](https://github.com/gcostudiobusiness-cell/loop-review-skill) |
| claude-review-loop | [yamadashy/skills](https://github.com/yamadashy/skills) |

The artefacts:

- **A.** A small Python rate-limiter with six seeded defects and four frozen behaviours, scored by a 15-case hidden test suite no reviewer saw.
- **B.** The same library with the six defects fixed. This measures corruption and over-editing, the quantity the break-even condition turns on and the one none of the published loops reports. The reruns later showed it still had a few real defects (see below).
- **C.** A 54-line key-rotation runbook with six seeded defects. Frozen: under 80 lines, section order, continuous step numbering. Scored by a cold grader executing it as a strict on-call engineer.

Reviewers were separate `claude -p` processes wherever a skill asked for a fresh reader. Lines changed counts library code and tests together, as a diff against the starting tree.

**A. Defective code**

| Skill | Seeds fixed | Frozen kept | Cold reviewer | Rounds | Lines changed |
|---|---|---|---|---|---|
| hill-climb | 6/6 | 4/4 | yes | 3 (cap) | +476 / -32 |
| reviewloop | 6/6 | 4/4 | yes | 3 (cap) | +546 / -38 |
| loop-review | 4/6 | 4/4 | no* | 1 | +160 / -22 |
| claude-review-loop | 5/6 | 4/4 | no* | 2 | +144 / -26 |

\* The running agent did not find the `claude` CLI and reviewed in-session. This was not a fault of the skill.

**B. Correct code**

| Skill | Frozen kept | Hidden tests | Rounds | Lines changed | Round-1 findings |
|---|---|---|---|---|---|
| hill-climb | 4/4 | 15/15 | 3 (cap) | +249 / -10 | 10 blocking, 8 confirmed by the checker |
| reviewloop | 4/4 | 15/15 | 3 (cap) | +333 / -20 | 13 |
| loop-review | 4/4 | 15/15 | 1 | +300 / -23 | 15 |
| claude-review-loop | 4/4 | 15/15 | 2 | +115 / -11 | 9 |

**C. Runbook**

| Skill | Seeds fixed | Frozen kept | Introduced blockers | Invented facts | Lines |
|---|---|---|---|---|---|
| hill-climb | 6/6 | yes | 0 | 1 | 67 |
| reviewloop | 6/6 | yes | 3 | 4 | 65 |
| loop-review | 6/6 | yes | 1 | 0 | 68 |
| claude-review-loop | 6/6 | yes | 0 | 2 | 73 |

### What the results showed

Finding the seeded defects did not separate the loops; all of them fixed all or nearly all. Two other results did.

On the runbook, the two loops that applied final-round fixes without another review each shipped a broken command. In one, a key read into an unexported shell variable means the rotation can never succeed. In the other, a UTC timestamp is passed to a tool that reads it as local time. hill-climb applies final-round fixes only where a mechanical check covers the edit, and it delivered no introduced blockers. claude-review-loop also delivered none.

On the correct library, every loop changed far more than the library needed, and every reviewer reported blocking defects in it: NaN rates, infinite bursts, boolean coercion, an overflow escaping, a clock read before the lock. Most are real edge cases outside the stated requirements; a few, the reruns showed, are inside them. hill-climb's checker, then a smaller model than the critic, disputed nothing in six rounds. On the defective library, 26 of hill-climb's 37 findings were out-of-scope hardening.

That drove the current version. The checker now runs on the strongest model available and must reproduce a finding, not find it plausible. Every finding gets a scope verdict against numbered requirements. The reduced cap triggers on confirmed in-scope findings rather than the critic's raw tally, which was never zero in twelve runs. Later critics see the previous round's diff. Each fixed finding gets one test, no more. Fixes to executable documents may not assert environment facts the original does not state.

Three ideas came from the other loops. From loop-review: challenging each finding against the code before acting on it, and stopping after one round on a clean artefact. From claude-review-loop: reviewing only changed lines in later rounds. From reviewloop: a numbered acceptance list re-checked on every pass. None of the three has a contract fixed before round one, stopping rules readable from a table, versioned rounds, or an owner's list.

### Rerun with the current version

The current version was run twice on the correct library, each time by a fresh agent following the same brief. Run A used a smaller model for the critic than for the checker; run B used the same model for both.

| Run on the correct library | Frozen kept | Hidden tests | Lines changed | Library code | Tests | Stopped by |
|---|---|---|---|---|---|---|
| previous version | 4/4 | 15/15 | +249 / -10 | +36 / -10 | +213 | cap |
| current version, run A | 4/4 | 15/15 | +70 / -8 | +15 / -8 | +55 | cap, one confirmed finding left for the owner |
| current version, run B | 4/4 | 15/15 | +83 / -6 | +14 / -6 | +69 | rule 1, on the third critic call |

Total lines changed fell by about two thirds. Most of the fall is in tests, where each fixed finding now gets one test; changes to the library code fell from 46 lines to 23 and 20. Both runs fixed the same three things, each tied to a requirement:

- **Requirement 1, thread safety.** `SlidingWindow` now reads the clock inside its lock. The test for this checks the code's structure; it does not show a key admitting more than its limit.
- **Requirement 2, rates below one per second.** `RateLimiter` no longer writes refilled tokens back when it denies a request, which caused drift at fractional rates.
- **Requirement 4, invalid configuration raises `ConfigError`.** `load_config` now rejects a NaN rate or window, an infinite or fractional burst, and unknown keys of mixed types.

Every test the two runs added fails on the original library.

The reruns also showed that the correct library was not quite correct. Unknown keys of mixed types raised `TypeError`, which breaks requirement 4 as written; the previous version fixed that too. Run A's checker reproduced a rounding defect under requirement 2: at a rate of 0.3, a request at exactly t = 10.0 is denied, because elapsed time multiplied by rate comes to 0.9999999999999999. It was found in the final round, so the final-call rule kept it out of the fix batch and put it on the owner's list. Run B did not find it. Whether the NaN, infinite and fractional cases fall under requirement 4 depends on how its list of invalid inputs is read.

### Caveats

- **One run per cell.** Variance was not measured, so a difference of one seed or one blocker is noise. Read the tables as a shape, not a ranking.
- **The current version has two runs.** Both are on the correct library only, with a different critic model in each, so the rerun is a worked example, not a measurement.
- **Corruption is measured only as far as the tests reach.** The hidden tests cover the six seeds and four frozen behaviours. "No corruption" means none they detect.
- **Anthropic models throughout.** Every reviewer and grader was one, and same-family bias applies to all of them.
- **LLM graders.** Where no test applied, the graders were LLMs, and each says where it relied on simulation rather than reproduction.

## Other limits

- **Cost.** A round is at least two agent calls. A code climb that runs to the cap is ten or more.
- **Cold reads need a second context.** Without the Agent tool or the `claude` CLI, every tally is labelled "not cold".
- **Prose is extrapolation.** The quantitative literature is on code, maths and short answers. The rankings for runbooks, pages and proposals follow the same logic but have less evidence behind them.
- **The caps are judgement figures.** The research gives a break-even condition, not a round count.

## Install

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Copy the skill into your repo:

```
cp -r skills/hill-climb/ your-repo/.claude/skills/hill-climb/
```

Then invoke it on a draft:

```
/hill-climb docs/runbook.md
```

It also triggers on requests such as "improve this until it's good", "review and fix", "harden this" or "make it survive review".

## References

1. Tsui, "Self-Correction Bench" (2025). [arXiv:2507.02778](https://arxiv.org/abs/2507.02778)
2. Chen, Su and Chiang, "The Self-Correction Illusion" (2026). [arXiv:2606.05976](https://arxiv.org/abs/2606.05976)
3. Reitich, "Correction and Corruption: A Two-Rate View of Error Flow in LLM Protocols" (2026). [arXiv:2604.18245](https://arxiv.org/abs/2604.18245)
4. Liu and Meng, "Self-Correction as Feedback Control" (2026). [arXiv:2604.22273](https://arxiv.org/abs/2604.22273)
5. McAleese et al., "LLM Critics Help Catch LLM Bugs" (2024). [arXiv:2407.00215](https://arxiv.org/abs/2407.00215)
6. Pombal, Rei and Martins, "Self-Preference Bias in Rubric-Based Evaluation" (2026). [arXiv:2604.06996](https://arxiv.org/abs/2604.06996)
7. Wataoka, Takahashi and Ri, "Self-Preference Bias in LLM-as-a-Judge" (2024). [arXiv:2410.21819](https://arxiv.org/abs/2410.21819)
8. Snell et al., "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters" (2024). [arXiv:2408.03314](https://arxiv.org/abs/2408.03314)
