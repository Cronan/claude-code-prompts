---
name: jsx-artifact
description: |
  Build interactive single-file React artifacts: dashboards, trackers, data
  visualizations, planners, calculators, or any self-contained UI. Outputs
  either a .jsx file for a Vite renderer or a standalone .html file that
  opens directly in any browser. Trigger this when the user asks for a
  dashboard, tracker, chart, tool, widget, visualizer, planner, monitor,
  or any interactive UI component.
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

You build single-file React components. Each artifact is one file containing a complete interactive UI: data, components, and rendering in a single place.

## Environment detection

On first use, determine which output mode to use:

1. Look for a Vite+React renderer: check for `~/jsx-renderer/`, or a `package.json` with `react` and `vite` in the current project, or a running dev server.
2. If a renderer is found, use **renderer mode** (`.jsx` file with ES module imports).
3. If no renderer is found, use **standalone mode** (`.html` file with CDN-loaded scripts).
4. If you are unsure, ask the user.

The user can override at any time by asking for a specific format. Both modes use the same design tokens, component patterns, and Tailwind classes. The component code is nearly identical -- only the file shell differs.

-----

## Renderer mode

Use this when a Vite+React dev server is available. Produces a `.jsx` file.

### File shape

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

### Output location

Save to the renderer's artifacts directory. Common locations:
- `~/jsx-renderer/artifacts/`
- `./artifacts/`
- `./src/artifacts/`

On first use, check whether the expected directory exists. If not, ask the user where to save.

### Available libraries

The renderer may have these installed. Only import what the artifact needs. Before importing anything beyond `react`, verify the package exists (check `package.json` or `node_modules`). Stick to `react`, `recharts`, and `lucide-react` unless the user asks for something specific or you have confirmed availability.

| Package | Use for |
|---|---|
| react | Core. Always available. |
| recharts | Charts: line, bar, area, pie, radar, scatter |
| lucide-react | Icons: `Search`, `Menu`, `X`, `ChevronDown`, etc. |
| d3 | Custom data visualization beyond Recharts |
| lodash | Utility functions when native JS is awkward |
| mathjs | Math expressions, unit conversions, matrix operations |
| papaparse | CSV parsing |
| xlsx | Excel file reading/writing |
| three | 3D rendering (Three.js) |
| mammoth | .docx to HTML conversion |
| chart.js | Alternative charting library |
| tone | Audio synthesis and music |

-----

## Standalone mode

Use this when no renderer is available. Produces a `.html` file that opens directly in any browser. No Node.js, npm, or build step required.

### File shape

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Artifact Title</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Add only if needed: -->
  <!-- <script src="https://unpkg.com/recharts@2/umd/Recharts.js"></script> -->
  <!-- <script src="https://unpkg.com/lucide-react@latest/dist/umd/lucide-react.js"></script> -->
  <script>
    tailwind.config = { darkMode: "class" }
  </script>
</head>
<body class="bg-zinc-900 text-white min-h-screen">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useMemo, useEffect, useRef } = React;
    // If using Recharts: const { LineChart, Line, ... } = Recharts;
    // If using Lucide: const { Search, Menu, ... } = LucideReact;

    // ── Data ──────────────────────────────────────────────────

    const ITEMS = [
      { id: 1, name: "Alpha", value: 42 },
    ];

    // ── Components ────────────────────────────────────────────

    const App = () => {
      // ...
    };

    const root = ReactDOM.createRoot(document.getElementById("root"));
    root.render(<App />);
  </script>
</body>
</html>
```

Key differences from renderer mode:
- No `import` or `export` statements. Libraries are loaded via CDN `<script>` tags and accessed as globals (`React`, `Recharts`, `LucideReact`).
- Destructure hooks and library components from their global objects.
- The component is mounted with `ReactDOM.createRoot`, not exported.
- Do not load CDN scripts the artifact does not use.
- No TypeScript. Babel standalone handles JSX only.

### Tailwind CDN and dynamic classes

Tailwind's Play CDN scans the HTML for class names at runtime. Dynamically constructed class names that never appear as complete strings in the file will be missed. If you build class names from variables, include the full strings somewhere the CDN can find them:

```jsx
// Tailwind CDN safelist:
// bg-emerald-900/30 text-emerald-400 bg-red-900/30 text-red-400
const statusStyles = {
  active: "bg-emerald-900/30 text-emerald-400",
  error: "bg-red-900/30 text-red-400",
};
```

### Output location

Save standalone artifacts wherever the user requests. Reasonable defaults:
- The current working directory
- A `./artifacts/` subdirectory
- The user's home directory

Name files with kebab-case: `system-monitor.html`, `recipe-planner.html`.

-----

## Shared design rules

Everything below applies to both modes. The component code inside the file shell is identical.

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

When the user requests a light theme, use these tokens instead. The structure mirrors the dark theme exactly.

Background hierarchy:
- Page: `bg-white` or `bg-zinc-50`
- Card / panel: `bg-white` (with border) or `bg-zinc-50`
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

```jsx
<div className="min-h-screen bg-zinc-50 text-zinc-900">
  <div className="max-w-5xl mx-auto p-3 md:p-6">
    <h1 className="text-xl md:text-2xl font-bold mb-6">Title</h1>
    {/* content */}
  </div>
</div>
```

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
          <td className="px-4 py-3 text-zinc-300">{row.name}</td>
          <td className="px-4 py-3 text-zinc-300">{row.status}</td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
```

## Recharts

Always wrap in `ResponsiveContainer`. Match chart colors to the dark theme:

```jsx
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

Renderer mode import:
```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
```

Standalone mode global:
```jsx
const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } = Recharts;
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

- No `<artifact>` or `<antartifact>` wrapper tags.
- No `<form>` tags.
- No external API calls or `fetch`.
- No `localStorage` or `sessionStorage`.
- No external image URLs. Use Lucide icons (renderer mode), inline SVGs, or CSS-only graphics.
- No hover-only interactions without a tap/click alternative.
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
2. All data is hardcoded at the top and clearly structured for easy editing.
3. The layout works at mobile, tablet, and desktop widths.
4. Dark theme tokens are consistent (not mixing `zinc-900` page with `zinc-900` cards).
5. Interactive elements (tabs, filters, sort) work without requiring hover.
6. No unused imports or CDN scripts.
7. File is named with kebab-case.

## Reference files

Before building complex artifacts, read the reference material in this skill directory:

- Component layout patterns and recurring structures: `references/patterns.md`
- Tailwind dark theme tokens and spacing conventions: `references/tailwind-guide.md`
- Complete working examples: `examples/example-dashboard.jsx` (renderer mode), `examples/example-dashboard.html` (standalone mode)
