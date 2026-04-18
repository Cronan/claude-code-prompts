# claude-code-prompts

Skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Each skill is a self-contained specification that Claude Code follows when you invoke it by name. Copy a skill directory into `.claude/skills/` in your repo.

```
cp -r skills/deep-init/ your-repo/.claude/skills/deep-init/
```

## Skills

| Skill | What it does |
|---|---|
| [`/deep-init`](skills/deep-init/) | Mine repo history (PRs, tickets, wiki) to produce a CLAUDE.md grounded in what the team actually learned, not just what the code looks like |
| [`/stet`](skills/stet/) | Strip the 27 patterns that make AI-assisted writing monotonous, vague, and generic -- an editorial tool, not a humanizer |
| [`/artifact`](skills/artifact/) | Build single-file HTML dashboards, trackers, and visualizations with Alpine.js, ECharts, and Tailwind -- opens directly in any browser |
| [`/code-safety-preflight`](skills/code-safety-preflight/) | Triage a repo for hardcoded secrets, credentials in connection strings, sensitive committed files, and unsafe coding patterns -- a stopgap, not a security control |

## Docs

| Document | What it covers |
|---|---|
| [Structured Research with AI](docs/structured-research-with-ai.md) | A complete guide to producing evidence-backed documents using AI -- setup, multi-pass research, reconciliation, fact validation, and final production |

## Contributing

Suggestions welcome via [issues](../../issues). Built by [Cronan](https://github.com/Cronan).

## License

MIT. See [LICENSE](LICENSE).
