# Tailwind dark theme reference

Token reference for JSX artifacts. All artifacts default to dark mode. This guide covers the color system, spacing conventions, typography, and common utility patterns.

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

| Role      | Class            | When to use                      |
|-----------|------------------|----------------------------------|
| Primary   | `text-white`     | Headings, stat values, emphasis  |
| Body      | `text-zinc-300`  | Paragraphs, table cells          |
| Secondary | `text-zinc-400`  | Labels, descriptions, captions   |
| Muted     | `text-zinc-500`  | Placeholders, disabled text      |

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
| Small / caption | `text-xs text-zinc-500`              |
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

## Recharts theme tokens

Match chart chrome to the dark theme:

```jsx
// Grid and axes
<CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
<XAxis stroke="#71717a" fontSize={12} />
<YAxis stroke="#71717a" fontSize={12} />

// Tooltip
contentStyle={{
  backgroundColor: "#27272a",
  border: "1px solid #3f3f46",
  borderRadius: "8px",
  color: "#fafafa",
}}

// Line/bar colors (Tailwind 500-level hex values)
emerald:  #10b981
blue:     #3b82f6
violet:   #8b5cf6
amber:    #f59e0b
red:      #ef4444
cyan:     #06b6d4
```

## Platform performance notes

These artifacts may run on a Raspberry Pi with 1GB RAM and a 1024x600 screen. Keep things light:

- DOM node count matters. Paginate or virtualize lists longer than 50 items.
- CSS transitions are cheaper than JavaScript animation.
- `box-shadow` stacking and `backdrop-blur` on large surfaces are GPU-intensive. Use sparingly.
- Recharts renders well with under 100 data points. More than that causes visible lag on constrained hardware.
