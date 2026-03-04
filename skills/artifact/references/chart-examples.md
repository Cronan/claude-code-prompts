# Chart type examples

Complete ECharts option objects for chart types that need more than a `series.type` and data array. The core SKILL.md covers line, bar, area, pie, and scatter. This file covers everything else.

-----

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

**Waterfall** -- bridge chart showing cumulative effect of positive and negative values. Uses stacked bars with a transparent base series:

```js
{
  xAxis: {
    type: 'category',
    data: ['Q1 Revenue', 'COGS', 'Gross Profit', 'OpEx', 'Tax', 'Net Income']
  },
  yAxis: { type: 'value', axisLabel: { formatter: (v) => '$' + (v / 1e6).toFixed(0) + 'M' } },
  series: [
    {
      // Invisible base (creates the "floating" effect)
      type: 'bar', stack: 'waterfall', silent: true,
      itemStyle: { color: 'transparent', borderColor: 'transparent' },
      data: [0, 8000000, 0, 5200000, 4000000, 0]  // running total minus current bar
    },
    {
      // Visible bars
      type: 'bar', stack: 'waterfall',
      data: [
        { value: 12000000, itemStyle: { color: '#3b82f6' } },  // total: positive
        { value: -4000000, itemStyle: { color: '#ef4444' } },   // decrease
        { value: 8000000, itemStyle: { color: '#10b981' } },    // subtotal
        { value: -1200000, itemStyle: { color: '#ef4444' } },   // decrease
        { value: -1000000, itemStyle: { color: '#ef4444' } },   // decrease
        { value: 5800000, itemStyle: { color: '#10b981' } }     // final total
      ],
      label: {
        show: true, position: 'top',
        formatter: (p) => {
          const v = p.value;
          return (v < 0 ? '-' : '') + '$' + (Math.abs(v) / 1e6).toFixed(1) + 'M';
        }
      }
    }
  ]
}
```

The transparent base series shifts each bar vertically to create the waterfall stepping effect. Pre-compute the base values: for each bar, the base is the running total before that bar's contribution. Color positive values blue/green, negatives red, and subtotals/totals with a distinct accent.

**Calendar heatmap** -- daily values plotted on a calendar grid. Uses ECharts `calendar` component:

```js
{
  visualMap: {
    min: 0, max: 15, calculable: true,
    orient: 'horizontal', left: 'center', bottom: 0,
    inRange: { color: ['#27272a', '#3b82f6', '#10b981'] }
  },
  calendar: {
    range: '2024',
    cellSize: ['auto', 14],
    itemStyle: { borderWidth: 2, borderColor: '#18181b' },
    yearLabel: { color: '#a1a1aa' },
    monthLabel: { color: '#a1a1aa' },
    dayLabel: { color: '#71717a', firstDay: 1 },
    splitLine: { lineStyle: { color: '#3f3f46' } }
  },
  series: [{
    type: 'heatmap',
    coordinateSystem: 'calendar',
    data: generateCalendarData()  // [[date_string, value], ...]
  }]
}
```

Generate calendar data as `[['2024-01-01', 5], ['2024-01-02', 12], ...]`. The `calendar` component handles day-of-week layout, month boundaries, and label positioning. Use `cellSize: ['auto', 14]` for a compact GitHub-style contribution graph; increase to `['auto', 20]` for larger displays.

**Sunburst** -- radial hierarchy with drill-down. Click a sector to zoom into that subtree; click the center circle to zoom back out:

