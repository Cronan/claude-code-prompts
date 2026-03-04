---
name: artifact
description: |
  Build interactive single-file HTML artifacts: dashboards, trackers, data
  visualizations, planners, calculators, or any self-contained UI. Outputs
  a standalone .html file that opens directly in any browser. Trigger this
  when the user asks for a dashboard, tracker, chart, tool, widget,
  visualizer, planner, monitor, or any interactive UI component.
user-invocable: true
context: fork
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Build an HTML artifact

You build single-file HTML pages. Each artifact is one `.html` file containing a complete interactive UI: data, layout, charts, and behavior in a single place. No build step, no server, no dependencies beyond a browser.

The stack:

- **Alpine.js** for UI state and interactivity (tabs, search, filters, sorting)
- **ECharts** for interactive charts (line, bar, area, pie, radar, scatter, with zoom, brush, linked tooltips)
- **Tailwind CSS** for styling (dark theme, responsive layout)

All three load from CDN. The file opens directly in any browser.

-----

## File shape

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Artifact Title</title>
  <style>[x-cloak] { display: none !important; }</style>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = { darkMode: "class" }</script>
  <!-- Include only if the artifact uses charts: -->
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.6.0/dist/echarts.min.js"></script>
</head>
<body class="bg-zinc-900 text-white min-h-screen">

<script>
document.addEventListener('alpine:init', () => {

  // ── ECharts theme (include only if using charts) ────────
  echarts.registerTheme('zinc-dark', {
    darkMode: true,
    backgroundColor: 'transparent',
    color: ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4'],
    textStyle: { color: '#d4d4d8' },
    title: { textStyle: { color: '#f4f4f5' }, subtextStyle: { color: '#a1a1aa' } },
    legend: { textStyle: { color: '#a1a1aa' } },
    tooltip: {
      backgroundColor: '#27272a',
      borderColor: '#3f3f46',
      textStyle: { color: '#d4d4d8' }
    },
    categoryAxis: {
      axisLine: { lineStyle: { color: '#3f3f46' } },
      axisTick: { lineStyle: { color: '#3f3f46' } },
      axisLabel: { color: '#a1a1aa' },
      splitLine: { lineStyle: { color: '#27272a' } }
    },
    valueAxis: {
      axisLine: { lineStyle: { color: '#3f3f46' } },
      axisTick: { lineStyle: { color: '#3f3f46' } },
      axisLabel: { color: '#a1a1aa' },
      splitLine: { lineStyle: { color: '#27272a' } }
    },
    dataZoom: {
      backgroundColor: '#18181b',
      fillerColor: 'rgba(63, 63, 70, 0.3)',
      borderColor: '#3f3f46',
      handleStyle: { color: '#71717a' },
      textStyle: { color: '#a1a1aa' },
      dataBackground: {
        lineStyle: { color: '#3f3f46' },
        areaStyle: { color: '#27272a' }
      }
    },
    toolbox: { iconStyle: { borderColor: '#a1a1aa' } }
  });

  // ── Data ────────────────────────────────────────────────
  const ITEMS = [
    { id: 1, name: 'Alpha', value: 42 },
    { id: 2, name: 'Beta', value: 87 },
  ];

  // ── Alpine component ───────────────────────────────────
  Alpine.data('app', () => {
    // Chart instances must live outside Alpine's reactive proxy.
    // Alpine v3 wraps data properties in Proxy objects, which breaks
    // ECharts internal state -- treemap drill-down, brushSelection,
    // dispatchAction, and breadcrumb navigation all fail silently
    // when the instance is proxied.
    let charts = {};

    return {
    tab: 'overview',
    search: '',
    items: ITEMS,

    get filtered() {
      return this.items.filter(item =>
        item.name.toLowerCase().includes(this.search.toLowerCase())
      );
    },

    init() {
      this.$nextTick(() => {
        this.initCharts();
        requestAnimationFrame(() => {
          Object.values(charts).forEach(c => c.resize());
        });
      });

      this.$watch('filtered', () => this.updateCharts());

      window.addEventListener('resize', () => {
        Object.values(charts).forEach(c => c.resize());
      });
    },

    initCharts() {
      charts.main = echarts.init(this.$refs.mainChart, 'zinc-dark');
      charts.main.setOption({ /* ... */ });
    },

    updateCharts() {
      charts.main.setOption({
        xAxis: { data: this.filtered.map(d => d.name) },
        series: [{ data: this.filtered.map(d => d.value) }]
      });
    }
  }; });

});
</script>

<div x-cloak x-data="app">
  <div class="max-w-5xl mx-auto p-3 md:p-6">
    <h1 class="text-xl md:text-2xl font-bold mb-6">Title</h1>
    <!-- content -->
  </div>
</div>

