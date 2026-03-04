# Dashboard feature recipes

Implementation patterns for interactive dashboard features. Each section is self-contained. Use these when the user requests the specific feature or when the artifact complexity warrants it.

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
      Object.values(charts).forEach(c => c.resize());
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
Alpine.data('app', () => {
  let charts = {};
  return {
  selectedCategory: null,
  items: ITEMS,

  get filtered() {
    if (!this.selectedCategory) return this.items;
    return this.items.filter(i => i.category === this.selectedCategory);
  },

  init() {
    charts.pie = echarts.init(this.$refs.pieChart, 'zinc-dark');
    charts.pie.setOption({ /* ... */ });

    // Click a pie slice to filter everything else
    charts.pie.on('click', (params) => {
      this.selectedCategory = this.selectedCategory === params.name
        ? null  // click again to clear
        : params.name;
    });

    // Update dependent charts when filter changes
    this.$watch('filtered', () => this.updateBarChart());
  }
}; });
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
  charts.pie.dispatchAction({
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

## View-as-table toggle

Add a "View as table" toggle on chart cards so users can see the raw data. This is the most accessible way to present chart data and helps screen reader users:

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
        <template x-for="(val, i) in chartData" :key="i">
          <tr class="border-b border-zinc-700/50">
            <td class="px-3 py-2 text-zinc-300" x-text="labels[i]"></td>
            <td class="px-3 py-2 text-zinc-300 text-right" x-text="'$' + val.toLocaleString()"></td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</div>
```

Use nested `x-data` to keep the toggle state local to each card. The chart stays initialized (via `x-show`, not `x-if`) so switching back is instant.

For screen readers, the table view provides equivalent access to all data that the chart visualizes.

-----

## Color-blind mode toggle

Add a runtime toggle that swaps the ECharts color palette to a color-blind-safe set. This goes beyond the static palette guidance in the theme section:

```js
Alpine.data('app', () => {
  let charts = {};
  return {
  colorBlindMode: false,

  get palette() {
    return this.colorBlindMode
      ? ['#3b82f6', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']  // deuteranopia-safe
      : ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4']; // default
  },

  toggleColorBlind() {
    this.colorBlindMode = !this.colorBlindMode;
    // Re-apply palette to all charts
    Object.values(charts).forEach(c => {
      c.setOption({ color: this.palette });
    });
  }
}; });
```

Toggle button (place in the header):

```html
<button @click="toggleColorBlind()"
        :class="colorBlindMode ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 border border-zinc-700'"
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors no-print"
        aria-label="Toggle color-blind safe palette">
  <span x-text="colorBlindMode ? 'Standard palette' : 'Color-blind safe'"></span>
</button>
```

The deuteranopia-safe palette avoids the red-green pair that is indistinguishable to ~8% of males. When active, all charts update immediately via `setOption` merge. Pair with shape/style redundancy (dashed lines, different markers) for complete accessibility.

-----

## Sticky table header

Pin table column headers while scrolling long tables. Pure CSS, no JavaScript:

```html
<div class="overflow-auto max-h-[32rem]">
  <table class="w-full text-sm text-left">
    <thead class="sticky top-0 z-10 bg-zinc-900">
      <tr class="border-b border-zinc-700 text-zinc-400">
        <th class="px-4 py-3 font-medium">Name</th>
        <th class="px-4 py-3 font-medium">Status</th>
        <th class="px-4 py-3 font-medium">Value</th>
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

The outer `div` sets `overflow-auto` with a `max-h-[32rem]` (or any height that fits the layout). The `thead` uses `sticky top-0 z-10` with a solid background color matching the page. The `z-10` ensures headers stay above row hover backgrounds.

For dark/light toggle dashboards, use `bg-white dark:bg-zinc-900` on the `thead` to match the page background in both modes. If the table is inside a card (`bg-zinc-800`), use that card background on the `thead` instead.

Use sticky headers when the table has more than ~15 rows. For shorter tables, skip it -- the overhead is unnecessary and the sticky behavior can feel odd in small containers.

-----

## Detail panel / drawer

A slide-in side panel for showing item detail when a table row is clicked. More fluid than a modal for list-detail exploration patterns:

```html
<!-- Table row with click handler -->
<tr @click="selectedItem = row; drawerOpen = true"
    class="border-b border-zinc-700/50 hover:bg-zinc-800/50 cursor-pointer">
  <td class="px-4 py-3 text-zinc-300" x-text="row.name"></td>
  <td class="px-4 py-3 text-zinc-300" x-text="row.status"></td>
</tr>

<!-- Drawer overlay -->
<div x-show="drawerOpen" class="fixed inset-0 z-40"
     x-transition.opacity>
  <div class="absolute inset-0 bg-black/50" @click="drawerOpen = false"></div>
</div>

<!-- Drawer panel -->
<div :class="drawerOpen ? 'translate-x-0' : 'translate-x-full'"
     class="fixed top-0 right-0 z-50 h-full w-full max-w-md bg-zinc-800 border-l border-zinc-700
            shadow-xl transform transition-transform duration-200 overflow-y-auto">
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold" x-text="selectedItem?.name"></h2>
      <button @click="drawerOpen = false"
              class="text-zinc-400 hover:text-zinc-200 p-1"
              aria-label="Close detail panel">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Detail content -->
    <template x-if="selectedItem">
      <div class="space-y-4">
        <div>
          <p class="text-xs text-zinc-400 mb-1">Status</p>
          <p class="text-sm text-zinc-300" x-text="selectedItem.status"></p>
        </div>
        <div>
          <p class="text-xs text-zinc-400 mb-1">Value</p>
          <p class="text-sm text-zinc-300" x-text="selectedItem.value"></p>
        </div>
        <!-- Add more fields, mini-charts, related data -->
      </div>
    </template>
  </div>
</div>
```

Alpine state:

```js
drawerOpen: false,
selectedItem: null,
```

Wire Escape to close the drawer alongside other keyboard handlers:

```js
// In the @keydown.escape.window handler
drawerOpen = false;
```

The drawer slides in from the right with a CSS transform transition. The semi-transparent overlay behind it dims the page and closes the drawer on click. Use `max-w-md` (448px) for a standard width; use `max-w-lg` for dashboards with more detail fields.

For dark/light toggle dashboards, add `bg-white dark:bg-zinc-800` on the panel and `border-zinc-200 dark:border-zinc-700` on the border.

-----

## Multi-select filtering

Extend the filter chip pattern to allow selecting multiple values simultaneously. Users can toggle multiple statuses on/off rather than picking one at a time:

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

Alpine state and methods:

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

The "All" button clears the array. Each option chip toggles its presence in the `activeFilters` array. An empty array means "show everything" (no filter applied). The `filtered` getter checks if `activeFilters` is empty (show all) or if the item's status is in the active set.

For URL hash persistence, serialize as comma-separated: `#status=Active,Warning`. Parse back with `split(',')`.

-----

## Pagination

Page controls for tables with many rows. Prevents rendering hundreds of DOM nodes at once and keeps the interface scannable:

```html
<!-- Paginated table body -->
<tbody>
  <template x-for="row in paged" :key="row.id">
    <tr class="border-b border-zinc-700/50 hover:bg-zinc-800/50">
      <td class="px-4 py-3 text-zinc-300" x-text="row.name"></td>
      <td class="px-4 py-3 text-zinc-300" x-text="row.status"></td>
    </tr>
  </template>
</tbody>

<!-- Pagination controls -->
<div class="flex items-center justify-between mt-4 text-sm">
  <span class="text-zinc-400"
        x-text="'Showing ' + (pageStart + 1) + '-' + Math.min(pageStart + pageSize, sorted.length) + ' of ' + sorted.length"></span>
  <div class="flex items-center gap-1">
    <button @click="page = Math.max(1, page - 1)"
            :disabled="page === 1"
            :class="page === 1 ? 'text-zinc-600 cursor-not-allowed' : 'text-zinc-400 hover:text-zinc-200'"
            class="px-3 py-1.5 rounded border border-zinc-700 text-xs">
      Prev
    </button>
    <template x-for="p in totalPages" :key="p">
      <button @click="page = p"
              :class="page === p ? 'bg-blue-600 text-white' : 'text-zinc-400 hover:text-zinc-200'"
              class="px-3 py-1.5 rounded border border-zinc-700 text-xs min-w-[2rem]"
              x-text="p"></button>
    </template>
    <button @click="page = Math.min(totalPages, page + 1)"
            :disabled="page === totalPages"
            :class="page === totalPages ? 'text-zinc-600 cursor-not-allowed' : 'text-zinc-400 hover:text-zinc-200'"
            class="px-3 py-1.5 rounded border border-zinc-700 text-xs">
      Next
    </button>
  </div>
</div>
```

Alpine state and computed properties:

```js
page: 1,
pageSize: 10,

get pageStart() {
  return (this.page - 1) * this.pageSize;
},

get totalPages() {
  return Math.max(1, Math.ceil(this.sorted.length / this.pageSize));
},

get paged() {
  return this.sorted.slice(this.pageStart, this.pageStart + this.pageSize);
},
```

Reset page to 1 when filters change to avoid showing an empty page:

```js
this.$watch('search', () => { this.page = 1; });
this.$watch('activeFilters', () => { this.page = 1; });
```

For datasets under ~30 items, skip pagination and render the full list. Pagination adds interaction cost; only use it when the performance or readability benefit justifies it. For very large page counts (20+), show only a window of page numbers around the current page instead of all numbers.

-----

## Toast notifications

Transient feedback messages that auto-dismiss after a timeout. Use after actions like CSV export, clipboard copy, or filter reset:

```html
<!-- Toast container (fixed to bottom-right) -->
<div class="fixed bottom-4 right-4 z-50 space-y-2 no-print">
  <template x-for="toast in toasts" :key="toast.id">
    <div x-show="toast.visible"
         x-transition:enter="transition ease-out duration-200"
         x-transition:enter-start="opacity-0 translate-y-2"
         x-transition:enter-end="opacity-100 translate-y-0"
         x-transition:leave="transition ease-in duration-150"
         x-transition:leave-start="opacity-100 translate-y-0"
         x-transition:leave-end="opacity-0 translate-y-2"
         :class="{
           'bg-emerald-900/80 border-emerald-700 text-emerald-200': toast.type === 'success',
           'bg-red-900/80 border-red-700 text-red-200': toast.type === 'error',
           'bg-zinc-800/90 border-zinc-600 text-zinc-200': toast.type === 'info'
         }"
         class="flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg backdrop-blur-sm text-sm max-w-sm">
      <span x-text="toast.message"></span>
      <button @click="dismissToast(toast.id)"
              class="text-current opacity-60 hover:opacity-100 ml-auto flex-shrink-0">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
  </template>
</div>
```

Alpine state and methods:

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

Usage examples:

```js
// After CSV export
this.downloadCSV('data.csv', headers, rows);
this.showToast('CSV exported', 'success');

// After clearing filters
this.activeFilters = [];
this.showToast('Filters cleared', 'info');

// On error
this.showToast('Export failed', 'error', 5000);
```

Toasts stack vertically from the bottom-right corner. Each auto-dismisses after the specified duration (default 3 seconds). The two-phase dismiss (set `visible: false`, then remove from array after 200ms) allows the leave transition to play before the element is removed from the DOM.

Three types: `success` (green), `error` (red), `info` (neutral zinc). Keep toast messages short (under 40 characters). Do not use toasts for critical information that requires user action -- use an inline alert or modal instead.

-----