```js
{
  series: [{
    type: 'sunburst',
    data: [
      { name: 'Engineering', children: [
        { name: 'Backend', value: 600000, children: [
          { name: 'API', value: 300000 },
          { name: 'Database', value: 200000 },
          { name: 'Auth', value: 100000 }
        ]},
        { name: 'Frontend', value: 400000, children: [
          { name: 'Web App', value: 250000 },
          { name: 'Mobile', value: 150000 }
        ]},
        { name: 'Infra', value: 200000 }
      ]},
      { name: 'Product', children: [
        { name: 'Design', value: 250000 },
        { name: 'Research', value: 150000 }
      ]},
      { name: 'Operations', children: [
        { name: 'HR', value: 180000 },
        { name: 'Finance', value: 120000 }
      ]}
    ],
    radius: ['15%', '90%'],
    label: { fontSize: 11, color: '#d4d4d8' },
    itemStyle: { borderRadius: 4, borderWidth: 1, borderColor: '#18181b' },
    levels: [
      {},
      { r0: '15%', r: '40%', label: { fontSize: 12 } },
      { r0: '40%', r: '65%', label: { fontSize: 11 } },
      { r0: '65%', r: '90%', label: { fontSize: 10, position: 'outside' } }
    ]
  }]
}
```

Sunburst differs from treemap in that concentric rings show hierarchy depth at a glance. Use `levels` to control styling per ring. Leaf nodes without `children` must have a `value`; parent node values are auto-summed from children unless explicitly set.

**Graph/Network** -- force-directed node-link diagram. Nodes auto-position based on link weights:

```js
{
  series: [{
    type: 'graph',
    layout: 'force',
    roam: true,
    draggable: true,
    label: { show: true, color: '#d4d4d8', fontSize: 11 },
    force: { repulsion: 200, edgeLength: [80, 160], gravity: 0.1 },
    emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
    data: [
      { name: 'API Gateway', symbolSize: 40, category: 0 },
      { name: 'Auth Service', symbolSize: 30, category: 1 },
      { name: 'User Service', symbolSize: 30, category: 1 },
      { name: 'Order Service', symbolSize: 30, category: 1 },
      { name: 'PostgreSQL', symbolSize: 25, category: 2 },
      { name: 'Redis', symbolSize: 25, category: 2 }
    ],
    links: [
      { source: 'API Gateway', target: 'Auth Service', value: 1 },
      { source: 'API Gateway', target: 'User Service', value: 1 },
      { source: 'API Gateway', target: 'Order Service', value: 1 },
      { source: 'User Service', target: 'PostgreSQL', value: 1 },
      { source: 'Order Service', target: 'PostgreSQL', value: 1 },
      { source: 'Auth Service', target: 'Redis', value: 1 }
    ],
    categories: [
      { name: 'Gateway' },
      { name: 'Services' },
      { name: 'Data Stores' }
    ],
    lineStyle: { color: 'source', curveness: 0.1, opacity: 0.6 }
  }],
  legend: { data: ['Gateway', 'Services', 'Data Stores'] }
}
```

Use `layout: 'force'` for organic positioning or `layout: 'circular'` for a ring layout. Set `roam: true` for pan/zoom and `draggable: true` to let users reposition nodes. Node `symbolSize` should reflect importance (degree, traffic volume). Use `categories` for color grouping and `emphasis.focus: 'adjacency'` to highlight connected nodes on hover.

**Parallel coordinates** -- multi-dimensional comparison. Each vertical axis is a dimension:

```js
{
  parallelAxis: [
    { dim: 0, name: 'CPU Cores', min: 2, max: 64 },
    { dim: 1, name: 'RAM (GB)', min: 4, max: 256 },
    { dim: 2, name: 'Storage (TB)', min: 0.5, max: 10 },
    { dim: 3, name: 'Price ($/mo)', min: 50, max: 2000, inverse: true },
    { dim: 4, name: 'Benchmark', min: 1000, max: 50000 }
  ],
  parallel: { left: '5%', right: '13%', bottom: '10%', top: '8%' },
  series: [{
    type: 'parallel',
    lineStyle: { width: 2, opacity: 0.4 },
    emphasis: { lineStyle: { width: 3, opacity: 1 } },
    data: [
      [4, 16, 0.5, 120, 8500],
      [8, 32, 1, 280, 18000],
      [16, 64, 2, 550, 32000],
      [32, 128, 4, 1100, 42000],
      [64, 256, 8, 1900, 48000]
    ]
  }]
}
```

