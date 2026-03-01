# Tailwind dark theme reference

Token reference for JSX artifacts. All artifacts default to dark mode. This guide covers the color system, spacing conventions, and common utility patterns.

## Color system

### Backgrounds

| Surface          | Class                | When to use                        |
|------------------|----------------------|------------------------------------|
| Page             | `bg-zinc-950`        | Document body, outermost container |
| Card / panel     | `bg-zinc-900`        | Primary content containers         |
| Elevated surface | `bg-zinc-800`        | Modals, dropdowns, popovers       |
| Input / well     | `bg-zinc-800/50`     | Text inputs, search bars, insets   |
| Hover            | `bg-zinc-800/30`     | Table row hover, list item hover   |
| Active / pressed | `bg-zinc-700/50`     | Active nav item, pressed button    |
| Overlay          | `bg-black/50`        | Behind modals and drawers          |

### Text

| Role      | Class            | When to use                   |
|-----------|------------------|-------------------------------|
| Primary   | `text-zinc-100`  | Headings, body text, values   |
| Secondary | `text-zinc-400`  | Labels, descriptions, captions|
| Muted     | `text-zinc-500`  | Placeholders, disabled text   |
| Inverse   | `text-zinc-950`  | Text on light accent buttons  |
| On accent | `text-white`     | Text on colored backgrounds   |

### Borders

| Context        | Class                  |
|----------------|------------------------|
| Default        | `border-zinc-800`      |
| Subtle         | `border-zinc-700/50`   |
| Focus ring     | `ring-zinc-600`        |
| Accent focus   | `ring-blue-500/50`     |

### Accent colors

Use Tailwind's standard palette for semantic meaning:

| Meaning  | Base color  | Background          | Text              | Border               |
|----------|-------------|---------------------|-------------------|----------------------|
| Primary  | blue        | `bg-blue-500/20`    | `text-blue-400`   | `border-blue-500/30` |
| Success  | emerald     | `bg-emerald-500/20` | `text-emerald-400`| `border-emerald-500/30` |
| Warning  | amber       | `bg-amber-500/20`   | `text-amber-400`  | `border-amber-500/30`|
| Error    | red         | `bg-red-500/20`     | `text-red-400`    | `border-red-500/30`  |
| Info     | violet      | `bg-violet-500/20`  | `text-violet-400` | `border-violet-500/30` |

The `/20` and `/30` opacity modifiers keep accent backgrounds subtle against dark surfaces.

## Spacing

Use the 4px grid. Standard spacing values in Tailwind:

| Token | Value | Common use                     |
|-------|-------|--------------------------------|
| `1`   | 4px   | Tight gaps between inline items|
| `2`   | 8px   | Icon-to-text gap, badge padding|
| `3`   | 12px  | Compact card padding           |
| `4`   | 16px  | Standard card padding, gaps    |
| `6`   | 24px  | Page padding, section spacing  |
| `8`   | 32px  | Large section gaps             |

Consistent spacing patterns:
- Card padding: `p-4` (standard) or `p-3` (compact)
- Page padding: `p-6`
- Grid gaps: `gap-4` (standard) or `gap-3` (compact)
- Stack spacing: `space-y-4` for stacked cards, `space-y-1` for nav items
- Inline spacing: `gap-2` for icon + text, `gap-3` for button groups

## Typography

### Scale

| Element         | Classes                          |
|-----------------|----------------------------------|
| Page title      | `text-lg font-semibold`          |
| Section heading | `text-sm font-medium text-zinc-400` |
| Body            | `text-sm`                        |
| Small / caption | `text-xs text-zinc-500`          |
| Large number    | `text-2xl font-semibold`         |
| Mono / code     | `font-mono text-xs`              |

Use `text-sm` as the base size. Artifacts are information-dense; larger type wastes space.

### Font stack

Tailwind's default sans-serif stack works on all target platforms. Do not specify custom fonts -- they require additional CDN loads and may not render on all devices.

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
Default:  bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded text-xs font-medium
Success:  bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-xs font-medium
Error:    bg-red-500/20 text-red-400 px-2 py-0.5 rounded text-xs font-medium
```

### Inputs

```
Text:     w-full px-3 py-2 bg-zinc-800/50 border border-zinc-700/50 rounded-lg text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600
Select:   same as text, add appearance-none and a chevron SVG
```

### Transitions

```
Color:    transition-colors duration-150
All:      transition-all duration-200
Scale:    transition-transform duration-150 hover:scale-105
Opacity:  transition-opacity duration-200
```

Keep durations between 100ms and 200ms. Longer transitions feel sluggish, especially on low-powered hardware.

### Scrollable regions

```
Vertical:   overflow-y-auto max-h-[400px]
Horizontal: overflow-x-auto
Custom:     scrollbar-thin (if Tailwind scrollbar plugin is available; otherwise skip)
```

## Recharts theme tokens

When using Recharts, align chart colors with the Tailwind palette:

```jsx
// Grid and axes
<CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
<XAxis tick={{ fill: '#71717a', fontSize: 12 }} />
<YAxis tick={{ fill: '#71717a', fontSize: 12 }} />

// Tooltip
contentStyle={{
  backgroundColor: '#18181b',
  border: '1px solid #27272a',
  borderRadius: '8px',
  color: '#fafafa',
}}

// Line/bar colors (Tailwind 500-level hex values)
emerald:  #10b981
blue:     #3b82f6
violet:   #8b5cf6
amber:    #f59e0b
red:      #ef4444
cyan:     #06b6d4
```

## Performance notes for constrained devices

Tailwind's Play CDN generates styles at runtime by scanning the DOM. On a Raspberry Pi, this is fast enough for artifacts with a few hundred elements. For larger pages:

- Avoid deeply nested responsive variants (`lg:hover:focus:bg-zinc-800`). Each variant increases the CSS the CDN generates.
- Prefer static class strings over dynamic template literals where possible. The CDN scans the HTML for class names; dynamically constructed names that never appear as complete strings may be missed.
- If a class name is built dynamically, ensure the full string appears somewhere in the file (a comment or a constant) so the CDN can find it:

```jsx
// Ensure these classes are discoverable by Tailwind CDN:
// bg-emerald-500/20 text-emerald-400 bg-red-500/20 text-red-400 bg-amber-500/20 text-amber-400
const statusColors = {
  healthy: 'bg-emerald-500/20 text-emerald-400',
  error: 'bg-red-500/20 text-red-400',
  warning: 'bg-amber-500/20 text-amber-400',
};
```
