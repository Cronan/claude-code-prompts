# Chart selection and dashboard composition

How to reason about which visualizations to use and how to compose them into dashboards. The SKILL.md "Choosing visualizations" section covers the quick-reference routing table. This file covers the deeper reasoning: dashboard composition patterns, analytical rationale behind the example artifacts, and visualization anti-patterns.

-----

## Dashboard composition patterns

Most dashboards follow one of four structural patterns. Identify which pattern fits the user's goal before selecting individual chart types.

### KPI monitor

**Goal:** Track operational health at a glance. The audience checks frequently and wants instant answers to "is anything wrong?"

**Structure:**
- Stat cards at top showing current values with trend indicators (+/-%)
- One or two time-series charts (line or area) showing the primary metric over time
- A table of items below with status badges, sortable columns, and optional sparklines
- Cross-filtering: click a status badge or chart region to filter the table

**Chart choices:** Line/area for trends. Stat cards for current values. Sparklines in table cells for per-item trends. Gauge only for a single hero metric (e.g., uptime percentage).

**When to use:** Server monitoring, sales dashboards, project health trackers, fleet management.

**Example in this repo:** `examples/example-dashboard.html` -- system monitor with CPU/memory/network charts, service table with sparklines, cross-filtering by status.

### Analytical explorer

**Goal:** Let the user investigate data by slicing, filtering, and drilling down. The audience has questions they want to answer themselves.

**Structure:**
- Tabs organizing different analytical angles (e.g., by geography, by time, by category)
- Multiple chart types per tab, each showing a different dimension of the same data
- Cross-filtering between charts: click a chart element to filter others
- Tables with sort and search for finding specific items
- Detail panel (drawer) for inspecting individual records

**Chart choices:** Diverse -- match chart type to each analytical dimension. Use treemap for composition, scatter for relationships, bar for comparison, line for trends. Different tabs can use different chart types.

**When to use:** Economic analysis, product analytics, research data exploration, financial reporting.

**Example in this repo:** `examples/example-gdp-analysis.html` -- GDP data explored through composition (treemap), correlation (scatter), multi-dimensional comparison (radar), temporal trends (area), and workforce distribution (stacked bar).

### Overview + detail

**Goal:** Provide a summary first, then let the user drill into specifics. The audience ranges from executives who skim to analysts who dig.

**Structure:**
- Top section: 3-5 stat cards with key metrics
- Middle section: one or two charts showing the most important trends or breakdowns
- Bottom section: full data table with search, sort, filter, pagination
- Click-to-expand: table rows open a detail drawer or expand inline

**Chart choices:** Pick 1-2 chart types that answer the primary question. Do not fill the page with charts. The table carries the detail.

**When to use:** Inventory management, customer lists, team performance reviews, content catalogs.

### Narrative report

**Goal:** Tell a story with data. The audience reads top-to-bottom and reaches a conclusion.

**Structure:**
- Linear scroll (no tabs)
- Sections with headings, each containing one chart and a text summary
- Charts are sized large enough to be the focus of each section
- Minimal interactivity: tooltips and dataZoom, but not cross-filtering
- Print stylesheet is important -- this may be shared as a PDF

**Chart choices:** Fewer chart types, used consistently. Waterfall for financial walk-through. Line for trend narrative. Bar for comparison evidence. Avoid exotic types that need explanation.

**When to use:** Board reports, quarterly reviews, research summaries, investment memos.

-----

## Analytical rationale for example artifacts

### Chart showcase (`examples/example-chart-showcase.html`)

**Purpose:** Demonstrate the range of available chart types, not analytical reasoning. This is a reference gallery, not a dashboard.

**Why these groupings:**
- Line, area, bar, pie are fundamental types every dashboard user recognizes. They appear first.
- Radar, scatter, heatmap show relationship and distribution analysis -- the next level of complexity.
- Treemap, sunburst, sankey, funnel are specialized types for specific data shapes (hierarchical, flow, sequential). They appear last because they apply to narrower use cases.

**What this teaches:** The range of the toolkit. When a user requests a specific chart type by name, this example shows the correct configuration. It does not teach when to choose between types.

### System monitor (`examples/example-dashboard.html`)

**Purpose:** Demonstrate the KPI monitor pattern with full interactivity.

**Analytical reasoning behind the composition:**
- **Stat cards** (CPU, memory, network, services) answer "what are the current values?" Trend arrows answer "are things getting better or worse?" These two questions dominate operational monitoring.
- **Time-series area charts** answer "what happened over the last N hours?" Area fill (not just line) emphasizes volume, which maps to resource utilization.
- **Service table with sparklines** answers "which specific services have problems?" The sparkline in each row shows per-service trends without requiring a separate chart per service. This is more compact than small multiples for 10+ services.
- **Cross-filtering by status** answers "show me only the services that are in error state." This is the interaction that separates a dashboard from a report -- the user narrows focus.
- **Synced crosshairs** across the CPU and memory charts answer "when CPU spiked, did memory spike too?" Temporal correlation requires linked tooltips.

