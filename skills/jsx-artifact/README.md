# /jsx-artifact

Build interactive single-file React artifacts: dashboards, trackers, data visualizations, planners, calculators, or any self-contained UI.

## Two output modes

The skill detects the environment on first use and picks the right format:

- **Renderer mode** -- When a Vite+React dev server is available. Produces a `.jsx` file with standard ES module imports and `export default`. Cleaner code, full library support.
- **Standalone mode** -- When no renderer is available. Produces a `.html` file with CDN-loaded React, Babel standalone, and Tailwind. Opens directly in any browser. No Node.js, npm, or build step required.

Both modes use the same design tokens, component patterns, and Tailwind classes. The component code inside the file shell is identical.

## Install

```
cp -r skills/jsx-artifact/ your-repo/.claude/skills/jsx-artifact/
```

## Usage

```
/jsx-artifact
```

Describe what you want and Claude Code produces an artifact file. The skill also auto-triggers when you ask for dashboards, trackers, charts, tools, widgets, or similar interactive UI.

## Platform targets

Artifacts render on:

- Chromium on Raspberry Pi OS (ARM, 1024x600)
- Firefox and Chrome on desktop Linux
- Safari on macOS
- Chrome/Edge on Windows

Performance guidance covers DOM limits, animation constraints, and dataset sizes for low-powered hardware.

## Available libraries

Always available: `react`. Commonly used: `recharts`, `lucide-react`. Also supported if installed in the renderer: `d3`, `lodash`, `mathjs`, `papaparse`, `xlsx`, `three`, `mammoth`, `chart.js`, `tone`.

In standalone mode, libraries are loaded from CDN. Only `react`, `recharts`, and `lucide-react` have CDN UMD builds that work reliably.

## Constraints

- Single file. One component per artifact.
- No external API calls. Data is hardcoded, structured for easy editing.
- No `localStorage` or `sessionStorage`.
- Dark theme by default (`bg-zinc-900` page, `bg-zinc-800` cards, `border-zinc-700`).
- No `<form>` tags. Use `onClick` and `onChange` directly.
- No hover-only interactions. Touch devices must work.

## Reference files

| File | Content |
|---|---|
| [`references/patterns.md`](references/patterns.md) | Component skeletons for both modes: sidebar, cards, tables, tabs, search, charts, badges, progress bars |
| [`references/tailwind-guide.md`](references/tailwind-guide.md) | Dark theme tokens, spacing scale, typography, Recharts theming |
| [`examples/example-dashboard.jsx`](examples/example-dashboard.jsx) | Renderer mode example: system monitor with charts, sortable table, search, filtering, tabs |
| [`examples/example-dashboard.html`](examples/example-dashboard.html) | Standalone mode example: same dashboard, opens directly in a browser |
