# Tailwind and ECharts theme reference

Token reference for HTML artifacts. All artifacts default to dark mode. This guide covers the color system, spacing conventions, typography, common utility patterns, and ECharts theme configuration.

## Color system

### Backgrounds

| Surface          | Class              | When to use                        |
|------------------|--------------------|------------------------------------|
| Page             | `bg-zinc-900`      | Outermost container, body          |
| Card / panel     | `bg-zinc-800`      | Primary content containers         |
| Elevated surface | `bg-zinc-700`      | Modals, dropdowns, active tabs     |
| Input / well     | `bg-zinc-800/50`   | Text inputs, search bars           |
| Hover            | `bg-zinc-800/50`   | Table row hover, list item hover   |
| Tab container    | `bg-zinc-800`      | Tab bar background                 |
| Overlay          | `bg-black/50`      | Behind modals and drawers          |

### Text

| Role         | Class            | When to use                            |
|--------------|------------------|----------------------------------------|
| Primary      | `text-white`     | Headings, stat values, emphasis        |
| Body         | `text-zinc-300`  | Paragraphs, table cells, descriptions  |
| Labels       | `text-zinc-400`  | Card labels, column headers, captions  |
| Placeholders | `text-zinc-500`  | Input placeholders, disabled text only |

Do not use `text-zinc-500` for labels or visible captions. It fails WCAG AA contrast against `bg-zinc-800` (3.3:1, needs 4.5:1).

### Borders

| Context        | Class              |
|----------------|--------------------|
| Default        | `border-zinc-700`  |
| Subtle / inner | `border-zinc-700/50` |

### Accent colors

Use Tailwind's palette for semantic meaning. Pair gentle opacity backgrounds with the matching 400-level text:

| Meaning  | Base    | Background          | Text              |
|----------|---------|---------------------|-------------------|
| Success  | emerald | `bg-emerald-900/30` | `text-emerald-400`|
| Error    | red     | `bg-red-900/30`     | `text-red-400`    |
| Warning  | amber   | `bg-amber-900/30`   | `text-amber-400`  |
| Info     | cyan    | `bg-cyan-900/30`    | `text-cyan-400`   |
| Primary  | blue    | `bg-blue-600`       | `text-white`      |

Use `/30` opacity for status backgrounds. Use full-strength (`bg-blue-600`) only for primary action buttons.

## Light theme

When the user requests a light theme, swap tokens. Structure mirrors dark theme exactly.

### Light backgrounds

| Surface          | Class            |
|------------------|------------------|
| Page             | `bg-zinc-50`     |
| Card / panel     | `bg-white`       |
| Elevated surface | `bg-white`       |
| Input / well     | `bg-zinc-100`    |
| Tab container    | `bg-zinc-100`    |

### Light text

| Role         | Class            |
|--------------|------------------|
| Primary      | `text-zinc-900`  |
| Body         | `text-zinc-700`  |
| Labels       | `text-zinc-500`  |
| Placeholders | `text-zinc-400`  |

### Light borders

`border-zinc-200`

### Light accents

| Meaning  | Background       | Text               | Border              |
|----------|------------------|---------------------|---------------------|
| Success  | `bg-emerald-50`  | `text-emerald-700`  | `border-emerald-200`|
| Error    | `bg-red-50`      | `text-red-700`      | `border-red-200`    |
| Warning  | `bg-amber-50`    | `text-amber-700`    | `border-amber-200`  |
| Info     | `bg-cyan-50`     | `text-cyan-700`     | `border-cyan-200`   |
| Primary  | `bg-blue-600`    | `text-white`        | --                  |

## Spacing

Use the 4px grid. Mobile-first padding with responsive step-up.

| Token | Value | Common use                          |
|-------|-------|-------------------------------------|
| `1`   | 4px   | Tight gaps, tab container padding   |
| `2`   | 8px   | Icon-to-text gap, badge padding     |
| `3`   | 12px  | Mobile padding, compact card padding|
| `4`   | 16px  | Standard card padding, grid gaps    |
| `6`   | 24px  | Desktop padding, section spacing    |

Consistent spacing patterns:
- Page padding: `p-3 md:p-6`
- Card padding: `p-4`
- Grid gaps: `gap-3` (stats row) or `gap-4` (content grid)
- Stack spacing: `space-y-4` for stacked cards, `space-y-1` for nav items
- Inline spacing: `gap-2` for icon + text, `gap-3` for button groups
- Bottom margin after title: `mb-6`

## Typography

### Scale

| Element         | Classes                              |
|-----------------|--------------------------------------|
| Page title      | `text-xl md:text-2xl font-bold`      |
| Section heading | `text-lg font-bold`                  |
| Card label      | `text-sm text-zinc-400`              |
| Body            | `text-sm text-zinc-300`              |
| Stat value      | `text-2xl font-bold`                 |
| Stat trend      | `text-emerald-400 font-medium` (up) or `text-red-400 font-medium` (down) |
| Small / caption | `text-xs text-zinc-400`              |
| Mono / code     | `font-mono text-xs`                  |

