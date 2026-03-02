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
  Alpine.data('app', () => ({
    tab: 'overview',
    search: '',
    items: ITEMS,
    charts: {},

    get filtered() {
      return this.items.filter(item =>
        item.name.toLowerCase().includes(this.search.toLowerCase())
      );
    },

    init() {
      this.charts.main = echarts.init(this.$refs.mainChart, 'zinc-dark');
      this.charts.main.setOption({ /* ... */ });

      this.$watch('filtered', () => this.updateCharts());

      const resizeAll = () => {
        Object.values(this.charts).forEach(c => c.resize());
      };
      window.addEventListener('resize', resizeAll);
    },

    updateCharts() {
      this.charts.main.setOption({
        xAxis: { data: this.filtered.map(d => d.name) },
        series: [{ data: this.filtered.map(d => d.value) }]
      });
    }
  }));

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
Alpine.data('app', () => ({
  darkMode: true,
  // ...
  toggleTheme() {
    this.darkMode = !this.darkMode;
    // Re-initialize charts with the appropriate theme
    Object.values(this.charts).forEach(c => c.dispose());
    this.$nextTick(() => this.initCharts());
  }
}));
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
this.charts.main = echarts.init(this.$refs.mainChart, theme);
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

Initialize charts in the Alpine `init()` method using `$refs`:

