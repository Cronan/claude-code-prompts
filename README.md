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
| [`/jsx-artifact`](skills/jsx-artifact/) | Build single-file React artifacts (dashboards, trackers, visualizations) styled with Tailwind, rendered in a local Vite dev server |

## Writing

For background on the pattern taxonomy behind `/stet` and why editorial correction differs from detection evasion, see [The 27 ways AI overwrites your voice](docs/ai-writing-patterns.md).

## Contributing

Suggestions welcome via [issues](../../issues). Built by [Cronan](https://github.com/Cronan).

## License

MIT. See [LICENSE](LICENSE).