Use `text-sm` as the base body size. Artifacts are information-dense.

### Font stack

Tailwind's default sans-serif stack works on all target platforms. Do not specify custom fonts.

## Common utility patterns

### Buttons

```
Primary:    bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors
Secondary:  bg-zinc-800 hover:bg-zinc-700 text-zinc-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-zinc-700
Ghost:      hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 px-3 py-2 rounded-lg text-sm transition-colors
Danger:     bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors
```

### Badges / tags

```
Default:  bg-zinc-700 text-zinc-300 px-2 py-0.5 rounded text-xs font-medium
Success:  bg-emerald-900/30 text-emerald-400 px-2 py-0.5 rounded text-xs font-medium
Error:    bg-red-900/30 text-red-400 px-2 py-0.5 rounded text-xs font-medium
Warning:  bg-amber-900/30 text-amber-400 px-2 py-0.5 rounded text-xs font-medium
Info:     bg-cyan-900/30 text-cyan-400 px-2 py-0.5 rounded text-xs font-medium
```

### Inputs

```
Text:     w-full px-3 py-2 bg-zinc-800/50 border border-zinc-700 rounded-lg text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500
Select:   same as text, add appearance-none and a chevron icon
```

### Transitions

```
Color:    transition-colors duration-150
All:      transition-all duration-200
Transform: transition-transform duration-200
```

Keep durations between 100ms and 200ms. Longer transitions feel sluggish on low-powered hardware.

### Cards

```
Standard: bg-zinc-800 rounded-xl p-4 border border-zinc-700
```

Use `rounded-xl` for cards, `rounded-lg` for buttons and inputs, `rounded-md` for tabs.

## ECharts zinc-dark theme

Register this theme before initializing any charts. It maps Tailwind's zinc palette to ECharts' internal styling:

```js
echarts.registerTheme('zinc-dark', {
  darkMode: true,
  backgroundColor: 'transparent',
  color: ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4'],
  textStyle: { color: '#d4d4d8' },
  title: {
    textStyle: { color: '#f4f4f5' },
    subtextStyle: { color: '#a1a1aa' }
  },
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
```

### Color mapping

| ECharts property | Tailwind token | Hex |
|---|---|---|
| `backgroundColor` | transparent | Chart inherits card background via CSS |
| `textStyle.color` | zinc-300 | `#d4d4d8` |
| `title.textStyle.color` | zinc-100 | `#f4f4f5` |
| `title.subtextStyle.color` | zinc-400 | `#a1a1aa` |
| `legend.textStyle.color` | zinc-400 | `#a1a1aa` |
| `tooltip.backgroundColor` | zinc-800 | `#27272a` |
| `tooltip.borderColor` | zinc-700 | `#3f3f46` |
| `axisLine.lineStyle.color` | zinc-700 | `#3f3f46` |
| `axisLabel.color` | zinc-400 | `#a1a1aa` |
| `splitLine.lineStyle.color` | zinc-800 | `#27272a` |

### Series colors (Tailwind 500-level hex)

| Color   | Hex       |
|---------|-----------|
| emerald | `#10b981` |
| blue    | `#3b82f6` |
| violet  | `#8b5cf6` |
| amber   | `#f59e0b` |
| red     | `#ef4444` |
| cyan    | `#06b6d4` |

These appear in the theme's `color` array. ECharts assigns them to series in order. Override per-series with `itemStyle: { color: '#hex' }` if needed.

## Tailwind CDN safelist

Tailwind's Play CDN generates styles at runtime by scanning the HTML for class names. Dynamically constructed class names that never appear as complete strings will be missed. If you build class names from variables, include the full strings somewhere the CDN can find them:

```html
<!-- Tailwind CDN safelist:
  bg-emerald-900/30 text-emerald-400 bg-red-900/30 text-red-400
  bg-amber-900/30 text-amber-400 bg-zinc-700 text-zinc-300
-->
```

Place this as an HTML comment in the body. The CDN scanner finds the class strings and generates the corresponding CSS.

## Platform performance notes

These artifacts may run on a Raspberry Pi with 1GB RAM and a 1024x600 screen. Keep things light:

- DOM node count matters. Paginate or virtualize lists longer than 50 items.
- CSS transitions are cheaper than JavaScript animation.
- `box-shadow` stacking and `backdrop-blur` on large surfaces are GPU-intensive. Use sparingly.
- ECharts: disable animation with `animation: false` for Pi-targeted dashboards.
- ECharts: use the SVG renderer (`{ renderer: 'svg' }`) for dashboards with many small charts.
- ECharts: keep datasets under 500 points per series. Use `sampling: 'lttb'` for larger datasets.
- Keep transition durations at 100-200ms. Longer durations feel sluggish on weak hardware.
