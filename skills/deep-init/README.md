# /deep-init

Claude Code's `/init` produces a CLAUDE.md by reading the code. That captures build commands and project structure. It misses everything the team learned the hard way: domain rules from bug fixes, edge cases from ticket post-mortems, design decisions buried in PR reviews.

`/deep-init` mines git history, PR comments, issue tracker tickets, and team wiki pages, then produces a CLAUDE.md grounded in what the team actually learned.

## Before and after

<details>
<summary><strong>/init output</strong> (code-derived)</summary>

```markdown
# MyRepo

## Build and test
Run `pytest` to execute tests. Run `ruff check` for linting.

## Project structure
- src/orders/ -- Order processing modules
- src/inventory/ -- Stock management and allocation

## Coding conventions
- Use type hints for all function signatures
- Follow PEP 8 naming conventions
```

</details>

<details>
<summary><strong>After /deep-init</strong> (history-derived)</summary>

```markdown
# MyRepo
Last audited: 2026-02-19

Order processing and fulfillment engine. Errors here produce incorrect charges
or oversold inventory.

## Domain rules

Stock reservations expire after 30 minutes if payment is not captured.
Never extend the window; it causes overselling during flash sales.

Never query the warehouse API during the nightly inventory sync (02:00-03:30 UTC).
Use the cached snapshot from `InventoryCache.get_snapshot()`.

Discount application runs after stock validation, not before.
Applying discounts to out-of-stock items generates refund obligations
for orders that should have been rejected.

## Build and test

`pytest` runs the full suite. No special flags needed.
Pre-commit hooks enforce ruff and mypy -- do not skip them.

## Coding patterns

Use Arrow-backed DataFrames (`dtype_backend="pyarrow"`), not the default NumPy backend.
See `load_orders` in src/data/loader.py for the canonical pattern.

## References

Before modifying anything in src/orders/, read docs/claude/domain-rules.md.
For business term definitions, see docs/claude/domain-glossary.md.
```

</details>

## How the audit works

**Phase 1 -- Reconnaissance.** A git history subagent scans the log to identify hot files (files with recurring fix commits), revert commits, and ticket IDs.

**Phase 2 -- Domain extraction.** Three subagents run in parallel, focused by Phase 1 output:

- **PR comments**: domain rules from reviewer feedback on merged PRs
- **Issue tracker**: root cause analysis and acceptance criteria from closed tickets
- **Team wiki**: ADRs, glossaries, and runbooks

**Synthesis.** Findings are cross-referenced by ticket ID, deduplicated, tested against a rule ("does this reveal something Claude cannot discover from the code?"), and written as concise instructions.

Prerequisites: a repo with an existing CLAUDE.md from `/init`, and access to your PR platform and issue tracker (via `gh` CLI for GitHub, or MCP servers for other platforms). The git subagent works with any git repository directly.

Full specification: [`SKILL.md`](SKILL.md).

## Install

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Copy the skill into your repo:

```
cp -r skills/deep-init/ your-repo/.claude/skills/deep-init/
```

Then run:

```
/deep-init
```

## Design rationale

### Instruction budget

Research on instruction-following (IFScale, July 2025) found that frontier thinking models follow roughly 150-200 instructions with reasonable consistency. Compliance degrades uniformly as instruction count increases. Claude Code's system prompt already contains approximately 50 instructions, leaving a budget of roughly 100-150 for the CLAUDE.md.

This is why the skill targets under 100 instructions in the root file and uses reference files for detail. It is not an arbitrary limit.

### Progressive disclosure

The Claude Code harness wraps CLAUDE.md content with a system-level instruction telling the model that the context may or may not be relevant and should be ignored if not highly relevant to the current task. This means entries about stock reservation rules may be filtered out when Claude is editing a logging utility in the same repo.

Two consequences: (1) the reference file approach matters because root file entries about a specific subdomain can get filtered during unrelated work; (2) pointers to reference files should be conditional, tied to file paths or code areas, so they appear relevant when Claude works in that area.

### File length

There is no magic line count. Anthropic says "concise" without specifying a number. HumanLayer keeps their root file under 60 lines. The real test: if a developer wouldn't read the whole file in one sitting, it's too long.

### Maintenance

The audit produces the initial file. The `#` key is how it stays alive. When a PR review catches an error, the correction goes into the relevant section via `#` before the PR merges. This is Deming's PDSA cycle encoded in a markdown file: every mistake becomes a rule.