<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js"></script>
</body>
</html>
```

Key points:

- The `x-cloak` style in the head prevents flash of unstyled content before Alpine initializes.
- ECharts and Tailwind load synchronously in the head.
- Alpine component registration happens inside an `alpine:init` event listener.
- Data constants are defined above the `Alpine.data()` call, inside the same `alpine:init` block.
- Alpine.js loads last with `defer`.
- No React, no Babel, no JSX. Plain HTML with Alpine directives.

-----

## Script loading order

Order matters. Follow this sequence:

1. **Tailwind CDN** -- in `<head>`
2. **ECharts** -- in `<head>`, only if charts are used
3. **Inline `<script>`** -- in `<body>`, registers `alpine:init` listener, defines data and Alpine components
4. **Alpine.js with `defer`** -- last `<script>` in `<body>`

Do not load scripts the artifact does not use. If there are no charts, omit the ECharts script and theme registration entirely.

-----

## Output location

Save artifacts wherever the user requests. Reasonable defaults:

- The current working directory
- A `./artifacts/` subdirectory
- The user's home directory

Name files with kebab-case: `system-monitor.html`, `recipe-planner.html`.

-----

## Dark theme

Dark theme is the default. Design for dark first.

Background hierarchy:
- Page: `bg-zinc-900`
- Card / panel: `bg-zinc-800`
- Elevated surface: `bg-zinc-700`
- Input / well: `bg-zinc-800/50`

Text hierarchy:
- Primary: `text-white` -- headings, stat values, emphasis
- Body: `text-zinc-300` -- paragraphs, table cells, descriptions
- Labels: `text-zinc-400` -- card labels, column headers, secondary info
- Placeholders: `text-zinc-500` -- input placeholders, disabled text only

Do not use `text-zinc-500` for labels or captions. It fails WCAG AA contrast on `bg-zinc-800` (3.3:1, needs 4.5:1). This is visible on low-quality displays.

Borders: `border-zinc-700`

Accent colors:
- Success / positive: `emerald` -- `bg-emerald-900/30 text-emerald-400`
- Error / negative: `red` -- `bg-red-900/30 text-red-400`
- Warning: `amber` -- `bg-amber-900/30 text-amber-400`
- Primary action: `blue` -- `bg-blue-600 hover:bg-blue-500 text-white`
- Info / cool: `cyan` -- `bg-cyan-900/30 text-cyan-400`

Use gentle opacity backgrounds (`bg-emerald-900/30`) for status badges and category indicators. Full-strength backgrounds (`bg-blue-600`) for primary action buttons only.

### Color-blind accessibility

Approximately 8% of males have red-green color deficiency. Never rely solely on the emerald/red distinction to convey meaning. Always pair color with a redundant signal:

- **Trend indicators**: Use directional text (`+12%` / `-3%`) or arrows alongside color. The `+`/`-` prefix is the primary signal; color reinforces it.
- **Status badges**: Include the status text (`active`, `error`) inside the badge. The text is the primary signal; color reinforces it.
- **Chart series**: When contrasting positive vs. negative in charts, use different line styles (solid vs. dashed) or marker shapes in addition to color. ECharts supports `lineStyle: { type: 'dashed' }` and `symbol: 'triangle'` per series.

For color-blind-safe chart palettes, replace the default theme `color` array:

```js
// Deuteranopia-safe palette (avoids red-green confusion)
color: ['#3b82f6', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']
// Blue, amber, violet, cyan, pink, lime -- all distinguishable

// Protanopia-safe palette
color: ['#3b82f6', '#f59e0b', '#8b5cf6', '#06b6d4', '#f97316', '#14b8a6']
```

When building dashboards for users who may have color vision deficiency, use the deuteranopia-safe palette and confirm that all data distinctions are also encoded in text, shape, or pattern.

## Light theme

When the user requests a light theme, use these tokens instead.

Background hierarchy:
- Page: `bg-zinc-50`
- Card / panel: `bg-white`
- Elevated surface: `bg-white shadow-sm` (shadow distinguishes elevated from card)
- Input / well: `bg-zinc-100`

Text hierarchy:
- Primary: `text-zinc-900` -- headings, values
- Body: `text-zinc-700` -- paragraphs, table cells
- Labels: `text-zinc-500` -- card labels, column headers
- Placeholders: `text-zinc-400` -- input placeholders

Borders: `border-zinc-200`

Accent colors remain the same base hues, adjusted for light backgrounds:
- Success: `bg-emerald-50 text-emerald-700 border-emerald-200`
- Error: `bg-red-50 text-red-700 border-red-200`
- Warning: `bg-amber-50 text-amber-700 border-amber-200`
- Primary: `bg-blue-600 hover:bg-blue-700 text-white`
- Info: `bg-cyan-50 text-cyan-700 border-cyan-200`

Light theme page shell:

```html
<body class="bg-zinc-50 text-zinc-900 min-h-screen">
```

Light theme ECharts: register a `zinc-light` theme variant with matching tokens, or use `echarts.init(el)` without a theme argument (ECharts defaults to a light palette).

### Dark/light mode toggle

When the user requests a theme toggle, use Alpine state and Tailwind's `dark:` variant:

```html
<html lang="en" :class="darkMode ? 'dark' : ''">
```

```js
Alpine.data('app', () => {
  let charts = {};
  return {
  darkMode: true,
  // ...
  toggleTheme() {
    this.darkMode = !this.darkMode;
    // Re-initialize charts with the appropriate theme
    Object.values(charts).forEach(c => c.dispose());
    charts = {};
    this.$nextTick(() => this.initCharts());
  }
}; });
```

Configure Tailwind for class-based dark mode (already in the standard config):

```js
tailwind.config = { darkMode: "class" }
```

Then use Tailwind's `dark:` prefix throughout the HTML:

```html
<body class="bg-zinc-50 dark:bg-zinc-900 text-zinc-900 dark:text-white min-h-screen">
<div class="bg-white dark:bg-zinc-800 rounded-xl p-4 border border-zinc-200 dark:border-zinc-700">
```

Register both ECharts themes and select based on mode:

```js
const theme = this.darkMode ? 'zinc-dark' : null;  // null = ECharts light default
charts.main = echarts.init(this.$refs.mainChart, theme);
```

For the toggle button:

```html
<button @click="toggleTheme()" class="p-2 rounded-lg text-zinc-400 hover:text-zinc-200">
  <svg x-show="darkMode" class="w-5 h-5" ...><!-- sun icon --></svg>
  <svg x-show="!darkMode" class="w-5 h-5" ...><!-- moon icon --></svg>
</button>
```

This approach requires duplicating token classes with `dark:` prefixes, which increases HTML verbosity. Only add a toggle when the user requests it; default to dark-only for simpler artifacts.

-----

## Layout

Standard page shell:

```html
<div class="max-w-5xl mx-auto p-3 md:p-6">
  <h1 class="text-xl md:text-2xl font-bold mb-6">Title</h1>
  <!-- content -->
</div>
```

Use `max-w-5xl` as the default content width. For data-dense dashboards, use `max-w-7xl`. Use `p-3 md:p-6` for mobile-first padding. See the Responsiveness section for guidance on wider layouts.

Grid patterns:
- Stats row: `grid grid-cols-2 md:grid-cols-4 gap-3`
- Two-column: `grid grid-cols-1 md:grid-cols-2 gap-4`
- Three-column: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
- Four-column (large displays): `grid grid-cols-2 md:grid-cols-4 xl:grid-cols-4 gap-3`

-----

## Cards

```html
<div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
  <h3 class="text-sm text-zinc-400 mb-1">Label</h3>
  <p class="text-2xl font-bold">Value</p>
</div>
```

For stat cards showing trends:

```html
<p class="text-emerald-400 font-medium">+12%</p>
<p class="text-red-400 font-medium">-3%</p>
```

## Tabs

Use pill-style tabs inside a container with ARIA tab roles:

```html
<div role="tablist" class="flex gap-1 bg-zinc-800 rounded-lg p-1">
  <template x-for="t in tabs" :key="t">
    <button role="tab"
            :aria-selected="tab === t"
            :aria-controls="'panel-' + t.toLowerCase()"
            @click="tab = t"
            :class="tab === t
              ? 'bg-zinc-700 text-white'
              : 'text-zinc-400 hover:text-zinc-200'"
            class="px-4 py-2 rounded-md text-sm font-medium transition-colors"
            x-text="t"></button>
  </template>
</div>
```

Show tab content with `x-show` and `role="tabpanel"`:

```html
<div role="tabpanel" id="panel-overview" x-show="tab === 'overview'">...</div>
<div role="tabpanel" id="panel-details" x-show="tab === 'details'">...</div>
```

## Tables

Wrap in `overflow-x-auto` for small screens. Use `<template x-for>` for rows:

```html
<div class="overflow-x-auto">
  <table class="w-full text-sm text-left">
    <thead>
      <tr class="border-b border-zinc-700 text-zinc-400">
        <th class="px-4 py-3 font-medium">Name</th>
        <th class="px-4 py-3 font-medium">Status</th>
      </tr>
    </thead>
    <tbody>
      <template x-for="row in filtered" :key="row.id">
        <tr class="border-b border-zinc-700/50 hover:bg-zinc-800/50">
          <td class="px-4 py-3 text-zinc-300" x-text="row.name"></td>
          <td class="px-4 py-3 text-zinc-300" x-text="row.status"></td>
        </tr>
      </template>
    </tbody>
  </table>
</div>
```

Important: `<template x-for>` must be inside `<tbody>`, not `<table>` directly. Browsers enforce HTML nesting rules and may hoist `<template>` elements out of tables otherwise.

-----

## ECharts

### Initialization

Initialize charts in the Alpine `init()` method using `$refs`. Store chart instances in a closure variable (`let charts = {}`), not as a property on the Alpine data object. Alpine v3 wraps data properties in Proxy objects, which breaks ECharts internal state management -- treemap drill-down, breadcrumb navigation, brushSelection, and dispatchAction all fail silently when the instance is proxied.

Wrap the init calls in `$nextTick` so the DOM has settled after Alpine removes `x-cloak` -- without this, `echarts.init()` can run on a zero-size container and charts render blank on first load (especially on mobile):

```js
init() {
  this.$nextTick(() => {
    this.initCharts();
    // One extra resize after the first paint to catch any remaining
    // layout shifts (mobile orientation, late font load, etc.)
    requestAnimationFrame(() => {
      Object.values(charts).forEach(c => c.resize());
    });
  });

  window.addEventListener('resize', () => {
    Object.values(charts).forEach(c => c.resize());
  });
},

initCharts() {
  charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
  charts.cpu.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series: [{ name: 'CPU', type: 'line', data: values, areaStyle: { opacity: 0.2 } }]
  });
}
```

The `charts` variable is declared as `let charts = {}` inside the `Alpine.data()` factory function but outside the returned object (the revealing module pattern). See the scaffold at the top of this document for the full structure.

Extracting chart setup into a separate `initCharts()` method makes it reusable for theme toggles, which need to dispose and reinit all charts from scratch.

Chart container in the HTML:

```html
<div x-ref="cpuChart" class="h-64 w-full"></div>
```

### Charts inside hidden tabs

ECharts cannot initialize on a zero-size container. When a chart is inside an `x-show="false"` panel, it has no dimensions on page load. Two solutions:

**Option A: Initialize all charts on load, resize when tab activates.**

```js
init() {
  // Initialize even for hidden tabs
  charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
  charts.cpu.setOption({ /* ... */ });

  this.$watch('tab', () => {
    this.$nextTick(() => {
      Object.values(charts).forEach(c => c.resize());
    });
  });
}
```

Use `x-show` (not `x-if`) for tab panels so the DOM elements exist at init time. `x-show` only toggles `display: none`; the elements remain in the DOM.

**Option B: Lazy initialization on first tab activation.**

```js
init() {
  this.$watch('tab', (val) => {
    if (val === 'charts' && !charts.cpu) {
      this.$nextTick(() => {
        charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
        charts.cpu.setOption({ /* ... */ });
      });
    }
  });
}
```

Option A is simpler and recommended for most artifacts.

### Choosing visualizations

Before picking a chart type, identify what the user's data answers. The analytical question determines the chart family; the data shape narrows the specific type.

**Question type to chart family:**

| Analytical question | Chart family | Typical types |
|---|---|---|
| How does X change over time? | Trend | Line, area, stacked area, candlestick, themeRiver |
| How does X compare to Y? | Comparison | Bar (grouped), lollipop, bullet, radar, parallel coordinates |
| What are the parts of the whole? | Composition | Pie/donut (5-6 categories max), treemap, sunburst, stacked bar, waterfall |
| How is X distributed? | Distribution | Boxplot, scatter, heatmap, histogram (custom bar) |
| How are X and Y related? | Relationship | Scatter, bubble (scatter + symbolSize), heatmap (correlation matrix) |
| Where does X flow? | Flow | Sankey, funnel |
| What is the current value of X? | Status | Gauge, stat card, bullet chart, progress bar |
| How does X break down by category over time? | Composition + Trend | Stacked area, themeRiver, small multiples |
| How do items rank? | Ranking | Horizontal bar, lollipop, sorted table |

**Data shape routing:**

- **Time series + 1-3 series**: line or area chart. Use stacked area if parts of a whole.
- **Time series + 4+ series**: small multiples (one mini-chart per series). Overlapping lines become unreadable past 4.
- **Categories + values**: bar chart (vertical for <8 categories, horizontal for more). Lollipop for ranked lists where exact values matter.
- **Categories + values summing to whole**: pie/donut (5-6 categories max), treemap (7+), or stacked bar.
- **Hierarchical data**: treemap (flat comparison of leaf sizes), sunburst (emphasis on nesting depth).
- **Two continuous variables**: scatter. Add third variable via bubble size. Add fourth via color.
- **Matrix of values (x-category, y-category, value)**: heatmap.
- **Source-to-target flows**: sankey.
- **Sequential stages with dropoff**: funnel.
- **Cyclical categories (months, hours, weekdays)**: polar bar.
- **Multi-dimensional comparison (4-8 dimensions)**: radar (2-3 items) or parallel coordinates (many items).
- **Single KPI value**: stat card for text, gauge for visual, bullet chart for value-vs-target.

**When not to chart:**

- Fewer than 4 data points: use a stat card or formatted table. Charts with 2-3 bars are wasteful.
- Exact values matter more than visual patterns: use a sortable table with optional sparklines.
- User will export the data: lead with a table and CSV export; add charts as supplementary.

For deeper guidance on dashboard composition patterns and analytical rationale, see `references/chart-selection.md`.

### Chart types

| Type | `series.type` | Notes |
|---|---|---|
| Line | `'line'` | Add `smooth: true` for curved lines. Caution: smoothing invents intermediate values and misrepresents volatile data (sharp drops, spikes). Use only for trends, not precise data. |
| Bar | `'bar'` | Add `barWidth: '50%'` to control width. For stacked: add `stack: 'total'` to each series. For grouped: omit `stack` and ECharts groups automatically. Always start bar chart Y-axes at 0 -- a non-zero baseline exaggerates differences. |
| Area | `'line'` | Add `areaStyle: { opacity: 0.3 }` to a line series |
| Pie | `'pie'` | No axes. Data is `[{ name, value }]`. Use `radius: ['40%', '70%']` for donut. Limit to 5-6 slices; use a horizontal bar chart for more categories. |
| Radar | `'radar'` | Needs a `radar` component with `indicator` array instead of axes |
| Scatter | `'scatter'` | Data is `[[x, y], ...]` pairs. Both axes are `type: 'value'`. For bubble charts, map a third dimension to `symbolSize`. |
| Candlestick | `'candlestick'` | Data is `[[open, close, low, high], ...]`. Requires `type: 'category'` or `type: 'time'` x-axis. Standard for OHLC financial data. |
| Heatmap | `'heatmap'` | Data is `[[x, y, value], ...]`. Requires a `visualMap` component for color mapping. Use for correlation matrices, calendar heatmaps, time-of-day activity patterns. |
| Treemap | `'treemap'` | Data is `[{ name, value, children: [...] }]`. No axes. Use for hierarchical part-to-whole: portfolio allocation, budget breakdowns, file size maps. |
| Boxplot | `'boxplot'` | Data is `[[min, Q1, median, Q3, max], ...]`. Use for distribution comparisons, outlier detection, volatility analysis. |
| Gauge | `'gauge'` | Single-value display. Data is `[{ value: 72, name: 'Score' }]`. No axes. Use for KPIs, health scores, completion percentage. |
| Funnel | `'funnel'` | Data is `[{ name, value }]` in descending order. No axes. Use for conversion funnels, sales pipelines, process stages. |
| Sankey | `'sankey'` | Data is `{ nodes: [...], links: [{ source, target, value }] }`. No axes. Use for flow visualization: budget allocation, traffic sources, energy flow. |
| Waterfall | `'bar'` | Simulated using stacked bars with a transparent base. Data is `[{ name, value }]` with computed running total. Use for financial statements, variance analysis, bridge charts. |
| Calendar heatmap | `'heatmap'` + `calendar` | Uses ECharts `calendar` component. Data is `[[date, value], ...]`. Use for activity tracking, contribution graphs, daily patterns over months. |
| Sunburst | `'sunburst'` | Data is `[{ name, value, children: [...] }]`. No axes. Like treemap but radial; emphasizes hierarchy depth. Click a sector to drill in, click center to zoom out. Use for nested breakdowns: org structures, file system usage, cost allocation by department/team/project. |
| Graph/Network | `'graph'` | Data is `{ nodes: [{ name, ... }], links: [{ source, target, ... }] }`. No axes. Use `layout: 'force'` for auto-positioned nodes or `layout: 'circular'` for ring layout. Use for dependency maps, architecture diagrams, social networks, knowledge graphs. |
| Parallel coordinates | `'parallel'` | Each dimension is a vertical axis; each data point is a polyline crossing all axes. Requires a `parallelAxis` array and `parallel` component instead of standard axes. Use for multi-criteria comparison: server benchmarks, product specs, dataset exploration. |
| ThemeRiver | `'themeRiver'` | Data is `[[date, value, categoryName], ...]`. Uses a `singleAxis` with `type: 'time'` and ISO date strings. A centered streamgraph showing how category volumes evolve over time. Use for topic trends, content category shifts, technology adoption over time. |
| Polar bar | `'bar'` + `polar` | Uses ECharts `polar`, `radiusAxis`, and `angleAxis` components. A Nightingale rose chart: bars arranged radially. Use for cyclical data patterns: monthly revenue, hourly traffic, seasonal comparisons, wind direction frequencies. |
| Custom | `'custom'` | Fully custom rendering via a `renderItem` callback. Each data point returns a graphic element (rect, circle, line, group, etc.). Use for chart types ECharts does not have natively: bullet charts, range bars, dumbbell charts. |
| Bullet | `'custom'` | Horizontal bar with qualitative range bands and a target marker. Data is `[actual, target, poor, satisfactory, good]`. Use for KPI vs target: revenue vs quota, response time vs SLA, utilization vs capacity. |
| Lollipop | `'bar'` + `'scatter'` | Dot on a stem -- a bar chart with less ink. Overlay a thin `bar` (barWidth: 2) for stems and a `scatter` for dots on a shared category axis. Data is a plain values array. Use for ranked lists, survey results, benchmark comparisons where the exact value matters more than the bar area. |
| Small multiples | multiple instances | Grid of identical mini-charts, one per category. Use ECharts `grid` array with one x/y axis pair per cell, or multiple ECharts instances in a CSS grid. Use for per-service metrics, per-region trends, cohort comparisons. |

For complete option objects for chart types beyond line/bar/area/pie/scatter, see `references/chart-examples.md`.

### Combining chart types

A single ECharts instance can render multiple series types. Common combinations:

- **Line + Bar**: overlay a trend line on a bar chart. Both share the same x-axis but may use different y-axes (see dual-axis charts).
- **Candlestick + Bar**: price chart with volume bars underneath (see candlestick example above).
- **Line + Scatter**: trend line with outlier points highlighted as scatter markers.
- **Stacked area**: multiple `type: 'line'` series with `areaStyle` and `stack: 'total'`.

```js
// Line overlaid on bar chart
series: [
  { name: 'Revenue', type: 'bar', data: revenueData },
  { name: 'Growth %', type: 'line', data: growthData, yAxisIndex: 1 }
]
```

When mixing types, ensure the tooltip `trigger` handles both. Use `trigger: 'axis'` for charts sharing a category axis. For mixed axis types, use `trigger: 'item'` on the scatter/pie series.

### Interactive features

Add these to the chart option for rich interactivity:

**Tooltip** -- shows data on hover/tap:

```js
tooltip: {
  trigger: 'axis',
  axisPointer: { type: 'cross' }
}
```

**DataZoom** -- slider and scroll-wheel zoom:

```js
dataZoom: [
  { type: 'slider', start: 0, end: 100, height: 20 },
  { type: 'inside' }
]
```

**Toolbox** -- save image, data view, reset zoom:

```js
toolbox: {
  feature: {
    saveAsImage: { pixelRatio: 2 },
    dataView: { readOnly: false },
    restore: {},
    dataZoom: { yAxisIndex: 'none' }
  }
}
```

**Legend** -- click to toggle series visibility:

```js
legend: {
  data: ['CPU', 'Memory'],
  textStyle: { color: '#a1a1aa' }
}
```

**Brush** -- rectangle or polygon selection for filtering:

```js
brush: {
  toolbox: ['rect', 'polygon', 'clear'],
  xAxisIndex: 0
},
toolbox: {
  feature: {
    brush: { type: ['rect', 'polygon', 'clear'] }
  }
}
```

Wire the selection to Alpine state:

```js
charts.scatter.on('brushSelected', (params) => {
  const selected = params.batch[0]?.selected[0]?.dataIndex || [];
  this.brushedItems = selected.map(i => this.items[i]);
});
```

Use brush on scatter, bar, and line charts for interactive data selection. The toolbox brush buttons let users switch between rectangle and polygon selection modes. Call `chart.dispatchAction({ type: 'brush', areas: [] })` to clear the selection programmatically.

**VisualMap (piecewise)** -- categorical color mapping for discrete ranges:

```js
visualMap: {
  type: 'piecewise',
  pieces: [
    { min: 0, max: 30, label: 'Low', color: '#10b981' },
    { min: 30, max: 70, label: 'Medium', color: '#f59e0b' },
    { min: 70, max: 100, label: 'High', color: '#ef4444' }
  ],
  orient: 'horizontal',
  left: 'center',
  bottom: 10,
  textStyle: { color: '#a1a1aa' }
}
```

Use piecewise visualMap for risk levels, status categories, or any discrete classification. The continuous `visualMap` (documented in the heatmap example) maps a numeric range to a gradient; piecewise maps ranges to distinct colors with labels.

### Linking charts

Synchronize tooltip position, legend toggles, and zoom range across charts:

```js
echarts.connect([charts.cpu, charts.memory, charts.network]);
```

Connected charts show linked crosshairs on hover -- move over one chart and see the corresponding position on all others. Only connect charts that share compatible axis types and data ranges. Connecting a time-series line chart to a categorical bar chart produces confusing crosshair behavior.

### Reactive data updates

When Alpine state changes (search, filter, tab), update charts with `setOption`. ECharts diffs and animates the transition:

```js
this.$watch('filtered', () => {
  charts.main.setOption({
    xAxis: { data: this.filtered.map(d => d.name) },
    series: [{ data: this.filtered.map(d => d.value) }]
  });
});
```

`setOption` merges by default. Pass only the parts that changed. When the number of series changes, use `{ replaceMerge: ['series'] }` as the second argument.

### Time axis

For time-series data, use `type: 'time'` instead of `type: 'category'`. ECharts handles irregular intervals, gap detection, and intelligent label formatting automatically:

```js
xAxis: {
  type: 'time',
  axisLabel: {
    formatter: (val) => new Date(val).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric'
    })
  }
},
series: [{
  type: 'line',
  data: [
    ['2024-01-15', 42],
    ['2024-01-22', 58],  // irregular interval is handled correctly
    ['2024-02-01', 35],
  ]
}]
```

ECharts accepts ISO 8601 strings or Unix milliseconds for time data. Do not use `type: 'category'` with string labels for time data -- it spaces all points equally regardless of actual time gaps, which distorts the visual representation.

For missing data points (weekends, holidays, halted trading), use `null` in the data array to show a gap, or set `connectNulls: true` on the series to draw through gaps.

### Number and axis formatting

Format axis labels and tooltips for readability. Raw numbers without separators or units are unacceptable in data dashboards.

```js
// Currency axis
yAxis: {
  type: 'value',
  axisLabel: {
    formatter: (val) => '$' + (Math.abs(val) >= 1e6
      ? (val / 1e6).toFixed(1) + 'M'
      : Math.abs(val) >= 1e3
      ? (val / 1e3).toFixed(0) + 'K'
      : val.toFixed(0))
  }
}