```js
init() {
  this.charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
  this.charts.cpu.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series: [{ name: 'CPU', type: 'line', data: values, areaStyle: { opacity: 0.2 } }]
  });

  window.addEventListener('resize', () => {
    Object.values(this.charts).forEach(c => c.resize());
  });
}
```

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
  this.charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
  this.charts.cpu.setOption({ /* ... */ });

  this.$watch('tab', () => {
    this.$nextTick(() => {
      Object.values(this.charts).forEach(c => c.resize());
    });
  });
}
```

Use `x-show` (not `x-if`) for tab panels so the DOM elements exist at init time. `x-show` only toggles `display: none`; the elements remain in the DOM.

**Option B: Lazy initialization on first tab activation.**

```js
init() {
  this.$watch('tab', (val) => {
    if (val === 'charts' && !this.charts.cpu) {
      this.$nextTick(() => {
        this.charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
        this.charts.cpu.setOption({ /* ... */ });
      });
    }
  });
}
```

Option A is simpler and recommended for most artifacts.

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

### Chart type examples

The table above covers basic configuration. The examples below show complete option objects for types that need more than a `series.type` and data array.

**Radar** -- multi-dimensional comparison. Each indicator is an axis spoke:

```js
{
  radar: {
    indicator: [
      { name: 'Performance', max: 100 },
      { name: 'Reliability', max: 100 },
      { name: 'Security', max: 100 },
      { name: 'Usability', max: 100 },
      { name: 'Scalability', max: 100 }
    ],
    shape: 'polygon'
  },
  series: [{
    type: 'radar',
    data: [
      { value: [85, 90, 72, 68, 95], name: 'Service A' },
      { value: [70, 82, 91, 88, 60], name: 'Service B' }
    ]
  }]
}
```

**Candlestick with volume** -- combine candlestick and bar series with dual axes. The volume bars sit below the price chart:

```js
{
  xAxis: { type: 'category', data: dates },
  yAxis: [
    { type: 'value', name: 'Price', scale: true },
    { type: 'value', name: 'Volume', max: (val) => val.max * 3,
      axisLabel: { show: false }, splitLine: { show: false } }
  ],
  series: [
    { type: 'candlestick', data: ohlcData, yAxisIndex: 0 },
    { type: 'bar', data: volumeData, yAxisIndex: 1,
      itemStyle: { color: 'rgba(59, 130, 246, 0.3)' }, barWidth: '60%' }
  ],
  dataZoom: [{ type: 'slider', xAxisIndex: 0 }, { type: 'inside' }]
}
```

The `max: (val) => val.max * 3` on the volume axis keeps volume bars in the lower third of the chart area.

**Heatmap** -- requires a `visualMap` component for the color gradient:

```js
{
  xAxis: { type: 'category', data: hours },
  yAxis: { type: 'category', data: days },
  visualMap: {
    min: 0, max: 100, calculable: true,
    orient: 'horizontal', left: 'center', bottom: 0,
    inRange: { color: ['#27272a', '#3b82f6', '#10b981'] }
  },
  series: [{
    type: 'heatmap',
    data: data,  // [[hourIndex, dayIndex, value], ...]
    label: { show: true, formatter: (p) => p.value[2] },
    emphasis: { itemStyle: { borderColor: '#fff', borderWidth: 1 } }
  }]
}
```

**Treemap** -- hierarchical data with drill-down. Click a node to zoom in; click the breadcrumb to zoom out:

```js
{
  series: [{
    type: 'treemap',
    data: [
      { name: 'Engineering', value: 1200000, children: [
        { name: 'Backend', value: 600000 },
        { name: 'Frontend', value: 400000 },
        { name: 'Infra', value: 200000 }
      ]},
      { name: 'Product', value: 400000 }
    ],
    label: { formatter: (p) => p.name + '\n' + fmt.compact(p.value) },
    breadcrumb: { itemStyle: { color: '#3f3f46', textStyle: { color: '#d4d4d8' } } },
    levels: [
      { itemStyle: { borderColor: '#3f3f46', borderWidth: 2, gapWidth: 2 } },
      { itemStyle: { borderColor: '#27272a', borderWidth: 1, gapWidth: 1 } }
    ]
  }]
}
```

**Boxplot** -- distribution comparison across categories:

```js
{
  xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
  yAxis: { type: 'value', name: 'Response Time (ms)' },
  series: [{
    type: 'boxplot',
    data: [
      [12, 25, 35, 48, 72],   // Q1: [min, Q1, median, Q3, max]
      [15, 22, 30, 42, 58],   // Q2
      [18, 28, 38, 52, 85],   // Q3
      [10, 20, 28, 40, 95]    // Q4
    ]
  }]
}
```

To add outlier points alongside a boxplot, add a scatter series with the same x-axis. ECharts does not auto-calculate outliers; pre-compute them in the data.

**Gauge** -- single KPI display. Use for dashboard hero metrics:

```js
{
  series: [{
    type: 'gauge',
    data: [{ value: 72, name: 'Uptime %' }],
    min: 0, max: 100,
    axisLine: {
      lineStyle: {
        width: 12,
        color: [[0.6, '#ef4444'], [0.8, '#f59e0b'], [1, '#10b981']]
      }
    },
    pointer: { width: 4 },
    detail: { formatter: '{value}%', fontSize: 24, color: '#f4f4f5', offsetCenter: [0, '60%'] },
    title: { offsetCenter: [0, '80%'], color: '#a1a1aa' }
  }]
}
```

The `color` array on `axisLine` defines threshold bands: red below 60, amber 60-80, green above 80.

**Funnel** -- conversion pipeline. Data must be sorted in descending order:

```js
{
  series: [{
    type: 'funnel',
    data: [
      { value: 10000, name: 'Visitors' },
      { value: 4200, name: 'Signups' },
      { value: 1800, name: 'Active' },
      { value: 600, name: 'Paid' },
      { value: 180, name: 'Enterprise' }
    ],
    left: '10%', width: '80%',
    label: {
      formatter: (p) => p.name + ': ' + fmt.num(p.value),
      position: 'inside'
    },
    gap: 2
  }]
}
```

**Sankey** -- flow between nodes. Each link has a source, target, and value:

```js
{
  series: [{
    type: 'sankey',
    data: [
      { name: 'Organic' }, { name: 'Paid' }, { name: 'Referral' },
      { name: 'Homepage' }, { name: 'Pricing' },
      { name: 'Signup' }, { name: 'Bounce' }
    ],
    links: [
      { source: 'Organic', target: 'Homepage', value: 5000 },
      { source: 'Paid', target: 'Homepage', value: 3000 },
      { source: 'Referral', target: 'Homepage', value: 1200 },
      { source: 'Homepage', target: 'Pricing', value: 4800 },
      { source: 'Homepage', target: 'Bounce', value: 4400 },
      { source: 'Pricing', target: 'Signup', value: 2200 },
      { source: 'Pricing', target: 'Bounce', value: 2600 }
    ],
    emphasis: { focus: 'adjacency' },
    lineStyle: { color: 'source', opacity: 0.4 },
    label: { color: '#d4d4d8' }
  }]
}
```

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

### Linking charts

Synchronize tooltip position, legend toggles, and zoom range across charts:

```js
echarts.connect([this.charts.cpu, this.charts.memory, this.charts.network]);
```

Connected charts show linked crosshairs on hover -- move over one chart and see the corresponding position on all others. Only connect charts that share compatible axis types and data ranges. Connecting a time-series line chart to a categorical bar chart produces confusing crosshair behavior.

### Reactive data updates

When Alpine state changes (search, filter, tab), update charts with `setOption`. ECharts diffs and animates the transition:

```js
this.$watch('filtered', () => {
  this.charts.main.setOption({
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
  this.charts.main = echarts.init(this.$refs.mainChart, 'zinc-dark');
  this.charts.main.setOption({ /* ... */ });
  this.charts.main.on('click', (params) => {
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

-----

## Alpine.js patterns

### State management

All UI state lives in the `x-data` object. Define properties for tabs, search queries, sort keys, expanded sections, and selected items:

```js
Alpine.data('app', () => ({
  tab: 'overview',
  search: '',
  sortKey: 'name',
  sortDir: 'asc',
  items: ITEMS,
  charts: {},
  // ...
}));
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
- **Legend**: move below the chart on narrow screens: `legend: { bottom: 0, orient: 'horizontal' }`. Top-right placement overlaps the chart at phone widths.
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
- Avoid `requestAnimationFrame` loops unless the artifact is explicitly a visualization or game.

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

### System theme detection

When building artifacts with a dark/light toggle, detect the system preference on load:

```js
Alpine.data('app', () => ({
  darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
  // ...
}));
```

This sets the initial theme to match the user's OS setting. The toggle button still works to override it.

-----

## Print stylesheet

Add a `@media print` block to make dashboards printable. Force a white background, hide interactive controls, and prevent charts from splitting across pages:

```html
<style>
  @media print {
    body { background: white !important; color: black !important; }
    .no-print { display: none !important; }
    .bg-zinc-800, .bg-zinc-900 { background: white !important; border-color: #e4e4e7 !important; }
    .text-white, .text-zinc-300, .text-zinc-400 { color: black !important; }
    canvas { max-width: 100% !important; }
    .break-inside-avoid { break-inside: avoid; }
  }
</style>
```

Apply `no-print` to elements that should not appear in print: tab bars, filter controls, search inputs, toggle buttons. Apply `break-inside-avoid` to chart cards so they don't split across page boundaries.

ECharts renders to `<canvas>` which prints natively. No extra handling needed for chart content.

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

## Synced crosshair across charts

Use `echarts.connect()` to synchronize tooltip position and crosshair across multiple charts that share the same x-axis:

```js
init() {
  this.charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
  this.charts.memory = echarts.init(this.$refs.memChart, 'zinc-dark');
  this.charts.network = echarts.init(this.$refs.netChart, 'zinc-dark');

  // Sync hover crosshair across all three
  echarts.connect([this.charts.cpu, this.charts.memory, this.charts.network]);
}
```

Only connect charts that share compatible axis types and data ranges. Connecting a time-series chart to a categorical bar chart produces confusing crosshair behavior. Connected charts also sync legend toggles and DataZoom ranges.

-----

## CSV export

Add a `downloadCSV()` utility for exporting table or chart data. Works on any browser without dependencies:

```js
downloadCSV(filename, headers, rows) {
  const escape = (v) => '"' + String(v).replace(/"/g, '""') + '"';
  const csv = [headers.map(escape).join(',')]
    .concat(rows.map(r => r.map(escape).join(',')))
    .join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

Wire it to a button:

```html
<button @click="downloadCSV('services.csv',
    ['Name', 'Status', 'CPU', 'Memory'],
    filtered.map(s => [s.name, s.status, s.cpu, s.memory]))"
  class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-3 py-2 rounded-lg text-sm font-medium transition-colors border border-zinc-700 no-print">
  Export CSV
</button>
```

-----

## Fullscreen panel

Let users expand a single chart card to fill the viewport. Uses Alpine state and a fixed overlay:

```html
<div :class="fullscreen === 'cpu' ? 'fixed inset-0 z-50 bg-zinc-900 p-4 md:p-8' : ''"
     class="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-sm text-zinc-400">CPU Usage</h2>
    <button @click="fullscreen = fullscreen === 'cpu' ? null : 'cpu'"
            class="text-zinc-400 hover:text-zinc-200 no-print"
            :aria-label="fullscreen === 'cpu' ? 'Exit fullscreen' : 'Enter fullscreen'">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path x-show="fullscreen !== 'cpu'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"/>
        <path x-show="fullscreen === 'cpu'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
  <div x-ref="cpuChart" :class="fullscreen === 'cpu' ? 'h-[calc(100vh-8rem)]' : 'h-64'" class="w-full"></div>
</div>
```

Alpine state:

```js
fullscreen: null,

// Watch for fullscreen changes and resize the affected chart
init() {
  this.$watch('fullscreen', () => {
    this.$nextTick(() => {
      Object.values(this.charts).forEach(c => c.resize());
    });
  });
}
```

Press `Escape` to exit fullscreen:

```html
<div @keydown.escape.window="fullscreen = null" x-data="app">
```

-----

## URL hash state

Encode filter values, active tab, and other UI state in the URL hash so views are shareable and bookmarkable:

```js
Alpine.data('app', () => ({
  tab: 'Overview',
  search: '',
  statusFilter: 'All',

  init() {
    // Read state from hash on load
    this.readHash();

    // Write state to hash on change
    this.$watch('tab', () => this.writeHash());
    this.$watch('search', () => this.writeHash());
    this.$watch('statusFilter', () => this.writeHash());

    // Handle browser back/forward
    window.addEventListener('hashchange', () => this.readHash());
  },

  readHash() {
    const params = new URLSearchParams(location.hash.slice(1));
    if (params.has('tab')) this.tab = params.get('tab');
    if (params.has('q')) this.search = params.get('q');
    if (params.has('status')) this.statusFilter = params.get('status');
  },

  writeHash() {
    const params = new URLSearchParams();
    if (this.tab !== 'Overview') params.set('tab', this.tab);
    if (this.search) params.set('q', this.search);
    if (this.statusFilter !== 'All') params.set('status', this.statusFilter);
    const hash = params.toString();
    history.replaceState(null, '', hash ? '#' + hash : location.pathname);
  }
}));
```

Use `replaceState` (not `pushState`) to avoid polluting the browser history with every keystroke. The hash is only written for non-default values to keep URLs clean.

-----

## Skeleton loading

Show pulsing placeholder blocks while CDN scripts load and Alpine hydrates. These are pure HTML/CSS with no JavaScript dependency:

```html
<div id="skeleton" class="max-w-5xl mx-auto p-3 md:p-6">
  <div class="h-8 w-48 bg-zinc-800 rounded animate-pulse mb-6"></div>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
    <div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700 h-20 animate-pulse"></div>
    <div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700 h-20 animate-pulse"></div>
    <div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700 h-20 animate-pulse"></div>
    <div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700 h-20 animate-pulse"></div>
  </div>
  <div class="bg-zinc-800 rounded-xl border border-zinc-700 h-64 animate-pulse"></div>
</div>
```

Hide the skeleton once Alpine initializes. The `x-cloak` attribute on the main app container already handles this -- Alpine removes `x-cloak` when it processes the element, so the real content appears. Hide the skeleton with a matching rule:

```html
<style>
  [x-cloak] { display: none !important; }
  [x-cloak] ~ #skeleton { display: block; }
  :not([x-cloak]) ~ #skeleton { display: none; }
</style>
```

Or simpler: place the skeleton inside the `x-data` container and use `x-show="false"` to hide it after Alpine processes.

Use skeletons for dashboards with multiple CDN dependencies where the load delay is noticeable. For simple artifacts with minimal scripts, skip them.

-----

## Cross-filtering

Wire chart click events to Alpine state to filter other charts and tables. This is the pattern that separates a dashboard from a page of independent charts:

```js
Alpine.data('app', () => ({
  selectedCategory: null,
  items: ITEMS,

  get filtered() {
    if (!this.selectedCategory) return this.items;
    return this.items.filter(i => i.category === this.selectedCategory);
  },

  init() {
    this.charts.pie = echarts.init(this.$refs.pieChart, 'zinc-dark');
    this.charts.pie.setOption({ /* ... */ });

    // Click a pie slice to filter everything else
    this.charts.pie.on('click', (params) => {
      this.selectedCategory = this.selectedCategory === params.name
        ? null  // click again to clear
        : params.name;
    });

    // Update dependent charts when filter changes
    this.$watch('filtered', () => this.updateBarChart());
  }
}));
```

In the HTML, show the active filter and a clear button:

```html
<div x-show="selectedCategory" class="flex items-center gap-2 mb-4">
  <span class="text-sm text-zinc-400">Filtered by:</span>
  <span class="bg-blue-600 text-white px-2 py-0.5 rounded text-xs" x-text="selectedCategory"></span>
  <button @click="selectedCategory = null" class="text-zinc-400 hover:text-zinc-200 text-xs">Clear</button>
</div>
```

Highlight the selected element in the source chart using ECharts `dispatchAction`:

```js
this.$watch('selectedCategory', (val) => {
  this.charts.pie.dispatchAction({
    type: val ? 'highlight' : 'downplay',
    name: val
  });
});
```

-----

## Keyboard shortcuts

Add keyboard shortcuts for common actions. Use Alpine's `@keydown.window` directive:

```html
<div @keydown.escape.window="fullscreen = null; selectedCategory = null"
     @keydown.window="handleKeyboard($event)"
     x-data="app">
```

```js
handleKeyboard(e) {
  // Ignore if user is typing in an input
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

  if (e.key === '?' && !e.ctrlKey) {
    this.showHelp = !this.showHelp;
  }
  // Tab switching with number keys
  const num = parseInt(e.key);
  if (num >= 1 && num <= this.tabs.length) {
    this.tab = this.tabs[num - 1];
  }
}
```

-----

## Quality checklist

Before saving the file, verify:

1. The page opens without console errors (no undefined references, no missing scripts).
2. All data is hardcoded at the top and clearly structured for easy editing.
3. The layout works at mobile, tablet, and desktop widths.
4. Dark theme tokens are consistent (not mixing `zinc-900` page with `zinc-900` cards).
5. Interactive elements (tabs, filters, sort) work without requiring hover.
6. Charts initialize correctly, resize on window resize, and reflect filtered data.
7. No unused CDN scripts in the head.
8. `x-cloak` style is present in the head.
9. Alpine.js script tag is last, with `defer`.
10. File is named with kebab-case.
11. `prefers-reduced-motion` is respected for animation.
12. Print stylesheet hides interactive controls and forces readable colors.
13. CSV export produces valid, escaped output for all data types.
14. Fullscreen panels resize charts correctly on enter and exit.

-----

## Reference files

Before building complex artifacts, read the reference material in this skill directory:

- Component layout patterns and recurring structures: `references/patterns.md`
- Tailwind dark theme tokens, ECharts theme configuration, and spacing conventions: `references/tailwind-guide.md`
- Chart type showcase: `examples/example-chart-showcase.html`
- Dashboard with features: `examples/example-dashboard.html`
- Real-world analysis dashboard: `examples/example-gdp-analysis.html`
