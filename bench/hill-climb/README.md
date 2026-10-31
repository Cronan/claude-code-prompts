# hill-climb benchmark harness

Everything needed to re-run the head-to-head of 31 October 2026, and every report it produced. Method, results and caveats: [`docs/hill-climb-benchmark-2026-10-31.md`](../../docs/hill-climb-benchmark-2026-10-31.md).

## Artefacts

| Directory | What it is | Scored by |
|---|---|---|
| `base/` | A small Python rate-limiter with six seeded defects and four frozen behaviours | `hidden/test_hidden.py` |
| `clean/` | The same library with the six defects fixed. Measures corruption and over-editing | `hidden/test_hidden.py`, plus lines changed |
| `prose/` | A 54-line key-rotation runbook with six seeded defects. Seeds are listed in `prose-seeds.md` | Cold grader, `grading-prose.md` |

`hidden/test_hidden.py` has one test per seed (D1 to D6) and one per frozen behaviour (F1 to F4), 15 cases in all. On `base/` 11 fail and 4 pass; on `clean/` all 15 pass. Reviewers never see it.

## Briefs

`BRIEF.md` (batch 1, defective code), `BRIEF2-clean.md` and `BRIEF2-prose.md` (batch 2) are the briefs each contender's agent received. `REPO`, `SKILL` and `OUT` are placeholders for the copy under review, the skill file and the output directory. The concrete brief for each run is in its `*-out/BRIEF.md`.

## Runs

`runs/` holds batch 1 (defective code); `runs2/` holds batch 2 (`clean-*` and `prose-*`). Each contender has two directories:

- `<contender>/`: the final tree or runbook as delivered, with any versioned copies the skill kept.
- `<contender>-out/`: the brief, every reviewer, critic, checker and fix-list report verbatim under `reports/`, and the agent's own `REPORT.md`.

Paths inside briefs and reports are the original absolute paths (`/home/claude/bench/...`).

## Contenders

- `hill-climb`: the version benchmarked is in `skills/hill-climb.md`. The current version, revised in response to these results, is [`skills/hill-climb/SKILL.md`](../../skills/hill-climb/SKILL.md) and has not been re-benchmarked.
- `reviewloop`, `loop-review` and `claude-review-loop`: three published Claude Code review-loop skills, each run from its SKILL.md as fetched on 31 October 2026 by an agent following it literally. Their authors were not involved. Their SKILL.md files are not redistributed here; to re-run them, fetch them from their authors' repositories.

## Re-running

Requires Python 3 and pytest.

1. Copy `base/`, `clean/` or `prose/` to a working directory and make it a git repository with one commit on `master`.
2. Give a fresh agent the matching brief, with `REPO`, `SKILL` and `OUT` filled in.
3. Score code runs with `./score.sh <working-directory>`. It runs the public tests, then the hidden tests, and prints a result per hidden test. Score prose runs with a cold grader given `prose-seeds.md` and the original runbook.

One run per cell was made. Variance across runs was not measured, so treat a difference of one seed or one blocker as noise.