Use `inverse: true` on axes where lower is better (price, latency). Each data row is a polyline crossing all axes. Add `parallelAxis.areaSelectStyle` for brush selection to filter lines interactively. Parallel coordinates work best with 4-8 dimensions and 10-50 data points; beyond that, the lines become unreadable.

**ThemeRiver** -- centered streamgraph showing category volumes over time:

```js
{
  tooltip: { trigger: 'axis' },
  singleAxis: { type: 'time', bottom: 30, top: 50 },
  series: [{
    type: 'themeRiver',
    emphasis: { focus: 'self' },
    label: { show: true, color: '#d4d4d8', fontSize: 11 },
    data: [
      ['2024-01', 850, 'Python'],
      ['2024-01', 620, 'JavaScript'],
      ['2024-01', 410, 'TypeScript'],
      ['2024-01', 280, 'Rust'],
      ['2024-02', 900, 'Python'],
      ['2024-02', 580, 'JavaScript'],
      ['2024-02', 490, 'TypeScript'],
      ['2024-02', 320, 'Rust'],
      ['2024-03', 870, 'Python'],
      ['2024-03', 540, 'JavaScript'],
      ['2024-03', 560, 'TypeScript'],
      ['2024-03', 380, 'Rust']
      // ... continue for each date
    ]
  }]
}
```

Each data entry is `[date, value, categoryName]`. The river is centered vertically so the overall shape shows total volume while individual streams show category proportions. Use `emphasis.focus: 'self'` to highlight one stream on hover. Best for 3-8 categories over 6+ time points.

**Polar bar (Nightingale rose)** -- radial bar chart for cyclical data:

```js
{
  polar: { radius: ['10%', '80%'] },
  angleAxis: {
    type: 'category',
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    startAngle: 90
  },
  radiusAxis: { show: false },
  tooltip: { trigger: 'item' },
  series: [{
    type: 'bar',
    coordinateSystem: 'polar',
    data: [120, 98, 150, 180, 220, 280, 310, 295, 240, 190, 160, 130],
    itemStyle: { borderRadius: [4, 4, 0, 0] },
    label: { show: true, position: 'outside', formatter: '{c}', color: '#d4d4d8' }
  }]
}
```

The `angleAxis` maps categories (months, hours, directions) around the circle. The `radiusAxis` maps values outward from center. Set `radiusAxis.show: false` for a cleaner look. Use `startAngle: 90` to place the first category at 12 o'clock. For stacked polar bars, add `stack: 'total'` to each series. The radial layout naturally communicates cyclical patterns that a linear bar chart would not.

**Custom series (renderItem)** -- the foundation for chart types ECharts does not provide natively. The `renderItem` callback receives each data point and returns graphic elements to draw:

```js
{
  xAxis: { type: 'category', data: categories },
  yAxis: { type: 'value' },
  series: [{
    type: 'custom',
    renderItem: (params, api) => {
      // api.value(dimIndex) reads data dimensions
      // api.coord([x, y]) converts data values to pixel coordinates
      // api.size([dataWidth, dataHeight]) converts data units to pixel sizes
      const x = api.coord([api.value(0), 0])[0];
      const y = api.coord([0, api.value(1)])[1];
      const baseY = api.coord([0, 0])[1];
      const width = api.size([0, 1])[0] * 0.4;
      return {
        type: 'rect',
        shape: { x: x - width / 2, y, width, height: baseY - y },
        style: api.style({ fill: '#10b981' })
      };
    },
    data: values
  }]
}
```

