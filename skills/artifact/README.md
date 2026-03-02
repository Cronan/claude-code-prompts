# /artifact

Build interactive single-file HTML artifacts: dashboards, trackers, data visualizations, planners, calculators, or any self-contained UI.

**[Browse examples](https://cronyn.co.uk/claude-code-prompts/skills/artifact/examples/)** -- open in any browser, no server required.

## How it works

The skill produces a single `.html` file that opens directly in any browser. No Node.js, npm, or build step required.

The stack:

- **Alpine.js** -- reactive UI state (tabs, search, filters, sorting) in ~15 KB
- **ECharts** -- interactive charts with zoom, brush, linked tooltips, and a toolbox
- **Tailwind CSS** -- dark/light theme styling, responsive layout

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

ECharts provides 20 chart types with complete configuration examples:

- **Standard**: line, bar, stacked area, line+bar combo
- **Part-to-whole**: donut/pie, treemap, funnel, sankey
- **Statistical**: scatter/bubble, heatmap, radar, boxplot
- **KPI**: gauge
- **Financial**: candlestick with volume overlay, waterfall, calendar heatmap
- **Advanced**: sunburst, graph/network, parallel coordinates, themeriver, polar bar

Interactive features include DataZoom (slider and scroll-wheel zoom), linked tooltips, toolbox (save image, data view, reset), legend toggle, brush selection, markLine thresholds, and markArea regions. Charts can be combined in a single instance (line + bar, candlestick + volume bars, stacked area).

Visual features include gradient fills (`LinearGradient`), decal patterns for accessibility, piecewise and continuous `visualMap`, and the `dataset` component with transforms for shared data sources.

Charts use dual ECharts themes (`zinc-dark` and `zinc-light`) that match the Tailwind dark/light theme tokens.

## Dashboard features

Beyond charting, artifacts support production-grade dashboard patterns:

- **Dark/light theme toggle** -- runtime switch with ECharts re-theming and `prefers-color-scheme` detection
- **Color-blind safe palette** -- runtime toggle swapping to a deuteranopia-safe color set
- **Cross-filtering** -- click a chart element to filter other charts and tables
- **CSV export** -- download table/chart data with proper quoting and escaping
- **URL hash state** -- filter values and active tab encoded in URL for shareable links
- **Fullscreen panels** -- expand any chart to fill the viewport
- **Keyboard shortcuts** -- number keys for tabs, Escape to reset
- **Skeleton loading** -- pulsing placeholders while CDN scripts load
- **Print stylesheet** -- white background, hidden controls, page-break-safe cards
- **Synced crosshair** -- linked tooltips across charts via `echarts.connect()`
- **Sparklines** -- tiny inline charts in table cells showing data trends
- **Sortable tables** -- keyboard-accessible headers with ARIA sort attributes
- **Sticky table headers** -- pinned column headers while scrolling long tables
- **Detail panel / drawer** -- slide-in side panel for item detail on row click
- **Multi-select filtering** -- toggle multiple filter values simultaneously
- **Pagination** -- page controls for large tables with configurable page size
- **Toast notifications** -- transient auto-dismissing feedback messages after actions
- **View-as-table toggle** -- swap between chart and data table for accessibility
- **Responsive legend** -- ECharts `media` option for automatic legend repositioning
- **Inline JSON data blocks** -- separate large datasets from chart logic
- **prefers-reduced-motion** -- respects system accessibility setting
- **prefers-color-scheme** -- detects system dark/light preference

Full specification: [`SKILL.md`](SKILL.md).

## Constraints

- Single file. One page per artifact.
- No external API calls. Data is hardcoded, structured for easy editing.
- No `localStorage` or `sessionStorage`.
- Dark theme by default, with light theme toggle available.
- No `<form>` tags. Use `@click` and `x-model` directly.
- No hover-only interactions. Touch devices must work.

## Reference files

| File | Content |
|---|---|
| [`references/patterns.md`](references/patterns.md) | Component skeletons: sidebar, cards, tables, tabs, search, charts, sparklines, badges, progress bars, CSV export, fullscreen panels, skeleton loading, print stylesheet, dark/light toggle, view-as-table toggle, color-blind palette toggle |
| [`references/tailwind-guide.md`](references/tailwind-guide.md) | Dark theme tokens, ECharts theme config, spacing scale, typography |

## Examples

**[Browse all examples](https://cronyn.co.uk/claude-code-prompts/skills/artifact/examples/)** or download and open individually in any browser.

| File | Content |
|---|---|
| [`examples/example-chart-showcase.html`](examples/example-chart-showcase.html) | 20 chart types organized by category (Standard, Part-to-Whole, Statistical, KPI, Financial, Advanced) with sunburst, graph/network, parallel coordinates, themeriver, polar bar, gradient area fill, dark/light toggle, color-blind mode, fullscreen panels, keyboard shortcuts |
| [`examples/example-dashboard.html`](examples/example-dashboard.html) | System monitor with cross-filtering, dark/light toggle, color-blind mode, CSV export, URL hash state, sortable table with sparklines, search, filter chips, skeleton loading, print stylesheet |
| [`examples/example-gdp-analysis.html`](examples/example-gdp-analysis.html) | GDP and labor market analysis: 10 economic sectors, 18 job categories, task-level automation breakdowns. Dark/light toggle, color-blind mode, treemap, scatter/bubble, radar, stacked bar, gauge, sortable tables, cross-filtering |
