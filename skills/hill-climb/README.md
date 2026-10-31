# /hill-climb

Improves a finished draft in rounds until a stopping rule agreed in advance fires. The draft can be code, a runbook, an essay, an HTML page, a proposal, a prompt or another skill. Each round is one cold critic read, a check of every finding by a second agent, one batch of fixes, and a new saved version. You get back the last version a critic actually read, a table of what each round found, and a list of everything the climb chose not to fix and why.

## Why it is built this way

Three observations shape the design. The evidence for each is in the [literature review](../../docs/hill-climb-review-2026-10-31.md) and the [benchmark](../../docs/hill-climb-benchmark-2026-10-31.md).

1. **Self-review misses most of what matters.** Models fail to correct their own errors about two thirds of the time, yet fix the identical error when it arrives from outside. The critic must not have seen the work being produced.
2. **Fixes introduce defects.** A revision round improves net quality only when its correction rate exceeds its corruption rate multiplied by baseline/(1 - baseline). At 95% baseline quality the multiplier is 19, so further rounds on a clean artefact tend to do harm. The fixer is handed a list of findings, not the critic's prose, and nothing is delivered that no critic has read.
3. **A critic reports blocking defects in a correct artefact.** In the benchmark, every reviewer, this one included, reported blocking defects in a library that met all of its stated requirements. The edge cases were real; none was in the requirements. The gate that holds is scope: a finding is fixed only if a second agent reproduces it and ties it to a numbered requirement, to frozen behaviour, or to a contract the artefact states about itself. Everything else goes to the owner.

## How it works

1. **Contract.** Before the first round, the skill writes at most eight lines in the conversation: the objective as numbered requirements, the behaviour no fix may change, the mechanical checks (tests, linters, word counts), a one-line scope test, and the stopping rules and cap.
2. **Cold critic.** A fresh context reads the artefact as the person who will have to live with it: the engineer executing the runbook, the reviewer before merge, the committee member. It is reached through the Agent tool, then a fresh `claude -p` process, then, as a last resort, a same-session review labelled "not cold". Where a model choice exists, the critic runs on a different model from the author. Findings are ranked blocking, misleading or minor against a definition specific to the artefact type.
3. **Checker.** A second cold agent on the strongest model available, briefed as the author's advocate. For each finding it returns two verdicts: reproduced or not (a failing test, or the two sentences that contradict), and in scope or not. Plausible is not confirmed.
4. **Fix batch.** Only confirmed, in-scope blocking and misleading findings are fixed, with at most one test per finding. Every round is saved as a new version (`name-vN.md`, or one commit per batch) and never overwrites the last.
5. **Next round.** The next critic reads the new version and the diff from the previous one. Outside the diff it reports only blocking findings, so each round does not regenerate the same list.
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

## Evidence and its limits

The skill was run against three published Claude Code review loops on identical artefacts: a Python library with six seeded defects, the same library with the defects fixed, and a 54-line runbook with six seeded defects. Every loop fixed all or nearly all of the seeded defects, so finding bugs did not separate them. Two other results did. On the runbook, the two loops that applied their final-round fixes without another review each shipped a broken command; hill-climb, whose final-round fixes are limited to what a mechanical check covers, delivered no introduced blockers (claude-review-loop also delivered none). On the correct library, every loop edited code that needed no edits: hill-climb added 249 lines, against a range of 62 to 333 across the four. That result is what led to the scope gate in the current version.

Read these numbers with the caveats in the [benchmark](../../docs/hill-climb-benchmark-2026-10-31.md): one run per cell, Anthropic models throughout, LLM graders where no test applies. The benchmark ran the previous version of the skill. The changes it prompted are in this version, which has not yet been re-benchmarked. The harness, seeded artefacts, hidden tests and every reviewer report are in [`bench/hill-climb/`](../../bench/hill-climb/).

Other limits:

- **Cost.** A round is at least two agent calls. A code climb that runs to the cap is ten or more.
- **Cold reads need a second context.** Without the Agent tool or the `claude` CLI, every tally is labelled "not cold".
- **Same-family bias.** A fresh context removes conversation contamination but not a judge's preference for text from its own model family. Where only one family is available, the skill says so.
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