**Why not other chart types:** Gauges were not used for CPU/memory because the time dimension matters more than the instantaneous value. A gauge shows one number; the area chart shows the last 24 hours. Radar was not used because the metrics (CPU, memory, network) are not comparable dimensions of the same entity -- they have different units and scales. Pie was not used because there is no part-to-whole relationship.

### GDP analysis (`examples/example-gdp-analysis.html`)

**Purpose:** Demonstrate the analytical explorer pattern with economic data.

**Analytical reasoning behind the composition:**
- **Tab 1 (Overview):** Treemap for sectoral GDP composition. Treemap was chosen over pie because there are 10+ sectors -- pie becomes unreadable past 6 slices. Treemap shows both the value (area) and the hierarchy (nested rectangles) simultaneously. A stacked bar would work for composition but loses the hierarchical nesting.
- **Tab 2 (Sectors):** Bar chart for cross-sector comparison. Horizontal bars because sector names are long. Sorted by value so the ranking is visible. This is the most direct answer to "which sectors are largest?"
- **Tab 3 (Correlation):** Scatter plot showing GDP vs. growth rate per sector. This answers "are larger sectors growing faster or slower?" -- a relationship question that only scatter can answer. Bubble size encodes employment, adding a third dimension.
- **Tab 4 (Multi-dimensional):** Radar chart comparing 3-4 sectors across multiple metrics (GDP, growth, employment, productivity). Radar works here because the dimensions are normalized to comparable scales and there are few enough items (3-4) to distinguish the polygons.
- **Tab 5 (Workforce):** Stacked bar chart showing employment distribution across sectors over time. This answers a composition-over-time question. Stacked area could also work but bar is clearer when exact period comparisons matter.

**Why tabs instead of one long scroll:** Each tab answers a different analytical question. An economist looks at composition (tab 1), comparison (tab 2), correlation (tab 3), and workforce (tab 5) as separate investigations. Putting them all on one page would dilute focus. Tabs force single-question-per-view discipline.

-----

## Visualization anti-patterns

Mistakes that undermine trust in the data or confuse the audience.

### Chart type mismatches

- **Pie chart with 10+ slices.** Past 6, slices become indistinguishable. Use a horizontal bar chart or treemap instead.
- **Radar chart with 2 or fewer dimensions.** A radar with 2 axes is a distorted bar chart. Use a grouped bar chart.
- **Radar chart with 10+ dimensions.** The polygon becomes unreadable. Use parallel coordinates.
- **Area chart with 4+ overlapping series.** Later series obscure earlier ones. Use small multiples or stacked area (if part-to-whole).
- **Dual-axis chart for same-unit metrics.** Dual axes are justified only when units differ (price vs. volume, temperature vs. humidity). Two metrics with the same unit should share one axis -- or use two separate charts.
- **3D effects on any chart.** 3D bars, 3D pie, perspective distortion. These reduce accuracy and add no information. ECharts supports 3D; do not use it for data dashboards.
- **Stacked bar with negative values.** The stacking arithmetic breaks when values go negative. Use a grouped bar chart or a waterfall.

### Axis and scale mistakes

- **Non-zero baseline on bar charts.** Truncating the y-axis exaggerates differences. Bar height encodes value; if the axis starts at 90, a bar at 95 looks 5x taller than one at 91. Always start bar chart y-axes at 0.
- **Inconsistent scales in small multiples.** If each mini-chart auto-scales its y-axis, a small variation in one chart looks the same as a large swing in another. Share the y-axis range across all panels, or clearly label each axis.
- **Using `type: 'category'` for time data.** Category axes space all points equally. If your data has 2 points in January and 10 in March, a category axis hides the gap. Use `type: 'time'`.
- **Smooth curves on volatile data.** `smooth: true` invents intermediate values between data points. For data with sharp drops or spikes (server errors, stock prices), use straight lines so the actual trajectory is visible.

### Dashboard composition mistakes

- **Every chart gets equal size.** The primary insight should dominate the layout. Make the most important chart largest (full-width or 2/3 width). Supporting charts should be smaller.
- **Charts without context.** A line chart going up means nothing without: what metric, what time range, what the trend was before, what "good" looks like. Add stat cards for current value, trend indicators for direction, and markLine for targets or thresholds.
- **Too many charts per view.** More than 4-5 charts on a single screen (without scrolling) overwhelms the viewer. Use tabs to separate analytical questions, or collapse secondary charts into expandable sections.
- **No cross-filtering on a multi-chart dashboard.** If a dashboard has a pie chart and a table showing the same data, clicking the pie should filter the table. Independent charts on the same page are a missed opportunity. The cross-filtering pattern in the SKILL.md wires this up.
- **Choosing a chart for aesthetics, not data.** Sankey diagrams and sunbursts look impressive but are wrong for data that has no flow or hierarchy. A bar chart that answers the question is better than a sankey that looks complex.
