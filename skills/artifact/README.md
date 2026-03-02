# /artifact

Build interactive single-file HTML artifacts: dashboards, trackers, data visualizations, planners, calculators, or any self-contained UI.

**[Browse examples](examples/index.html)** -- open in any browser, no server required.

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

ECharts provides 13 chart types with complete configuration examples:

- **Standard**: line, bar, stacked area, line+bar combo
- **Part-to-whole**: donut/pie, treemap, funnel, sankey
- **Statistical**: scatter/bubble, heatmap, radar, boxplot
- **KPI**: gauge
- **Financial**: candlestick with volume overlay

Interactive features include DataZoom (slider and scroll-wheel zoom), linked tooltips, toolbox (save image, data view, reset), legend toggle, brush selection, markLine thresholds, and markArea regions. Charts can be combined in a single instance (line + bar, candlestick + volume bars, stacked area).

Charts use a custom `zinc-dark` theme that matches the Tailwind dark theme tokens.

## Dashboard features

Beyond charting, artifacts support production-grade dashboard patterns:

- **Cross-filtering** -- click a chart element to filter other charts and tables
- **CSV export** -- download table/chart data with proper quoting and escaping
- **URL hash state** -- filter values and active tab encoded in URL for shareable links
- **Fullscreen panels** -- expand any chart to fill the viewport
- **Keyboard shortcuts** -- number keys for tabs, Escape to reset
- **Skeleton loading** -- pulsing placeholders while CDN scripts load
- **Print stylesheet** -- white background, hidden controls, page-break-safe cards
- **Synced crosshair** -- linked tooltips across charts via `echarts.connect()`
- **Sortable tables** -- keyboard-accessible headers with ARIA sort attributes
- **prefers-reduced-motion** -- respects system accessibility setting
- **prefers-color-scheme** -- detects system dark/light preference

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
| [`references/patterns.md`](references/patterns.md) | Component skeletons: sidebar, cards, tables, tabs, search, charts, badges, progress bars, CSV export, fullscreen panels, skeleton loading, print stylesheet |
| [`references/tailwind-guide.md`](references/tailwind-guide.md) | Dark theme tokens, ECharts theme config, spacing scale, typography |

## Examples

**[Browse all examples](examples/index.html)** or download and open individually in any browser.

| File | Content |
|---|---|
| [`examples/example-chart-showcase.html`](examples/example-chart-showcase.html) | All 13 chart types organized by category (Standard, Part-to-Whole, Statistical, KPI, Financial) with type labels, fullscreen panels, markLine/markArea, keyboard shortcuts |
| [`examples/example-dashboard.html`](examples/example-dashboard.html) | System monitor with cross-filtering, CSV export, URL hash state, sortable table, search, filter chips, skeleton loading, print stylesheet |
| [`examples/example-gdp-analysis.html`](examples/example-gdp-analysis.html) | GDP and labor market analysis: 10 economic sectors, 18 job categories, task-level automation breakdowns. Combines treemap, scatter/bubble, radar, stacked bar, gauge, sortable tables, cross-filtering |
