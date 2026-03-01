# Component patterns

Recurring layout and UI structures for JSX artifacts. Each pattern shows the minimal skeleton using the correct dark theme tokens. Combine them to build full artifacts.

Patterns below show renderer mode syntax (`import` / `export default`). For standalone mode, the component code is the same -- only the file shell differs. See the standalone shell pattern at the end of this file.

## Page shell (renderer mode)

Every artifact starts here. `App` owns the outermost layout.

```jsx
import { useState } from "react";

export default function App() {
  return (
    <div className="min-h-screen bg-zinc-900 text-white">
      <div className="max-w-5xl mx-auto p-3 md:p-6">
        <h1 className="text-xl md:text-2xl font-bold mb-6">Title</h1>
        {/* content */}
      </div>
    </div>
  );
}
```

## Sidebar layout

Fixed sidebar with scrollable main area. Collapses on mobile with a toggle button.

```jsx
import { useState } from "react";
import { Menu, X } from "lucide-react";

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-zinc-900 text-white">
      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-zinc-800 border-r border-zinc-700
        transform transition-transform duration-200
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
        lg:relative lg:translate-x-0
      `}>
        <div className="p-4">
          <h2 className="text-lg font-bold mb-4">App Name</h2>
          <nav className="space-y-1">
            {/* nav items */}
          </nav>
        </div>
      </aside>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main */}
      <div className="flex-1 min-w-0">
        <header className="border-b border-zinc-700 p-3 md:p-4 flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden text-zinc-400 hover:text-white"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <h1 className="text-lg font-bold">Page Title</h1>
        </header>
        <main className="p-3 md:p-6">
          {/* content */}
        </main>
      </div>
    </div>
  );
}
```

## Card

The basic content container for dashboard tiles, detail panels, list items.

```jsx
const Card = ({ title, children, className = "" }) => (
  <div className={`bg-zinc-800 rounded-xl p-4 border border-zinc-700 ${className}`}>
    {title && (
      <h3 className="text-sm text-zinc-400 mb-2">{title}</h3>
    )}
    {children}
  </div>
);
```

## Stat card

A card showing a single metric with optional trend indicator.

```jsx
const StatCard = ({ label, value, change, trend }) => (
  <div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
    <p className="text-sm text-zinc-400">{label}</p>
    <p className="text-2xl font-bold mt-1">{value}</p>
    {change && (
      <p className={`text-sm font-medium mt-1 ${
        trend === "up" ? "text-emerald-400" : "text-red-400"
      }`}>
        {trend === "up" ? "+" : ""}{change}
      </p>
    )}
  </div>
);
```

## Stats grid

Responsive grid for a row of stat cards.

```jsx
<div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
  <StatCard label="Total" value="1,234" change="12%" trend="up" />
  <StatCard label="Active" value="892" change="3%" trend="up" />
  <StatCard label="Errors" value="23" change="5%" trend="down" />
  <StatCard label="Latency" value="142ms" />
