# /jsx-artifact

Generate self-contained JSX artifacts as single HTML files. No build step, no toolchain, no server. The output opens directly in any browser.

## What it does

When invoked, Claude Code generates an interactive React component styled with Tailwind CSS and rendered in the browser using CDN-loaded libraries and Babel standalone for JSX transformation. The result is one `.html` file you can open with `xdg-open`, `chromium-browser`, or any file manager.

The skill targets constrained environments: headless Linux boxes, Raspberry Pis, machines without Node.js installed. If the device has a browser, the artifact works.

## Install

```
cp -r skills/jsx-artifact/ your-repo/.claude/skills/jsx-artifact/
```

## Usage

```
/jsx-artifact
```

Describe what you want (a dashboard, a data table, an interactive form) and Claude Code produces a single HTML file containing the complete artifact.

## What gets loaded from CDN

Every artifact includes:

- React 18 and ReactDOM (unpkg)
- Babel standalone for in-browser JSX (unpkg)
- Tailwind CSS Play CDN

Optional, loaded only when used:

- Recharts for data visualization
- Lucide React for icons

## Constraints

- Single file. No external assets, no local imports, no build step.
- No external API calls. Data is hardcoded mock data.
- No localStorage or sessionStorage. Stateless across page loads.
- Dark theme by default. Light theme is secondary.
- No TypeScript. Babel standalone handles JSX, not TSX.

## Platform targets

Tested patterns work on:

- Chromium on Raspberry Pi OS (ARM, 1024x600)
- Firefox and Chrome on desktop Linux
- Safari on macOS
- Chrome/Edge on Windows

Performance guidance in the SKILL.md covers DOM node limits, animation constraints, and Recharts dataset sizes appropriate for low-powered hardware.

## Reference files

| File | Content |
|---|---|
| [`references/patterns.md`](references/patterns.md) | Component skeletons: sidebar, cards, tables, tabs, search, charts |
| [`references/tailwind-guide.md`](references/tailwind-guide.md) | Dark theme tokens, spacing scale, typography, Recharts theming |
| [`examples/example-dashboard.html`](examples/example-dashboard.html) | Complete working artifact: system monitor dashboard with charts, tables, search, and filtering |
