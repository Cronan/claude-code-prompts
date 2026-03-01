# /artifact

Build interactive single-file HTML artifacts: dashboards, trackers, data visualizations, planners, calculators, or any self-contained UI.

## How it works

The skill produces a single `.html` file that opens directly in any browser. No Node.js, npm, or build step required.

The stack:

- **Alpine.js** -- reactive UI state (tabs, search, filters, sorting) in ~15 KB
- **ECharts** -- interactive charts with zoom, brush, linked tooltips, and a toolbox
- **Tailwind CSS** -- dark theme styling, responsive layout

All three load from CDN. Data is hardcoded in the file and structured for easy editing.

## Install

```
cp -r skills/artifact/ your-repo/.claude/skills/artifact/
```

## Usage

```
/artifact
```

Describe what you want and Claude Code produces an artifact file. The skill also auto-triggers when you ask for dashboards, trackers, charts, tools, widgets, or similar interactive UI.

## Platform targets

Artifacts render on:

- Chromium on Raspberry Pi OS (ARM, 1024x600)
- Firefox and Chrome on desktop Linux
- Safari on macOS
- Chrome/Edge on Windows

Performance guidance covers DOM limits, animation constraints, and dataset sizes for low-powered hardware. ECharts supports SVG rendering for memory-constrained devices.

## Charts

ECharts provides line, bar, area, pie, radar, and scatter charts. Interactive features include:

- DataZoom (slider and scroll-wheel zoom)
- Linked tooltips across multiple charts
- Toolbox (save as image, data view, reset)
- Legend toggle (click to show/hide series)
- Brush selection

Charts use a custom `zinc-dark` theme that matches the Tailwind dark theme tokens. Also supports candlestick, heatmap, treemap, and boxplot charts.

Full specification: [`SKILL.md`](SKILL.md).

## Constraints

- Single file. One page per artifact.
- No external API calls. Data is hardcoded, structured for easy editing.
- No `localStorage` or `sessionStorage`.
- Dark theme by default (`bg-zinc-900` page, `bg-zinc-800` cards, `border-zinc-700`).
- No `<form>` tags. Use `@click` and `x-model` directly.
- No hover-only interactions. Touch devices must work.

## Reference files

| File | Content |
|---|---|
| [`references/patterns.md`](references/patterns.md) | Component skeletons: sidebar, cards, tables, tabs, search, charts, badges, progress bars |
| [`references/tailwind-guide.md`](references/tailwind-guide.md) | Dark theme tokens, ECharts theme config, spacing scale, typography |
| [`examples/example-dashboard.html`](examples/example-dashboard.html) | Complete example: system monitor with linked charts, sortable table, search, filtering, tabs |
