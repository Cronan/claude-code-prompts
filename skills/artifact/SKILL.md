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
    }
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

## Light theme

When the user requests a light theme, use these tokens instead.

Background hierarchy:
- Page: `bg-zinc-50`
- Card / panel: `bg-white`
- Elevated surface: `bg-white`
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

-----

## Layout

Standard page shell:

```html
<div class="max-w-5xl mx-auto p-3 md:p-6">
  <h1 class="text-xl md:text-2xl font-bold mb-6">Title</h1>
  <!-- content -->
</div>
```

Use `max-w-5xl` as the default content width. Use `p-3 md:p-6` for mobile-first padding.

Grid patterns:
- Stats row: `grid grid-cols-2 md:grid-cols-4 gap-3`
- Two-column: `grid grid-cols-1 md:grid-cols-2 gap-4`
- Three-column: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`

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

Use pill-style tabs inside a container:

```html
<div class="flex gap-1 bg-zinc-800 rounded-lg p-1">
  <template x-for="t in tabs" :key="t">
    <button @click="tab = t"
            :class="tab === t
              ? 'bg-zinc-700 text-white'
              : 'text-zinc-400 hover:text-zinc-200'"
            class="px-4 py-2 rounded-md text-sm font-medium transition-colors"
            x-text="t"></button>
  </template>
</div>
```

Show tab content with `x-show`:

```html
<div x-show="tab === 'overview'">...</div>
<div x-show="tab === 'details'">...</div>
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
| Line | `'line'` | Add `smooth: true` for curved lines |
| Bar | `'bar'` | Add `barWidth: '50%'` to control width |
| Area | `'line'` | Add `areaStyle: { opacity: 0.3 }` to a line series |
| Pie | `'pie'` | No axes. Data is `[{ name, value }]`. Use `radius: ['40%', '70%']` for donut |
| Radar | `'radar'` | Needs a `radar` component with `indicator` array instead of axes |
| Scatter | `'scatter'` | Data is `[[x, y], ...]` pairs. Both axes are `type: 'value'` |

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

Connected charts show linked crosshairs on hover -- move over one chart and see the corresponding position on all others.

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

Toggle sort direction on header click:

```html
<th @click="toggleSort('name')"
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

Design mobile-first. Three breakpoints: default (mobile), `md:` (tablet), `lg:` (desktop).

The artifact must not break on:
- 1024x600 (common Raspberry Pi display)
- 375px wide (phone)
- 1920px wide (desktop)

Use `overflow-x-auto` on tables and wide content. Avoid fixed widths. Use percentage or `max-w-` constraints.

-----

## Platform constraints

The artifact runs in a browser on any platform: desktop Linux, Raspberry Pi, macOS, Windows. For low-powered hardware:

- Keep DOM node count low. Paginate or virtualize long lists instead of rendering hundreds of items.
- Prefer CSS transitions over JavaScript animation.
- Avoid stacking `box-shadow` and heavy `backdrop-blur` on large surfaces.
- Disable ECharts animation on Pi-targeted artifacts: `animation: false` in the chart option.
- Use the SVG renderer for dashboards with many small charts: `echarts.init(el, 'zinc-dark', { renderer: 'svg' })`.
- Use the Canvas renderer (default) for charts with large datasets (>1000 points).
- Keep chart datasets under 500 data points per series for general use. Use ECharts `sampling: 'lttb'` for larger datasets.
- Avoid `requestAnimationFrame` loops unless the artifact is explicitly a visualization or game.

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

-----

## Reference files

Before building complex artifacts, read the reference material in this skill directory:

- Component layout patterns and recurring structures: `references/patterns.md`
- Tailwind dark theme tokens, ECharts theme configuration, and spacing conventions: `references/tailwind-guide.md`
- Complete working example: `examples/example-dashboard.html`