</div>
```

## Tabs

Pill-style tabs inside a container. Active tab gets a lighter background.

```jsx
const Tabs = ({ tabs, activeTab, onChange }) => (
  <div className="flex gap-1 bg-zinc-800 rounded-lg p-1 mb-4">
    {tabs.map(t => (
      <button
        key={t}
        onClick={() => onChange(t)}
        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          activeTab === t
            ? "bg-zinc-700 text-white"
            : "text-zinc-400 hover:text-zinc-200"
        }`}
      >
        {t}
      </button>
    ))}
  </div>
);
```

Usage:

```jsx
const [tab, setTab] = useState("Overview");
const tabs = ["Overview", "Details", "Logs"];

<Tabs tabs={tabs} activeTab={tab} onChange={setTab} />
{tab === "Overview" && <OverviewPanel />}
{tab === "Details" && <DetailsPanel />}
{tab === "Logs" && <LogsPanel />}
```

## Data table

Scrollable table with clickable sort headers.

```jsx
const DataTable = ({ columns, data, sortKey, sortDir, onSort }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm text-left">
      <thead>
        <tr className="border-b border-zinc-700 text-zinc-400">
          {columns.map(col => (
            <th
              key={col.key}
              onClick={() => onSort(col.key)}
              className="px-4 py-3 font-medium cursor-pointer hover:text-zinc-200"
            >
              {col.label}
              {sortKey === col.key && (
                <span className="ml-1">{sortDir === "asc" ? "\u2191" : "\u2193"}</span>
              )}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i} className="border-b border-zinc-700/50 hover:bg-zinc-800/50">
            {columns.map(col => (
              <td key={col.key} className="px-4 py-3 text-zinc-300">
                {col.render ? col.render(row[col.key], row) : row[col.key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
```

## Search bar

Text input with search icon. Pair with `useMemo` for filtering.

```jsx
import { Search } from "lucide-react";

const SearchBar = ({ query, onChange, placeholder = "Search..." }) => (
  <div className="relative">
    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
    <input
      type="text"
      value={query}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full pl-10 pr-4 py-2 bg-zinc-800/50 border border-zinc-700 rounded-lg text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500"
    />
  </div>
);
```

## Filter chips

Clickable filter buttons. Pair with search bar for combined filtering.

```jsx
const FilterChips = ({ options, active, onChange }) => (
  <div className="flex gap-2 flex-wrap">
    {options.map(opt => (
      <button
        key={opt}
        onClick={() => onChange(opt)}
        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
          active === opt
            ? "bg-blue-600 text-white"
            : "bg-zinc-800 text-zinc-400 border border-zinc-700 hover:text-zinc-200"
        }`}
      >
        {opt}
      </button>
    ))}
  </div>
);
```

## Recharts wrapper

Always wrap charts in `ResponsiveContainer`. Use dark theme grid and tooltip colors.

```jsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const ChartCard = ({ title, data, dataKey, color = "#10b981" }) => (
  <div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
    <h3 className="text-sm text-zinc-400 mb-4">{title}</h3>
    <div className="h-48">
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
          <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  </div>
);
```

## Status badge

Small badge with opacity background for status indicators.

```jsx
const StatusBadge = ({ status }) => {
  const styles = {
    active: "bg-emerald-900/30 text-emerald-400",
    idle: "bg-zinc-700 text-zinc-300",
    error: "bg-red-900/30 text-red-400",
    warning: "bg-amber-900/30 text-amber-400",
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${styles[status] || styles.idle}`}>
      {status}
    </span>
  );
};
```

## Empty state

When a filtered or searched list has no results.

```jsx
const EmptyState = ({ message = "No results found" }) => (
  <div className="flex flex-col items-center justify-center py-12 text-zinc-500">
    <p className="text-sm">{message}</p>
  </div>
);
```

## Expandable section

Click-to-expand detail panel. Uses click, not hover.

```jsx
import { ChevronDown } from "lucide-react";

const Expandable = ({ title, children, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border border-zinc-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 bg-zinc-800 hover:bg-zinc-700/50 transition-colors"
      >
        <span className="text-sm font-medium">{title}</span>
        <ChevronDown
          size={16}
          className={`text-zinc-400 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open && (
        <div className="px-4 py-3 border-t border-zinc-700">
          {children}
        </div>
      )}
    </div>
  );
};
```

## Progress bar

Horizontal bar with percentage fill. Useful for disk usage, completion tracking.

```jsx
const ProgressBar = ({ value, max, color = "bg-blue-500" }) => {
  const pct = Math.round((value / max) * 100);
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-zinc-700 rounded-full h-2 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-zinc-400 w-10 text-right">{pct}%</span>
    </div>
  );
};
```

-----

## Page shell (standalone mode)

When no Vite renderer is available. The component code inside is the same as renderer mode -- only the file wrapper changes.

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
  <script>
    tailwind.config = { darkMode: "class" }
  </script>
</head>
<body class="bg-zinc-900 text-white min-h-screen">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useMemo } = React;

    // ── Data ──────────────────────────────────────────────────

    // ... hardcoded data here ...

    // ── Components ────────────────────────────────────────────

    // ... helper components here, same JSX as renderer mode ...

    const App = () => {
      return (
        <div className="min-h-screen bg-zinc-900 text-white">
          <div className="max-w-5xl mx-auto p-3 md:p-6">
            <h1 className="text-xl md:text-2xl font-bold mb-6">Title</h1>
            {/* content */}
          </div>
        </div>
      );
    };

    const root = ReactDOM.createRoot(document.getElementById("root"));
    root.render(<App />);
  </script>
</body>
</html>
```

Key differences from renderer mode:
- No `import` / `export`. Destructure from globals: `React`, `Recharts`, `LucideReact`.
- Mount with `ReactDOM.createRoot` instead of `export default`.
- Add CDN `<script>` tags only for libraries the artifact uses.
- Tailwind CDN needs full class strings to be discoverable (see `references/tailwind-guide.md`).