The `renderItem` function runs once per data point. Return types: `'rect'`, `'circle'`, `'line'`, `'arc'`, `'polygon'`, `'polyline'`, `'text'`, `'image'`, or `'group'` (containing children). Use `'group'` to combine multiple elements for a single data point. The `api.style()` call inherits series color, opacity, and emphasis state from ECharts configuration.

**Bullet chart** -- horizontal bar showing actual vs target with qualitative range bands. A compact alternative to gauges for KPI dashboards:

```js
{
  yAxis: {
    type: 'category',
    data: ['Revenue', 'Profit', 'Satisfaction'],
    inverse: true
  },
  xAxis: { type: 'value', show: false },
  series: [
    // Qualitative ranges (background bands, widest first)
    {
      type: 'bar', barWidth: 30, barGap: '-100%', z: 1, silent: true,
      itemStyle: { color: 'rgba(16, 185, 129, 0.12)' },
      data: [150, 120, 100]   // "good" range max
    },
    {
      type: 'bar', barWidth: 30, barGap: '-100%', z: 2, silent: true,
      itemStyle: { color: 'rgba(16, 185, 129, 0.25)' },
      data: [120, 90, 80]     // "satisfactory" range max
    },
    // Actual value (narrow bar on top)
    {
      type: 'bar', barWidth: 12, barGap: '-100%', z: 3,
      itemStyle: { color: '#10b981' },
      data: [95, 78, 88],
      label: { show: true, position: 'right', color: '#d4d4d8', formatter: '{c}' }
    },
    // Target marker (vertical line via custom series)
    {
      type: 'custom', z: 4,
      renderItem: (params, api) => {
        const categoryIndex = api.value(0);
        const targetVal = api.value(1);
        const point = api.coord([targetVal, categoryIndex]);
        const halfHeight = 18;
        return {
          type: 'line',
          shape: { x1: point[0], y1: point[1] - halfHeight, x2: point[0], y2: point[1] + halfHeight },
          style: { stroke: '#f4f4f5', lineWidth: 2.5 }
        };
      },
      data: [[0, 100], [1, 85], [2, 90]]  // [categoryIndex, targetValue]
    }
  ]
}
```

Stack three `'bar'` series with `barGap: '-100%'` to overlay range bands. The narrower actual-value bar sits on top (higher `z`). The target marker uses a `'custom'` series that renders a short vertical line at the target position. Bullet charts are horizontally oriented by convention -- categories on the y-axis, values on the x-axis.

**Lollipop chart** -- dot on a stem, a bar chart with less visual weight. Effective for ranked lists where the exact value matters:

```js
{
  yAxis: {
    type: 'category',
    data: ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
    inverse: true
  },
  xAxis: { type: 'value', name: 'Score' },
  series: [{
    type: 'custom',
    renderItem: (params, api) => {
      const y = api.coord([0, api.value(0)])[1];
      const x = api.coord([api.value(1), 0])[0];
      const baseX = api.coord([0, 0])[0];
      return {
        type: 'group',
        children: [
          // Stem
          {
            type: 'line',
            shape: { x1: baseX, y1: y, x2: x, y2: y },
            style: { stroke: '#10b981', lineWidth: 2 }
          },
          // Dot
          {
            type: 'circle',
            shape: { cx: x, cy: y, r: 6 },
            style: { fill: '#10b981' }
          }
        ]
      };
    },
    data: [[0, 92], [1, 85], [2, 78], [3, 71], [4, 65]],  // [categoryIndex, value]
    label: {
      show: true, position: 'right', color: '#d4d4d8',
      formatter: (params) => params.value[1]
    }
  }],
  tooltip: {
    trigger: 'axis',
    formatter: (params) => params[0].name + ': ' + params[0].value[1]
  }
}
```

The `renderItem` returns a `'group'` with two children: a horizontal line (stem) from the axis baseline to the data point, and a circle (dot) at the data position. Horizontal orientation (categories on y-axis, values on x-axis) reads naturally for ranked lists. Set `inverse: true` on the y-axis so the highest-ranked item is at the top.

