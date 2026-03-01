---
name: jsx-artifact
description: |
  Build interactive single-file React artifacts: dashboards, trackers, data
  visualizations, planners, calculators, or any self-contained UI. Produces
  a .jsx file styled with Tailwind CSS that renders in a local Vite dev
  server. Trigger this when the user asks for a dashboard, tracker, chart,
  tool, widget, visualizer, planner, monitor, or any interactive UI component.
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

# Build a JSX artifact

You build single-file React components. Each artifact is one `.jsx` file that renders in a local Vite+React dev server. The user opens a browser and sees the result. No separate build step.

## File shape

Every artifact follows this structure:

```jsx
import { useState } from "react";
// Other imports as needed: recharts, lucide-react, d3, etc.

// ── Data ────────────────────────────────────────────────────
// Hardcoded mock data at the top. Structured so the user can
// easily find and edit values.

const ITEMS = [
  { id: 1, name: "Alpha", value: 42 },
  { id: 2, name: "Beta", value: 87 },
];

// ── Helper components ───────────────────────────────────────

const StatusBadge = ({ status }) => {
  // ...
};

// ── Main ────────────────────────────────────────────────────

export default function App() {
  const [tab, setTab] = useState("overview");
  // ...
}
```

Key points:
- Standard ES module `import` / `export default` syntax.
- One default export: the `App` component.
- Helper components defined above `App` in the same file.
- Hardcoded data as named constants near the top, clearly separated, easy to edit.

## Output location

Save artifacts to `~/jsx-renderer/artifacts/` unless the user specifies a different path. On first use, check whether this directory exists. If not, ask the user where their renderer artifacts folder is.

Name files with kebab-case: `fitness-tracker.jsx`, `recipe-planner.jsx`, `system-monitor.jsx`.

## Available libraries

The renderer environment may include these packages. Only import what the artifact actually needs. Not all may be installed -- if a library is missing, the renderer will show an error. Stick to `react`, `recharts`, and `lucide-react` unless the user asks for something specific.

| Package | Use for |
|---|---|
| react | Core. Always available. |
| recharts | Charts: line, bar, area, pie, radar, scatter |
| lucide-react | Icons. Hundreds available: `Search`, `Menu`, `X`, `ChevronDown`, etc. |
| d3 | Custom data visualization beyond what Recharts covers |
| lodash | Utility functions when native JS is awkward |
| mathjs | Math expressions, unit conversions, matrix operations |
| papaparse | CSV parsing |
| xlsx | Excel file reading/writing |
| three | 3D rendering (Three.js, r128+) |
| mammoth | .docx to HTML conversion |
| chart.js | Alternative charting library |
| tone | Audio synthesis and music |

## Dark theme

Dark theme is the default. Design for dark first.

Background hierarchy:
- Page: `bg-zinc-900`
- Card / panel: `bg-zinc-800`
- Elevated surface: `bg-zinc-700`
- Input / well: `bg-zinc-800/50`

Text hierarchy:
- Primary: `text-white`
- Body: `text-zinc-300`
- Secondary: `text-zinc-400`
- Muted / labels: `text-zinc-500`

Borders: `border-zinc-700`

Accent colors:
- Success / positive: `emerald` -- `bg-emerald-900/30 text-emerald-400`
- Error / negative: `red` -- `bg-red-900/30 text-red-400`
- Warning: `amber` -- `bg-amber-900/30 text-amber-400`
- Primary action: `blue` -- `bg-blue-600 hover:bg-blue-500 text-white`
- Info / cool: `cyan` -- `bg-cyan-900/30 text-cyan-400`

Use gentle opacity backgrounds (`bg-emerald-900/30`) for status badges and category indicators. Full-strength backgrounds (`bg-blue-600`) for primary action buttons only.

## Layout

Standard page shell:

```jsx
<div className="min-h-screen bg-zinc-900 text-white">
  <div className="max-w-5xl mx-auto p-3 md:p-6">
    <h1 className="text-xl md:text-2xl font-bold mb-6">Title</h1>
    {/* content */}
  </div>
</div>
```

Use `max-w-5xl` as the default content width. Use `p-3 md:p-6` for mobile-first padding.