// Percentage axis
yAxis: {
  type: 'value',
  axisLabel: { formatter: '{value}%' }
}
```

Define reusable formatting utilities at the top of the data section:

```js
const fmt = {
  currency: (v, d = 0) => '$' + Math.abs(v).toLocaleString('en-US', {
    minimumFractionDigits: d, maximumFractionDigits: d
  }),
  pct: (v, d = 1) => v.toFixed(d) + '%',
  num: (v) => v.toLocaleString('en-US'),
  compact: (v) => {
    if (Math.abs(v) >= 1e9) return '$' + (v / 1e9).toFixed(1) + 'B';
    if (Math.abs(v) >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M';
    if (Math.abs(v) >= 1e3) return '$' + (v / 1e3).toFixed(0) + 'K';
    return '$' + v.toFixed(0);
  }
};
```

### Tooltip formatting

Format tooltips with value formatters for readable data:

```js
tooltip: {
  trigger: 'axis',
  axisPointer: { type: 'cross' },
  confine: true,  // prevents overflow on edge-of-viewport charts
  valueFormatter: (val) => fmt.currency(val, 2)
}
```

For multi-series tooltips where each series has different units, use a `formatter` function:

```js
tooltip: {
  trigger: 'axis',
  confine: true,
  formatter: (params) => {
    let html = params[0].axisValueLabel + '<br/>';
    params.forEach(p => {
      const val = p.seriesName === 'Revenue' ? fmt.currency(p.value)
                : p.seriesName === 'Growth' ? fmt.pct(p.value)
                : fmt.num(p.value);
      html += p.marker + ' ' + p.seriesName + ': ' + val + '<br/>';
    });
    return html;
  }
}
```

### Reference lines and thresholds

Use `markLine` for horizontal reference lines (targets, benchmarks, limits):

```js
series: [{
  type: 'line',
  data: values,
  markLine: {
    data: [
      { yAxis: 100000, name: 'Target' },
      { yAxis: 50000, name: 'Minimum', lineStyle: { type: 'dashed', color: '#ef4444' } }
    ],
    lineStyle: { type: 'dashed', color: '#f59e0b' },
    label: { color: '#a1a1aa' }
  }
}]
```

Use `markArea` for shaded regions (normal ranges, danger zones):

```js
markArea: {
  data: [[{ yAxis: 80 }, { yAxis: 100 }]],
  itemStyle: { color: 'rgba(239, 68, 68, 0.1)' },
  label: { show: false }
}
```

### Dual-axis charts

Use dual axes only when two metrics have fundamentally different units (price and volume, temperature and humidity). Never use them for metrics with the same unit.

```js
yAxis: [
  { type: 'value', name: 'Price ($)', axisLabel: { formatter: '${value}' } },
  { type: 'value', name: 'Volume', axisLabel: { formatter: (v) => fmt.compact(v) } }
],
series: [
  { name: 'Price', type: 'line', data: prices, yAxisIndex: 0 },
  { name: 'Volume', type: 'bar', data: volumes, yAxisIndex: 1 }
]
```

Warning: dual-axis scales are arbitrary. You can make any two series appear correlated or uncorrelated by adjusting scales. Use sparingly and only when the alternative (two separate charts) is worse.

### Chart interaction (drill-down)

Wire ECharts click events to Alpine state for drill-down patterns:

```js
init() {
  charts.main = echarts.init(this.$refs.mainChart, 'zinc-dark');
  charts.main.setOption({ /* ... */ });
  charts.main.on('click', (params) => {
    this.selectedItem = params.name;  // updates Alpine state
  });
}
```

### Chart line colors

The zinc-dark theme uses Tailwind 500-level hex values:
- emerald: `#10b981`
- blue: `#3b82f6`
- violet: `#8b5cf6`
- amber: `#f59e0b`
- red: `#ef4444`
- cyan: `#06b6d4`

For gradient fills, decal patterns, dataset transforms, and sparklines, see `references/chart-examples.md`.

-----

## Alpine.js patterns

### State management

All UI state lives in the `x-data` object. Define properties for tabs, search queries, sort keys, expanded sections, and selected items. Chart instances go in a closure variable, not on the data object (see the ECharts initialization section):

```js
Alpine.data('app', () => {
  let charts = {};
  return {
  tab: 'overview',
  search: '',
  sortKey: 'name',
  sortDir: 'asc',
  items: ITEMS,
  // ...
}; });
```

### Computed values (getters)

Use JavaScript getters for derived data. Alpine tracks dependencies automatically:

```js
get filtered() {
  return this.items.filter(item =>
    item.name.toLowerCase().includes(this.search.toLowerCase())
  );
},

get sorted() {
  return [...this.filtered].sort((a, b) => {
    const cmp = a[this.sortKey] > b[this.sortKey] ? 1 : -1;
    return this.sortDir === 'asc' ? cmp : -cmp;
  });
}
```

Inside getters and methods, use `this.` to reference sibling properties. In HTML directive expressions (`@click`, `x-text`), `this` is not needed -- Alpine resolves scope automatically.

Getters re-execute on every access (not cached like Vue computed). For dashboard-scale data (hundreds of rows) this is fine. For thousands of items, debounce the input instead.

### Iteration

Use `<template x-for>` to loop. The template must contain exactly one root element:

```html
<template x-for="item in sorted" :key="item.id">
  <div class="p-4 border-b border-zinc-700/50">
    <span x-text="item.name"></span>
  </div>
</template>
```

### Conditional visibility

Use `x-show` for show/hide. Prefer `x-show` over `x-if` because `x-show` keeps elements in the DOM (needed for ECharts containers):

```html
<div x-show="tab === 'overview'">Overview content</div>
<div x-show="tab === 'charts'" x-transition>Charts content</div>
```

Add `x-transition` for a fade/scale animation on show/hide.

### Two-way binding

Use `x-model` for inputs:

```html
<input type="text" x-model="search"
       class="w-full pl-10 pr-4 py-2 bg-zinc-800/50 border border-zinc-700 rounded-lg text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500"
       placeholder="Search...">
```

### Sorting

Toggle sort direction on header click. Add keyboard access and `aria-sort`:

```html
<th @click="toggleSort('name')" @keydown.enter="toggleSort('name')"
    tabindex="0"
    :aria-sort="sortKey === 'name' ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'"
    class="px-4 py-3 font-medium cursor-pointer hover:text-zinc-200">
  Name
</th>
```

Define the method in the Alpine component:

```js
toggleSort(key) {
  if (this.sortKey === key) {
    this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    this.sortKey = key;
    this.sortDir = 'asc';
  }
}
```

-----

## Tailwind CDN safelist

Tailwind's Play CDN generates styles at runtime by scanning the HTML for class names. Dynamically constructed class names that never appear as complete strings will be missed. If you build class names from variables, include the full strings somewhere the CDN can find them:

```html
<!-- Tailwind CDN safelist:
  bg-emerald-900/30 text-emerald-400
  bg-red-900/30 text-red-400
  bg-amber-900/30 text-amber-400
  bg-zinc-700 text-zinc-300
-->
```

Place this as an HTML comment anywhere in the body.

-----

## Icons

Do not use icon libraries that require React or a build step. For icons in artifacts, use one of:

1. **Inline SVG** -- copy the SVG markup directly. Keeps the file self-contained.
2. **Unicode characters** -- arrows, check marks, and common symbols. Zero overhead.
3. **Lucide static SVG** -- use SVG markup from the Lucide icon set, but inline it rather than importing a package.

Keep icon usage minimal. Most dashboard UIs work well with just arrows, chevrons, search, and close icons.

-----

## Data

All data is hardcoded at the top of the `alpine:init` script block. Make it realistic and internally consistent. Structure it so the user can easily find and replace values:

```js
// ── Data ────────────────────────────────────────────────
// Edit these arrays to change what the dashboard displays.

const SENSORS = [
  { id: 'temp-1', label: 'Living Room', value: 21.3, unit: 'C' },
  { id: 'temp-2', label: 'Garage', value: 14.8, unit: 'C' },
];
```

Do not fetch from external APIs. Do not use `localStorage` or `sessionStorage`. Session state (tab selection, search query, expanded panels) is fine in Alpine's reactive data.

### Inline JSON data blocks

For artifacts with large datasets, separate data from logic using `<script type="application/json">`. This keeps data editable without scrolling through chart configuration:

```html
<script type="application/json" id="sector-data">
[
  { "name": "Manufacturing", "gdp": 2890, "growth": 2.1, "employment": 12.8 },
  { "name": "Finance", "gdp": 2340, "growth": 2.8, "employment": 6.7 }
]
</script>
```

Read it in the `alpine:init` block:

```js
document.addEventListener('alpine:init', () => {
  const SECTORS = JSON.parse(document.getElementById('sector-data').textContent);
  // ... use SECTORS in Alpine.data()
});
```

This pattern is optional. For small datasets (under ~50 items), inline `const` declarations are simpler. Use JSON blocks when the data exceeds ~100 lines and would obscure the component logic.

-----

## What not to do

- No external API calls or `fetch`.
- No `localStorage` or `sessionStorage`.
- No external image URLs. Use inline SVGs or CSS-only graphics.
- No hover-only interactions without a tap/click alternative.
- No `<form>` tags. Use `@click` and `x-model` directly.
- No React, no JSX, no Babel.
- No `import` or `export` statements. Everything loads from CDN.
- No TypeScript.
- Do not load CDN scripts the artifact does not use.

-----

## Responsiveness

Design mobile-first. Use four breakpoints: default (phone), `sm:` (640px), `md:` (768px, tablet), `lg:` (1024px, desktop).

The artifact must render correctly on:
- 320px wide (small phone, portrait)
- 375px wide (standard phone)
- 768px (tablet)
- 1024x600 (Raspberry Pi display)
- 1920px (desktop)
- 2560px (ultra-wide / large monitor)

Use `overflow-x-auto` on tables and wide content. Avoid fixed widths. Use percentage or `max-w-` constraints.

### Content width

Use `max-w-5xl` (1024px) as the default. For data-dense dashboards with wide tables or many chart columns, use a wider container:

| Content type | Class |
|---|---|
| Standard dashboard | `max-w-5xl` |
| Wide / data-dense | `max-w-7xl` |
| Full-width (large monitors) | `max-w-[1600px]` with `px-4 sm:px-6 lg:px-8 xl:px-12` |

Do not use `max-w-full` without horizontal padding. Content touching screen edges is unreadable on large displays.

### Phone (default, < 640px)

- Stats grid: `grid-cols-2` minimum. Single-column stat cards waste space.
- Charts: minimum `h-48` (192px). Shorter charts are unreadable.
- Tables: always wrap in `overflow-x-auto`. Tables scroll horizontally on phones.
- Filter chips: use `px-3 py-2` for touch targets (not `py-1.5`). Minimum 44px tap height.
- Tabs: if more than 4 tabs, add `overflow-x-auto whitespace-nowrap` to the tab container so tabs scroll rather than wrap.
- Search and filters: stack vertically (`flex-col`), switch to `flex-row` at `md:`.
- Sidebar: hidden by default, slides in as overlay on tap.

### Tablet and desktop (md: 768px+)

- Stats: `md:grid-cols-4`
- Charts: `h-64` (256px)
- Page padding: `md:p-6`
- Two-column grids activate: `md:grid-cols-2`
- Three-column grids at `lg:`: `lg:grid-cols-3`
- Sidebar becomes persistent at `lg:` (`lg:relative lg:translate-x-0`)

### Large displays (xl: 1280px+)

For dashboards targeting large monitors:

- Use `xl:grid-cols-4` for card grids that benefit from more columns.
- Increase chart heights: `xl:h-96` for primary charts.
- Consider wider content containers (`max-w-7xl`) to fill the screen.
- For ultra-wide (2560px+), a persistent sidebar with wide content area works better than centering a narrow column in empty space.

### Touch targets

All interactive elements must be at least 44x44px. This applies to phones and Raspberry Pi touchscreens alike.

- Buttons and filter chips: `min-h-[44px]` with adequate padding
- Sort headers: `px-4 py-3` minimum
- Tab buttons: `px-4 py-2` minimum

### Chart responsiveness

Charts resize automatically via the `resize()` handler in the standard init pattern. Additional guidance for narrow screens:

- **Axis labels**: use `axisLabel: { rotate: 45, fontSize: 10 }` or `axisLabel: { interval: 'auto' }` to prevent label overlap on phones.
- **Legend**: move below the chart on narrow screens. Use ECharts `media` option for automatic responsive legend positioning:

```js
chart.setOption({
  // Base option (mobile-first)
  legend: { bottom: 0, orient: 'horizontal', left: 'center' },
  grid: { bottom: 40 },
  // ... series, axes, etc.
  media: [
    {
      query: { minWidth: 768 },
      option: {
        legend: { orient: 'vertical', right: 10, top: 'center', bottom: 'auto' },
        grid: { right: 120, bottom: 20 }
      }
    }
  ]
});
```

The `media` option works like CSS media queries inside ECharts. The base option applies to all sizes; query blocks override specific properties at breakpoints. This avoids legend overlapping chart content at phone widths.

- **Toolbox**: hide on phones. Set `toolbox: { show: window.innerWidth >= 768 }` in the chart option.

-----

## Platform constraints

The artifact runs in a browser on any platform: desktop Linux, Raspberry Pi, macOS, Windows. For low-powered hardware:

- Keep DOM node count low. Paginate or virtualize long lists instead of rendering hundreds of items.
- Prefer CSS transitions over JavaScript animation.
- Avoid stacking `box-shadow` and heavy `backdrop-blur` on large surfaces.
- Disable ECharts animation on Pi-targeted artifacts: `animation: false` in the chart option.
- Use the SVG renderer for dashboards with many small charts: `echarts.init(el, 'zinc-dark', { renderer: 'svg' })`. Use Canvas (default) for charts with large datasets.
- Dataset size guidance:
  - Under 1,000 points per series: no special handling needed.
  - 1,000-10,000 points: use `sampling: 'lttb'`, Canvas renderer, `animation: false`.
  - 10,000-100,000 points: add `large: true` and `largeThreshold: 2000` on the series for GPU-accelerated rendering.
  - Over 100,000 points: pre-aggregate the data before charting; this volume is beyond in-browser rendering.
- Note: `sampling: 'lttb'` only applies to line series. For bar charts with many categories, aggregate into bins. For scatter plots with thousands of points, use `large: true`.
- Avoid `requestAnimationFrame` loops unless the artifact is explicitly a visualization or game. A one-shot `requestAnimationFrame` for post-init chart resize (see Initialization section) is fine.

-----

## Accessibility media queries

### Reduced motion

Respect `prefers-reduced-motion` to avoid triggering vestibular disorders. Gate ECharts animation and CSS transitions:

```js
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Use in chart options
chart.setOption({
  animation: !prefersReducedMotion,
  // ...
});
```

In CSS, disable transitions for users who prefer reduced motion:

```html
<style>
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      transition-duration: 0.01ms !important;
      animation-duration: 0.01ms !important;
    }
  }
</style>
```

For system theme detection, the `tc()` getter pattern, and `zinc-light` theme registration, see `references/tailwind-guide.md`.

-----

## Default toolbox

Enable `saveAsImage` and `restore` in every chart's toolbox by default. These cost nothing and users expect them:

```js
toolbox: {
  feature: {
    saveAsImage: { pixelRatio: 2 },
    restore: {}
  }
}
```

Add `dataZoom` and `dataView` when appropriate for the chart type (time-series, tables of raw data). Hide the toolbox on small screens: `toolbox: { show: window.innerWidth >= 768 }`.

-----

## Quality checklist

Before saving the file, verify:

1. The page opens without console errors (no undefined references, no missing scripts).
2. All data is hardcoded at the top and clearly structured for easy editing.
3. The layout works at mobile, tablet, and desktop widths.
4. Dark theme tokens are consistent (not mixing `zinc-900` page with `zinc-900` cards).
5. Interactive elements (tabs, filters, sort) work without requiring hover.
6. Charts initialize correctly (via `$nextTick` + `requestAnimationFrame` resize), resize on window resize, and reflect filtered data.
7. No unused CDN scripts in the head.
8. `x-cloak` style is present in the head.
9. Alpine.js script tag is last, with `defer`.
10. File is named with kebab-case.
11. `prefers-reduced-motion` is respected for animation.

If the artifact includes any of the following features, also verify:

12. Print stylesheet hides interactive controls and forces readable colors. (See `references/features.md`.)
13. CSV export produces valid, escaped output for all data types.
14. Fullscreen panels resize charts correctly on enter and exit.
15. View-as-table shows equivalent data to the chart it accompanies.
16. Color-blind palette toggle updates all charts immediately.

-----

## Reference files

Read the indicated file BEFORE generating HTML when the artifact matches any trigger below. Do not read files the artifact does not need.

| Trigger | File |
|---|---|
| Any chart type beyond line, bar, area, pie, or scatter | `references/chart-examples.md` |
| Sparklines in table cells | `references/chart-examples.md` |
| Gradient area fills or bar fills | `references/chart-examples.md` |
| Brush selection on charts | `references/chart-examples.md` |
| Dashboard features: cross-filtering, CSV export, pagination, toasts, drawers, sticky headers, fullscreen panels, URL hash state, skeleton loading, view-as-table, color-blind toggle, keyboard shortcuts, print stylesheet | `references/features.md` |
| Chart selection reasoning, dashboard composition, visualization anti-patterns | `references/chart-selection.md` |
| Component layout patterns and recurring structures | `references/patterns.md` |
| Tailwind theme tokens, ECharts theme config, spacing conventions | `references/tailwind-guide.md` |
| Dark/light mode toggle with system theme detection | `references/tailwind-guide.md` |
| Complex artifact needing structural reference | Read one example: `examples/example-dashboard.html` or `examples/example-gdp-analysis.html` |
