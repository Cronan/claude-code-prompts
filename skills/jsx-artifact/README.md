# /jsx-artifact

Build interactive single-file React artifacts: dashboards, trackers, data visualizations, planners, calculators, or any self-contained UI. Produces a `.jsx` file that renders in a local Vite dev server.

## What it does

Claude Code generates a single `.jsx` file containing a complete React component styled with Tailwind CSS. The file uses standard ES module imports (`import { useState } from "react"`) and exports a default `App` component. A local Vite+React dev server renders the artifact in the browser.

The skill targets cross-platform use. Artifacts render on desktop Linux, Raspberry Pi (Chromium, 1024x600), macOS, and Windows. Performance guidance in the SKILL.md covers DOM limits and animation constraints for low-powered hardware.

## Install

```
cp -r skills/jsx-artifact/ your-repo/.claude/skills/jsx-artifact/
```

## Usage

```
/jsx-artifact
```

Describe what you want and Claude Code produces a `.jsx` file in the artifacts directory. The skill also auto-triggers when you ask for dashboards, trackers, charts, tools, widgets, or similar interactive UI.

## Available libraries

Always available: `react`. Commonly used: `recharts`, `lucide-react`. Also supported if installed: `d3`, `lodash`, `mathjs`, `papaparse`, `xlsx`, `three`, `mammoth`, `chart.js`, `tone`. Only what the artifact needs gets imported.

## Constraints

- Single `.jsx` file. Standard ES module `import` / `export default`.
- No external API calls. Data is hardcoded mock data, structured for easy editing.
- No `localStorage` or `sessionStorage`.
- Dark theme by default (`bg-zinc-900` page, `bg-zinc-800` cards, `border-zinc-700`).
- No `<form>` tags. Use `onClick` and `onChange` directly.

## Reference files

| File | Content |
|---|---|
| [`references/patterns.md`](references/patterns.md) | Component skeletons: sidebar, cards, tables, tabs, search, charts, badges, progress bars |
| [`references/tailwind-guide.md`](references/tailwind-guide.md) | Dark theme tokens, spacing scale, typography, Recharts theming |
| [`examples/example-dashboard.jsx`](examples/example-dashboard.jsx) | Complete working artifact: system monitor with charts, sortable table, search, filtering, and tabs |