**Small multiples** -- a grid of identical mini-charts, one per category. Uses multiple ECharts `grid` components with paired axes in a single instance:

```js
// Data: one series per service
const services = ['API', 'Auth', 'DB', 'Cache', 'Queue', 'Search'];
const times = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'];
const trends = [
  [12, 10, 14, 22, 18, 15],
  [8, 6, 9, 14, 12, 10],
  [35, 32, 38, 45, 42, 40],
  [5, 4, 6, 8, 5, 4],
  [15, 12, 18, 25, 20, 16],
  [20, 18, 22, 30, 25, 21]
];

const cols = 3, rows = 2;
const cellW = 100 / cols, cellH = 100 / rows;
const pad = { left: 6, right: 2, top: 5, bottom: 5 };

const grid = [], xAxis = [], yAxis = [], series = [];
services.forEach((name, i) => {
  const col = i % cols, row = Math.floor(i / cols);
  grid.push({
    left: (col * cellW + pad.left) + '%',
    top: (row * cellH + pad.top) + '%',
    width: (cellW - pad.left - pad.right) + '%',
    height: (cellH - pad.top - pad.bottom) + '%'
  });
  xAxis.push({ type: 'category', data: times, gridIndex: i, show: row === rows - 1 });
  yAxis.push({ type: 'value', gridIndex: i, show: col === 0, name: name, nameLocation: 'middle', nameGap: 30 });
  series.push({
    type: 'line', data: trends[i], xAxisIndex: i, yAxisIndex: i,
    smooth: true, symbol: 'none',
    areaStyle: { opacity: 0.2 }
  });
});

// Pass to setOption:
{ grid, xAxis, yAxis, series, tooltip: { trigger: 'axis' } }
```

Each cell gets its own `grid`, `xAxis`, and `yAxis` with matching `gridIndex`. Only show axis labels on the left column and bottom row to avoid clutter. The `grid` array positions each mini-chart using percentage-based coordinates. This pattern scales to 4, 6, 9, or 12 cells -- beyond that, use a scrollable container or paginate.

### Gradient fills

Use `echarts.graphic.LinearGradient` for gradient area fills, bar fills, or line backgrounds:

```js
series: [{
  type: 'line',
  data: values,
  areaStyle: {
    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      { offset: 0, color: 'rgba(16, 185, 129, 0.4)' },
      { offset: 1, color: 'rgba(16, 185, 129, 0.02)' }
    ])
  }
}]
```

The four constructor arguments `(x1, y1, x2, y2, colorStops)` define the gradient direction. `(0, 0, 0, 1)` is top-to-bottom. `(0, 0, 1, 0)` is left-to-right.

For bar chart gradients:

```js
series: [{
  type: 'bar',
  data: values,
  itemStyle: {
    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      { offset: 0, color: '#3b82f6' },
      { offset: 1, color: '#1d4ed8' }
    ])
  }
}]
```

Use gradients sparingly. A single gradient area fill under a line chart improves visual depth. Applying gradients to every series in a multi-series chart creates visual noise.

### Decal patterns (accessibility)

Decal patterns add hatching or dots to chart areas, making series distinguishable without relying on color alone. This complements the color-blind palette toggle:

```js
series: [{
  type: 'bar',
  data: values,
  itemStyle: {
    decal: { symbol: 'rect', dashArrayX: 5, dashArrayY: 3, rotation: 0.8 }
  }
}]
```

Enable global decals for all series:

```js
chart.setOption({
  aria: {
    enabled: true,
    decal: { show: true }
  }
});
```

ECharts provides built-in decal patterns (`'circle'`, `'rect'`, `'roundRect'`, `'triangle'`, `'diamond'`) that auto-apply different patterns per series. The `aria.decal.show` approach is the simplest -- each series gets a distinct pattern automatically.

### Dataset component