Grid patterns:
- Stats row: `grid grid-cols-2 md:grid-cols-4 gap-3`
- Two-column: `grid grid-cols-1 md:grid-cols-2 gap-4`
- Three-column: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`

## Tabs

Use pill-style tabs inside a container:

```jsx
<div className="flex gap-1 bg-zinc-800 rounded-lg p-1">
  {tabs.map(t => (
    <button
      key={t}
      onClick={() => setTab(t)}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
        tab === t
          ? "bg-zinc-700 text-white"
          : "text-zinc-400 hover:text-zinc-200"
      }`}
    >
      {t}
    </button>
  ))}
</div>
```

## Cards

```jsx
<div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
  <h3 className="text-sm text-zinc-400 mb-1">Label</h3>
  <p className="text-2xl font-bold">Value</p>
</div>
```

For stat cards showing trends:

```jsx
<p className="text-emerald-400 font-medium">+12%</p>
<p className="text-red-400 font-medium">-3%</p>
```

## Tables

Wrap in `overflow-x-auto` for small screens:

```jsx
<div className="overflow-x-auto">
  <table className="w-full text-sm text-left">
    <thead>
      <tr className="border-b border-zinc-700 text-zinc-400">
        <th className="px-4 py-3 font-medium">Name</th>
        <th className="px-4 py-3 font-medium">Status</th>
      </tr>
    </thead>
    <tbody>
      {data.map(row => (
        <tr key={row.id} className="border-b border-zinc-700/50 hover:bg-zinc-800/50">
          <td className="px-4 py-3">{row.name}</td>
          <td className="px-4 py-3">{row.status}</td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
```

## Recharts

Always wrap in `ResponsiveContainer`. Match chart colors to the dark theme:

```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

<div className="h-64">
  <ResponsiveContainer width="100%" height="100%">
    <LineChart data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
      <XAxis dataKey="name" stroke="#71717a" fontSize={12} />
      <YAxis stroke="#71717a" fontSize={12} />
      <Tooltip
        contentStyle={{
          backgroundColor: "#27272a",
          border: "1px solid #3f3f46",
          borderRadius: "8px",
          color: "#fafafa",
        }}
      />
      <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} dot={false} />
    </LineChart>
  </ResponsiveContainer>
</div>
```

Chart line colors (Tailwind 500-level hex):
- emerald: `#10b981`
- blue: `#3b82f6`
- violet: `#8b5cf6`
- amber: `#f59e0b`
- red: `#ef4444`
- cyan: `#06b6d4`

## Interactivity

Use `useState` for all interactive state: active tabs, search queries, sort keys, expanded sections, selected items.

Use `useMemo` when filtering or sorting data based on state.

Common patterns:
- Tabs: `useState` for active tab, conditional rendering per tab
- Search: controlled input + `useMemo` filtering
- Sort: `useState` for key and direction, toggle on header click
- Expandable: `useState` boolean, chevron rotation with `transition-transform`

Never rely on hover-only interactions. Touch devices have no hover state. Pair hover effects with click/tap handlers or visible controls.

No `<form>` tags. Use `onClick` and `onChange` handlers directly.

## Data

All data is hardcoded at the top of the file. Make it realistic and internally consistent. Structure it so the user can easily find and replace values:

```jsx
// ── Data ────────────────────────────────────────────────────
// Edit these arrays to change what the dashboard displays.

const SENSORS = [
  { id: "temp-1", label: "Living Room", value: 21.3, unit: "C" },
  { id: "temp-2", label: "Garage", value: 14.8, unit: "C" },
];
```

Do not fetch from external APIs. Do not use `localStorage` or `sessionStorage`. Session state (tab selection, search query, expanded panels) is fine.

## What not to do

- No `<artifact>` or `<antartifact>` wrapper tags. Just the JSX.
- No `<form>` tags.
- No external API calls or `fetch`.
- No `localStorage` or `sessionStorage`.
- No external image URLs. Use Lucide icons, inline SVGs, or CSS-only graphics.
- No hover-only interactions without a tap/click alternative.
- No TypeScript syntax unless the renderer is configured for it.
- No class components. Functional components with hooks only.

## Responsiveness

Design mobile-first. Three breakpoints: default (mobile), `md:` (tablet), `lg:` (desktop).

The artifact must not break on:
- 1024x600 (common Raspberry Pi display)
- 375px wide (phone)
- 1920px wide (desktop)

Use `overflow-x-auto` on tables and wide content. Avoid fixed widths. Use percentage or `max-w-` constraints.

## Platform constraints

The artifact runs in a browser on any platform: desktop Linux, Raspberry Pi, macOS, Windows. For low-powered hardware:

- Keep DOM node count low. Paginate or virtualize long lists instead of rendering hundreds of items.
- Prefer CSS transitions over JavaScript animation.
- Avoid stacking `box-shadow` and heavy `backdrop-blur` on large surfaces.
- Keep Recharts datasets under 100 data points.
- Avoid `requestAnimationFrame` loops unless the artifact is explicitly a visualization or game.

## Quality checklist

Before saving the file, verify:

1. The component renders without errors (no missing imports, no undefined references).
2. All data is hardcoded at the top and clearly structured.
3. The layout works at mobile, tablet, and desktop widths.
4. Dark theme tokens are consistent (not mixing `zinc-900` page with `zinc-900` cards).
5. Interactive elements (tabs, filters, sort) work without requiring hover.
6. No unused imports.
7. File is named with kebab-case and `.jsx` extension.

## Reference files

Before building complex artifacts, read the reference material in this skill directory:

- Component layout patterns and recurring structures: `references/patterns.md`
- Tailwind dark theme tokens and spacing conventions: `references/tailwind-guide.md`
- Complete working example: `examples/example-dashboard.jsx`
