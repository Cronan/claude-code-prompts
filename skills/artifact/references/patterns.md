# Component patterns

Recurring layout and UI structures for HTML artifacts. Each pattern shows the minimal skeleton using the correct dark theme tokens and Alpine.js directives. Combine them to build full artifacts.

-----

## Page shell

Every artifact starts here. The `alpine:init` listener registers data and components before Alpine processes the DOM.

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
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.6.0/dist/echarts.min.js"></script>
</head>
<body class="bg-zinc-900 text-white min-h-screen">

<script>
document.addEventListener('alpine:init', () => {
  echarts.registerTheme('zinc-dark', { /* see SKILL.md */ });

  const DATA = [ /* ... */ ];

  Alpine.data('app', () => ({
    items: DATA,
    // state, getters, methods, init()
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

## Sidebar layout

Fixed sidebar with scrollable main area. Collapses on mobile with a toggle button.

```html
<div x-cloak x-data="app">
  <div class="flex min-h-screen bg-zinc-900 text-white">

    <!-- Sidebar -->
    <aside :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
           class="fixed inset-y-0 left-0 z-40 w-64 bg-zinc-800 border-r border-zinc-700
                  transform transition-transform duration-200
                  lg:relative lg:translate-x-0">
      <div class="p-4">
        <h2 class="text-lg font-bold mb-4">App Name</h2>
        <nav class="space-y-1">
          <!-- nav items -->
        </nav>
      </div>
    </aside>

    <!-- Overlay -->
    <div x-show="sidebarOpen" @click="sidebarOpen = false"
         class="fixed inset-0 z-30 bg-black/50 lg:hidden"
         x-transition.opacity></div>

    <!-- Main -->
    <div class="flex-1 min-w-0">
      <header class="border-b border-zinc-700 p-3 md:p-4 flex items-center gap-3">
        <button @click="sidebarOpen = !sidebarOpen"
                aria-label="Toggle sidebar"
                class="lg:hidden text-zinc-400 hover:text-white">
          <!-- hamburger icon (inline SVG) -->
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <h1 class="text-lg font-bold">Page Title</h1>
      </header>
      <main class="p-3 md:p-6">
        <!-- content -->
      </main>
    </div>
  </div>
</div>
```

Alpine data for the sidebar:

```js
Alpine.data('app', () => ({
  sidebarOpen: false,
  // ...
}));
```

## Card

The basic content container for dashboard tiles, detail panels, list items.

```html
<div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
  <h3 class="text-sm text-zinc-400 mb-2">Card Title</h3>
  <!-- content -->
</div>
```

## Stat card

A card showing a single metric with optional trend indicator.

```html
<div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
  <p class="text-sm text-zinc-400" x-text="stat.label"></p>
  <p class="text-2xl font-bold mt-1" x-text="stat.value"></p>
  <p x-show="stat.change"
     :class="stat.trend === 'up' ? 'text-emerald-400' : 'text-red-400'"
     class="text-sm font-medium mt-1"
     x-text="(stat.trend === 'up' ? '+' : '') + stat.change"></p>
</div>
```

## Stats grid

Responsive grid for a row of stat cards.

```html
<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
  <template x-for="stat in stats" :key="stat.label">
    <div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
      <p class="text-sm text-zinc-400" x-text="stat.label"></p>
      <p class="text-2xl font-bold mt-1" x-text="stat.value"></p>
      <p x-show="stat.change"
         :class="stat.trend === 'up' ? 'text-emerald-400' : 'text-red-400'"
         class="text-sm font-medium mt-1"
         x-text="(stat.trend === 'up' ? '+' : '') + stat.change"></p>
    </div>
  </template>
</div>
```

## Tabs

Pill-style tabs inside a container. Active tab gets a lighter background. Use ARIA tab roles for screen reader support.

```html
<div role="tablist" class="flex gap-1 bg-zinc-800 rounded-lg p-1 mb-4">
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

<div role="tabpanel" id="panel-overview" x-show="tab === 'Overview'"><!-- content --></div>
<div role="tabpanel" id="panel-details" x-show="tab === 'Details'"><!-- content --></div>
<div role="tabpanel" id="panel-logs" x-show="tab === 'Logs'"><!-- content --></div>
```

Alpine data:

```js
tab: 'Overview',
tabs: ['Overview', 'Details', 'Logs'],
```

## Data table

Scrollable table with clickable sort headers. Sort headers are keyboard-accessible with `tabindex` and `@keydown.enter`.

```html
<div class="overflow-x-auto">
  <table class="w-full text-sm text-left">
    <thead>
      <tr class="border-b border-zinc-700 text-zinc-400">
        <th @click="toggleSort('name')" @keydown.enter="toggleSort('name')"
            tabindex="0"
            :aria-sort="sortKey === 'name' ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'"
            class="px-4 py-3 font-medium cursor-pointer hover:text-zinc-200">
          Name
          <span x-show="sortKey === 'name'" x-text="sortDir === 'asc' ? '\u2191' : '\u2193'" class="ml-1"></span>
        </th>
        <th @click="toggleSort('status')" @keydown.enter="toggleSort('status')"
            tabindex="0"
            :aria-sort="sortKey === 'status' ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'"
            class="px-4 py-3 font-medium cursor-pointer hover:text-zinc-200">
          Status
          <span x-show="sortKey === 'status'" x-text="sortDir === 'asc' ? '\u2191' : '\u2193'" class="ml-1"></span>
        </th>
        <th @click="toggleSort('value')" @keydown.enter="toggleSort('value')"
            tabindex="0"
            :aria-sort="sortKey === 'value' ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'"
            class="px-4 py-3 font-medium cursor-pointer hover:text-zinc-200">
          Value
          <span x-show="sortKey === 'value'" x-text="sortDir === 'asc' ? '\u2191' : '\u2193'" class="ml-1"></span>
        </th>
      </tr>
    </thead>
    <tbody>
      <template x-for="row in sorted" :key="row.id">
        <tr class="border-b border-zinc-700/50 hover:bg-zinc-800/50">
          <td class="px-4 py-3 text-zinc-300" x-text="row.name"></td>
          <td class="px-4 py-3 text-zinc-300" x-text="row.status"></td>
          <td class="px-4 py-3 text-zinc-300" x-text="row.value"></td>
        </tr>
      </template>
    </tbody>
  </table>
</div>
```

Alpine data for sorting:

```js
sortKey: 'name',
sortDir: 'asc',

get sorted() {
  return [...this.filtered].sort((a, b) => {
    const av = a[this.sortKey], bv = b[this.sortKey];
    const cmp = av > bv ? 1 : av < bv ? -1 : 0;
    return this.sortDir === 'asc' ? cmp : -cmp;
  });
},

toggleSort(key) {
  if (this.sortKey === key) {
    this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    this.sortKey = key;
    this.sortDir = 'asc';
  }
}
```

## Search bar

Text input with search icon. Pair with a getter for filtering.

```html
<div class="relative">
  <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500"
       fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
  </svg>
  <input type="text" x-model="search" placeholder="Search..."
         aria-label="Search"
         class="w-full pl-10 pr-4 py-2 bg-zinc-800/50 border border-zinc-700 rounded-lg text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500">
</div>
```

## Filter chips

Clickable filter buttons. Pair with search bar for combined filtering.

```html
<div class="flex gap-2 flex-wrap">
  <template x-for="opt in filterOptions" :key="opt">
    <button @click="statusFilter = opt"
            :class="statusFilter === opt
              ? 'bg-blue-600 text-white'
              : 'bg-zinc-800 text-zinc-400 border border-zinc-700 hover:text-zinc-200'"
            class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
            x-text="opt"></button>
  </template>
</div>
```

Alpine data:

```js
statusFilter: 'All',
filterOptions: ['All', 'Active', 'Idle', 'Error'],

get filtered() {
  return this.items.filter(item => {
    const matchSearch = item.name.toLowerCase().includes(this.search.toLowerCase());
    const matchStatus = this.statusFilter === 'All' || item.status === this.statusFilter.toLowerCase();
    return matchSearch && matchStatus;
  });
}
```

## ECharts card

A chart inside a titled card. Initialize in `init()`, update reactively.

HTML:

```html
<div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
  <h3 class="text-sm text-zinc-400 mb-4">CPU Usage</h3>
  <div x-ref="cpuChart" class="h-48 w-full"></div>
</div>
```

Alpine init:

```js
init() {
  this.charts.cpu = echarts.init(this.$refs.cpuChart, 'zinc-dark');
  this.charts.cpu.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: CPU_HISTORY.map(d => d.time) },
    yAxis: { type: 'value', max: 100 },
    series: [{
      type: 'line',
      data: CPU_HISTORY.map(d => d.value),
      areaStyle: { opacity: 0.2 },
      smooth: true
    }]
  });

  window.addEventListener('resize', () => {
    Object.values(this.charts).forEach(c => c.resize());
  });
}
```

## Sparkline (inline table chart)

A tiny chart inside a table cell showing a data trend. No axes, no labels, no chrome.

Data (add a `trend` array to each row):

```js
const ITEMS = [
  { id: 1, name: 'Service A', value: 42, trend: [8, 10, 9, 14, 11, 10, 13, 15, 12, 11, 13, 12] },
  // ...
];
```

HTML (inside a `<template x-for>` table row):

```html
<td class="px-4 py-3">
  <div x-init="$nextTick(() => initSparkline($el, row))"
       style="width:80px;height:24px"></div>
</td>
```

Alpine methods:

```js
_sparklines: {},

initSparkline(el, row) {
  const key = 'spark-' + row.id;
  if (this._sparklines[key]) this._sparklines[key].dispose();
  const chart = echarts.init(el, this.currentTheme, { width: 80, height: 24 });
  chart.setOption({
    animation: false,
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    xAxis: { show: false, type: 'category' },
    yAxis: { show: false, type: 'value', min: 0 },
    tooltip: { show: false },
    series: [{
      type: 'line', data: row.trend, smooth: true, symbol: 'none',
      lineStyle: { width: 1.5, color: '#10b981' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
          { offset: 1, color: 'transparent' }
        ])
      }
    }]
  });
  this._sparklines[key] = chart;
},

disposeSparklines() {
  Object.values(this._sparklines).forEach(c => c.dispose());
  this._sparklines = {};
}
```

Call `disposeSparklines()` in `toggleTheme()` before re-initializing charts. Alpine's `x-init` on each `x-for` row re-creates sparklines when the list changes.

## Bullet chart

Horizontal bar with qualitative range bands and a target marker. Three stacked `'bar'` series overlaid with `barGap: '-100%'` plus a `'custom'` series for the target line.

```js
series: [
  // Background range bands (widest first, ascending z)
  { type: 'bar', barWidth: 30, barGap: '-100%', z: 1, silent: true,
    itemStyle: { color: 'rgba(16, 185, 129, 0.12)' }, data: [150] },
  { type: 'bar', barWidth: 30, barGap: '-100%', z: 2, silent: true,
    itemStyle: { color: 'rgba(16, 185, 129, 0.25)' }, data: [120] },
  // Actual value (narrow bar)
  { type: 'bar', barWidth: 12, barGap: '-100%', z: 3,
    itemStyle: { color: '#10b981' }, data: [95] },
  // Target marker (vertical line)
  { type: 'custom', z: 4,
    renderItem: (params, api) => {
      const point = api.coord([api.value(1), api.value(0)]);
      return {
        type: 'line',
        shape: { x1: point[0], y1: point[1] - 18, x2: point[0], y2: point[1] + 18 },
        style: { stroke: '#f4f4f5', lineWidth: 2.5 }
      };
    },
    data: [[0, 100]]
  }
]
```

Axes: `yAxis: { type: 'category' }`, `xAxis: { type: 'value', show: false }`.

## Lollipop chart

Dot on a stem -- less ink than a bar chart. Uses `'custom'` series with a `'group'` return containing a line (stem) and circle (dot).

```js
series: [{
  type: 'custom',
  renderItem: (params, api) => {
    const y = api.coord([0, api.value(0)])[1];
    const x = api.coord([api.value(1), 0])[0];
    const baseX = api.coord([0, 0])[0];
    return {
      type: 'group',
      children: [
        { type: 'line', shape: { x1: baseX, y1: y, x2: x, y2: y },
          style: { stroke: '#10b981', lineWidth: 2 } },
        { type: 'circle', shape: { cx: x, cy: y, r: 6 },
          style: { fill: '#10b981' } }
      ]
    };
  },
  data: [[0, 92], [1, 85], [2, 78]],
  label: { show: true, position: 'right', color: '#d4d4d8',
    formatter: (params) => params.value[1] }
}]
```

Axes: `yAxis: { type: 'category', inverse: true }`, `xAxis: { type: 'value' }`.

## Small multiples

Grid of identical mini-charts, one per category. Uses ECharts `grid` array with paired axes.

```js
const cols = 3, rows = 2;
const cellW = 100 / cols, cellH = 100 / rows;
const pad = { left: 6, right: 2, top: 5, bottom: 5 };

const grid = [], xAxis = [], yAxis = [], series = [];
categories.forEach((name, i) => {
  const col = i % cols, row = Math.floor(i / cols);
  grid.push({
    left: (col * cellW + pad.left) + '%',
    top: (row * cellH + pad.top) + '%',
    width: (cellW - pad.left - pad.right) + '%',
    height: (cellH - pad.top - pad.bottom) + '%'
  });
  xAxis.push({ type: 'category', data: times, gridIndex: i, show: row === rows - 1 });
  yAxis.push({ type: 'value', gridIndex: i, show: col === 0, name, nameLocation: 'middle' });
  series.push({
    type: 'line', data: datasets[i], xAxisIndex: i, yAxisIndex: i,
    smooth: true, symbol: 'none', areaStyle: { opacity: 0.2 }
  });
});
```

Show axis labels only on the left column (`col === 0`) and bottom row (`row === rows - 1`). Scales to 4-12 cells.

## Status badge

Small badge with opacity background for status indicators.

```html
<span :class="{
        'bg-emerald-900/30 text-emerald-400': row.status === 'active',
        'bg-zinc-700 text-zinc-300': row.status === 'idle',
        'bg-red-900/30 text-red-400': row.status === 'error',
        'bg-amber-900/30 text-amber-400': row.status === 'warning'
      }"
      class="px-2 py-0.5 rounded text-xs font-medium"
      x-text="row.status"></span>
```

Tailwind CDN safelist comment (place anywhere in the HTML):

```html
<!-- bg-emerald-900/30 text-emerald-400 bg-red-900/30 text-red-400
     bg-amber-900/30 text-amber-400 bg-zinc-700 text-zinc-300 -->
```

## Empty state

When a filtered or searched list has no results.

```html
<div x-show="filtered.length === 0"
     class="flex flex-col items-center justify-center py-12 text-zinc-400">
  <p class="text-sm">No results found</p>
</div>
```

## Expandable section

Click-to-expand detail panel. Uses click, not hover.

```html
<div class="border border-zinc-700 rounded-xl overflow-hidden" x-data="{ open: false }">
  <button @click="open = !open"
          :aria-expanded="open"
          class="w-full flex items-center justify-between px-4 py-3 bg-zinc-800 hover:bg-zinc-700/50 transition-colors">
    <span class="text-sm font-medium">Section Title</span>
    <svg :class="open ? 'rotate-180' : ''"
         class="w-4 h-4 text-zinc-400 transition-transform duration-200"
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
    </svg>
  </button>
  <div x-show="open" x-transition class="px-4 py-3 border-t border-zinc-700">
    <!-- content -->
  </div>
</div>
```

## Progress bar

Horizontal bar with percentage fill. Useful for disk usage, completion tracking. Use `role="progressbar"` with ARIA attributes for accessibility.

```html
<div class="flex items-center gap-3">
  <div class="flex-1 bg-zinc-700 rounded-full h-2 overflow-hidden"
       role="progressbar"
       :aria-valuenow="Math.round((item.used / item.total) * 100)"
       aria-valuemin="0" aria-valuemax="100">
    <div class="h-full rounded-full bg-blue-500"
         :style="'width: ' + Math.round((item.used / item.total) * 100) + '%'"></div>
  </div>
  <span class="text-xs text-zinc-400 w-10 text-right"
        x-text="Math.round((item.used / item.total) * 100) + '%'"></span>
</div>
```

## CSV export button

Download table data as CSV. The `downloadCSV` method handles quoting and escaping.

```html
<button @click="downloadCSV('data.csv',
    ['Name', 'Status', 'Value'],
    filtered.map(r => [r.name, r.status, r.value]))"
  class="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-3 py-2 rounded-lg text-sm font-medium transition-colors border border-zinc-700 no-print">
  <span class="flex items-center gap-2">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
    </svg>
    Export CSV
  </span>
</button>
```

Alpine method:

```js
downloadCSV(filename, headers, rows) {
  const escape = (v) => '"' + String(v).replace(/"/g, '""') + '"';
  const csv = [headers.map(escape).join(',')]
    .concat(rows.map(r => r.map(escape).join(',')))
    .join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
```

## Fullscreen chart panel

Expand a chart card to fill the viewport. Click or press Escape to exit.

```html
<div :class="fullscreen === 'main' ? 'fixed inset-0 z-50 bg-zinc-900 p-4 md:p-8' : ''"
     class="bg-zinc-800 rounded-xl p-4 border border-zinc-700 break-inside-avoid">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-sm text-zinc-400">Chart Title</h2>
    <button @click="fullscreen = fullscreen === 'main' ? null : 'main'"
            class="text-zinc-400 hover:text-zinc-200 no-print"
            :aria-label="fullscreen === 'main' ? 'Exit fullscreen' : 'Enter fullscreen'">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path x-show="fullscreen !== 'main'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"/>
        <path x-show="fullscreen === 'main'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
  <div x-ref="mainChart" :class="fullscreen === 'main' ? 'h-[calc(100vh-8rem)]' : 'h-64'" class="w-full"></div>
</div>
```

Alpine data:

```js
fullscreen: null,

init() {
  this.$watch('fullscreen', () => {
    this.$nextTick(() => Object.values(this.charts).forEach(c => c.resize()));
  });
}
```

## Skeleton loading

Pulsing placeholder shown while CDN scripts load. Pure HTML/CSS, no JavaScript.

```html
<!-- Shown until Alpine hydrates -->
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

<!-- Real content hidden until Alpine processes x-cloak -->
<div x-cloak x-data="app"><!-- ... --></div>
```

Add this CSS rule to auto-hide the skeleton when Alpine initializes:

```css
:not([x-cloak]) ~ #skeleton { display: none; }
```

## Print stylesheet

Include in the `<head>` to make dashboards printable. Hides interactive controls and forces readable colors.

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

Apply `no-print` to: tab bars, filter inputs, export buttons, toggle buttons. Apply `break-inside-avoid` to chart cards.

## Active filter indicator

Show which cross-filters are applied and let users clear them.

```html
<div x-show="selectedCategory" class="flex items-center gap-2 mb-4 no-print" x-transition>
  <span class="text-sm text-zinc-400">Filtered by:</span>
  <span class="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-medium" x-text="selectedCategory"></span>
  <button @click="selectedCategory = null"
          class="text-zinc-400 hover:text-zinc-200 text-xs ml-1">
    <svg class="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
    </svg>
    Clear
  </button>
</div>
```

## Dark/light toggle

Toggle between dark and light themes. Detects system preference on load. Updates `<html>` class and re-themes ECharts instances.

```html
<button @click="toggleTheme()"
        class="text-zinc-400 hover:text-zinc-200 no-print p-2 rounded-lg"
        :aria-label="darkMode ? 'Switch to light theme' : 'Switch to dark theme'">
  <svg x-show="darkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
  </svg>
  <svg x-show="!darkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
  </svg>
</button>
```

Alpine data:

```js
darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,

toggleTheme() {
  this.darkMode = !this.darkMode;
  document.documentElement.classList.toggle('dark', this.darkMode);
  // Re-theme all ECharts instances
  const theme = this.darkMode ? 'zinc-dark' : 'zinc-light';
  Object.keys(this.charts).forEach(key => {
    const el = this.charts[key].getDom();
    const opt = this.charts[key].getOption();
    this.charts[key].dispose();
    this.charts[key] = echarts.init(el, theme);
    this.charts[key].setOption(opt);
  });
}
```

Register a light theme alongside the dark theme in the `alpine:init` block:

```js
echarts.registerTheme('zinc-light', {
  backgroundColor: 'transparent',
  textStyle: { color: '#3f3f46' },
  title: { textStyle: { color: '#18181b' } },
  legend: { textStyle: { color: '#52525b' } },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#d4d4d8' } },
    axisLabel: { color: '#71717a' },
    splitLine: { lineStyle: { color: '#e4e4e7' } }
  },
  valueAxis: {
    axisLine: { lineStyle: { color: '#d4d4d8' } },
    axisLabel: { color: '#71717a' },
    splitLine: { lineStyle: { color: '#e4e4e7' } }
  },
  color: ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4']
});
```

In Tailwind, light mode classes use the base (unprefixed) utilities. Dark mode classes use `dark:` prefix. Since `darkMode: "class"` is configured, the `dark` class on `<html>` controls everything:

```html
<body class="bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white min-h-screen">
```

## View-as-table toggle

Swap between chart and data table views on the same card. Uses nested `x-data` for local toggle state.

```html
<div class="bg-zinc-800 rounded-xl p-4 border border-zinc-700" x-data="{ showTable: false }">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-sm text-zinc-400">Revenue by Month</h2>
    <button @click="showTable = !showTable"
            class="text-zinc-400 hover:text-zinc-200 text-xs no-print"
            :aria-label="showTable ? 'Show chart' : 'Show data table'">
      <span x-text="showTable ? 'Chart' : 'Table'"></span>
    </button>
  </div>

  <!-- Chart view -->
  <div x-show="!showTable" x-ref="revenueChart" class="h-64 w-full"></div>

  <!-- Table view -->
  <div x-show="showTable" class="overflow-x-auto">
    <table class="w-full text-sm text-left">
      <thead>
        <tr class="border-b border-zinc-700 text-zinc-400">
          <th class="px-3 py-2 font-medium">Month</th>
          <th class="px-3 py-2 font-medium text-right">Revenue</th>
        </tr>
      </thead>
      <tbody>
        <template x-for="(val, i) in revenueData" :key="i">
          <tr class="border-b border-zinc-700/50">
            <td class="px-3 py-2 text-zinc-300" x-text="months[i]"></td>
            <td class="px-3 py-2 text-zinc-300 text-right" x-text="'$' + val.toLocaleString()"></td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</div>
```

The chart stays initialized (via `x-show`, not `x-if`) so switching back is instant. Use nested `x-data` to keep the toggle state local to each card without polluting the parent component.

## Color-blind palette toggle

Runtime toggle that swaps ECharts color palette to a deuteranopia-safe set. Place the button in the dashboard header alongside other controls.

```html
<button @click="toggleColorBlind()"
        :class="colorBlindMode ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 border border-zinc-700'"
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors no-print"
        aria-label="Toggle color-blind safe palette">
  <span x-text="colorBlindMode ? 'Standard palette' : 'Color-blind safe'"></span>
</button>
```

Alpine data:

```js
colorBlindMode: false,

get palette() {
  return this.colorBlindMode
    ? ['#3b82f6', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']
    : ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4'];
},

toggleColorBlind() {
  this.colorBlindMode = !this.colorBlindMode;
  Object.values(this.charts).forEach(c => {
    c.setOption({ color: this.palette });
  });
}
```

The deuteranopia-safe palette avoids the red-green pair. All charts update immediately via `setOption` merge.

## Sticky table header

Keep column headers visible while scrolling long tables. Pure CSS.

```html
<div class="overflow-auto max-h-[32rem]">
  <table class="w-full text-sm text-left">
    <thead class="sticky top-0 z-10 bg-zinc-900 shadow-[0_1px_0_0_theme(colors.zinc.700)]">
      <tr class="border-b border-zinc-700 text-zinc-400">
        <th class="px-4 py-3 font-medium">Name</th>
        <th class="px-4 py-3 font-medium">Status</th>
        <th class="px-4 py-3 font-medium text-right">Value</th>
      </tr>
    </thead>
    <tbody>
      <template x-for="row in sorted" :key="row.id">
        <tr class="border-b border-zinc-700/50 hover:bg-zinc-800/50">
          <td class="px-4 py-3 text-zinc-300" x-text="row.name"></td>
          <td class="px-4 py-3 text-zinc-300" x-text="row.status"></td>
          <td class="px-4 py-3 text-zinc-300 text-right" x-text="row.value"></td>
        </tr>
      </template>
    </tbody>
  </table>
</div>
```

The outer `div` sets `overflow-auto` with a max height. The `thead` uses `sticky top-0 z-10` with a solid background matching the page. Match the background to the parent: `bg-zinc-900` for page-level tables, `bg-zinc-800` for tables inside cards.

## Detail panel / drawer

Side panel that slides in from the right when a table row is clicked.

```html
<!-- Overlay -->
<div x-show="drawerOpen" class="fixed inset-0 z-40" x-transition.opacity>
  <div class="absolute inset-0 bg-black/50" @click="drawerOpen = false"></div>
</div>

<!-- Panel -->
<div :class="drawerOpen ? 'translate-x-0' : 'translate-x-full'"
     @keydown.escape.window="drawerOpen = false"
     role="dialog" aria-modal="true"
     class="fixed top-0 right-0 z-50 h-full w-full max-w-md bg-zinc-800 border-l border-zinc-700
            shadow-xl transform transition-transform duration-200 overflow-y-auto">
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold" x-text="selectedItem?.name"></h2>
      <button @click="drawerOpen = false" class="text-zinc-400 hover:text-zinc-200 p-1"
              aria-label="Close detail panel">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
    <template x-if="selectedItem">
      <div class="space-y-4">
        <div>
          <p class="text-xs text-zinc-400 mb-1">Status</p>
          <p class="text-sm text-zinc-300" x-text="selectedItem.status"></p>
        </div>
        <!-- more detail fields -->
      </div>
    </template>
  </div>
</div>
```

Alpine data:

```js
drawerOpen: false,
selectedItem: null,
```

Open the drawer from a table row click: `@click="selectedItem = row; drawerOpen = true"`. Close with Escape: add `drawerOpen = false` to the `@keydown.escape.window` handler.

## Multi-select filter chips

Filter chips that allow toggling multiple values simultaneously.

```html
<div class="flex gap-2 flex-wrap">
  <button @click="activeFilters = []"
          :class="activeFilters.length === 0
            ? 'bg-blue-600 text-white'
            : 'bg-zinc-800 text-zinc-400 border border-zinc-700 hover:text-zinc-200'"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors">
    All
  </button>
  <template x-for="opt in filterOptions" :key="opt">
    <button @click="toggleFilter(opt)"
            :class="activeFilters.includes(opt)
              ? 'bg-blue-600 text-white'
              : 'bg-zinc-800 text-zinc-400 border border-zinc-700 hover:text-zinc-200'"
            class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
            x-text="opt"></button>
  </template>
</div>
```

Alpine data:

```js
activeFilters: [],
filterOptions: ['Active', 'Idle', 'Warning', 'Error'],

toggleFilter(opt) {
  const idx = this.activeFilters.indexOf(opt);
  if (idx === -1) {
    this.activeFilters.push(opt);
  } else {
    this.activeFilters.splice(idx, 1);
  }
},

get filtered() {
  return this.items.filter(item => {
    const matchSearch = item.name.toLowerCase().includes(this.search.toLowerCase());
    const matchFilter = this.activeFilters.length === 0
      || this.activeFilters.includes(item.status);
    return matchSearch && matchFilter;
  });
}
```

Empty `activeFilters` means show everything. "All" button clears the array.

## Pagination

Page controls for large tables. Slices the sorted array by page.

```html
<div class="flex items-center justify-between mt-4 text-sm">
  <span class="text-zinc-400"
        x-text="'Showing ' + (pageStart + 1) + '-' + Math.min(pageStart + pageSize, sorted.length) + ' of ' + sorted.length"></span>
  <div class="flex items-center gap-1">
    <button @click="page = Math.max(1, page - 1)"
            :disabled="page === 1"
            :class="page === 1 ? 'text-zinc-600 cursor-not-allowed' : 'text-zinc-400 hover:text-zinc-200'"
            class="px-3 py-1.5 rounded border border-zinc-700 text-xs">Prev</button>
    <template x-for="p in totalPages" :key="p">
      <button @click="page = p"
              :class="page === p ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-zinc-200'"
              class="px-3 py-1.5 rounded border border-zinc-700 text-xs min-w-[2rem]"
              x-text="p"></button>
    </template>
    <button @click="page = Math.min(totalPages, page + 1)"
            :disabled="page === totalPages"
            :class="page === totalPages ? 'text-zinc-600 cursor-not-allowed' : 'text-zinc-400 hover:text-zinc-200'"
            class="px-3 py-1.5 rounded border border-zinc-700 text-xs">Next</button>
  </div>
</div>
```

Alpine data:

```js
page: 1,
pageSize: 10,

get pageStart() { return (this.page - 1) * this.pageSize; },
get totalPages() { return Math.max(1, Math.ceil(this.sorted.length / this.pageSize)); },
get paged() { return this.sorted.slice(this.pageStart, this.pageStart + this.pageSize); },

init() {
  this.$watch('search', () => { this.page = 1; });
  this.$watch('activeFilters', () => { this.page = 1; });
}
```

The `$watch` calls reset `page` to 1 when search or filters change, preventing empty pages after narrowing results.

## Toast notifications

Transient feedback messages that auto-dismiss. Fixed to bottom-right.

```html
<div class="fixed bottom-4 right-4 z-50 space-y-2 no-print" aria-live="polite">
  <template x-for="toast in toasts" :key="toast.id">
    <div x-show="toast.visible"
         x-transition:enter="transition ease-out duration-200"
         x-transition:enter-start="opacity-0 translate-y-2"
         x-transition:enter-end="opacity-100 translate-y-0"
         x-transition:leave="transition ease-in duration-150"
         x-transition:leave-start="opacity-100"
         x-transition:leave-end="opacity-0 translate-y-2"
         :class="{
           'bg-emerald-900/80 border-emerald-700 text-emerald-200': toast.type === 'success',
           'bg-red-900/80 border-red-700 text-red-200': toast.type === 'error',
           'bg-zinc-800/90 border-zinc-600 text-zinc-200': toast.type === 'info'
         }"
         class="flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg backdrop-blur-sm text-sm max-w-sm">
      <span x-text="toast.message"></span>
      <button @click="dismissToast(toast.id)" class="text-current opacity-60 hover:opacity-100 ml-auto">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
  </template>
</div>
```

Alpine data:

```js
toasts: [],
_toastId: 0,

showToast(message, type = 'info', duration = 3000) {
  const id = ++this._toastId;
  this.toasts.push({ id, message, type, visible: true });
  setTimeout(() => this.dismissToast(id), duration);
},

dismissToast(id) {
  const toast = this.toasts.find(t => t.id === id);
  if (toast) toast.visible = false;
  setTimeout(() => {
    this.toasts = this.toasts.filter(t => t.id !== id);
  }, 200);
}
```

Usage: `this.showToast('CSV exported', 'success')`. Three types: `success`, `error`, `info`. Default 3-second auto-dismiss.