The dataset component separates data from series configuration. This simplifies chart options and enables data transforms:

```js
const option = {
  dataset: {
    source: [
      ['product', 'Q1', 'Q2', 'Q3', 'Q4'],
      ['Widget A', 120, 132, 101, 134],
      ['Widget B', 220, 182, 191, 234],
      ['Widget C', 150, 232, 201, 154]
    ]
  },
  xAxis: { type: 'category' },
  yAxis: {},
  series: [
    { type: 'bar' },
    { type: 'bar' },
    { type: 'bar' },
    { type: 'bar' }
  ]
};
```

ECharts infers the mapping from dataset columns to series automatically. For explicit control, use `encode`:

```js
series: [{
  type: 'scatter',
  encode: { x: 'income', y: 'lifeExpectancy', tooltip: ['country', 'income', 'lifeExpectancy'] }
}]
```

Use dataset when multiple charts share the same data source or when you need transforms. For most single-chart dashboards, inline `data` arrays in each series are simpler and more readable.

**Dataset transforms** -- filter, sort, or aggregate data without preprocessing:

```js
dataset: [
  { source: rawData },
  {
    transform: {
      type: 'filter',
      config: { dimension: 'category', value: 'Electronics' }
    }
  },
  {
    transform: {
      type: 'sort',
      config: { dimension: 'revenue', order: 'desc' }
    }
  }
],
series: [
  { type: 'bar', datasetIndex: 1 },  // uses filtered data
  { type: 'line', datasetIndex: 2 }   // uses sorted data
]
```

Built-in transforms: `'filter'`, `'sort'`. The `ecStat` extension adds `'regression'`, `'histogram'`, and `'clustering'` transforms but requires an additional CDN script -- avoid for simple artifacts.

### Sparklines

Sparklines are tiny inline charts embedded in table cells that show a data trend without axes, labels, or chrome. Initialize an ECharts instance in a small container with all decorations stripped:

```js
initSparkline(el, data, color) {
  const chart = echarts.init(el, this.currentTheme, { width: 80, height: 24 });
  chart.setOption({
    animation: false,
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    xAxis: { show: false, type: 'category' },
    yAxis: { show: false, type: 'value', min: 0 },
    tooltip: { show: false },
    series: [{
      type: 'line', data: data, smooth: true, symbol: 'none',
      lineStyle: { width: 1.5, color: color },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
          { offset: 1, color: 'transparent' }
        ])
      }
    }]
  });
  return chart;
}
```

The table cell needs a fixed-size container:

```html
<td class="px-4 py-3">
  <div x-init="$nextTick(() => initSparkline($el, row.trend, '#10b981'))"
       style="width:80px;height:24px"></div>
</td>
```

Key constraints:
- `grid` with zero margins eliminates all padding around the chart
- `symbol: 'none'` hides data point dots that would clutter the tiny canvas
- `animation: false` avoids jarring entry effects on table render
- `min: 0` on yAxis anchors the baseline so all sparklines share visual scale
- Use `width` and `height` in `echarts.init` options, not CSS, for crisp rendering

Track sparkline instances for cleanup. When theme toggles or rows re-render, dispose all sparklines and re-create:

```js
_sparklines: {},

initSparkline(el, row) {
  const key = 'spark-' + row.id;
  if (this._sparklines[key]) this._sparklines[key].dispose();
  const chart = echarts.init(el, this.currentTheme, { width: 80, height: 24 });
  // ... setOption ...
  this._sparklines[key] = chart;
},

disposeSparklines() {
  Object.values(this._sparklines).forEach(c => c.dispose());
  this._sparklines = {};
}
```

Call `disposeSparklines()` before theme-toggle re-init. Alpine's `x-init` on each `<template x-for>` row handles re-creation automatically when the sorted/filtered list changes.

Color the sparkline to match the row's status (green for active, amber for warning, red for error) to reinforce meaning without needing a legend.

-----

