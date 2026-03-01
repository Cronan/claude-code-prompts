# Component patterns

Recurring layout and UI structures for JSX artifacts. Each pattern shows the minimal skeleton. Combine them to build full artifacts.

## Page shell

Every artifact starts with this structure. The `App` component owns the outermost layout.

```jsx
const App = () => {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="border-b border-zinc-800 px-6 py-4">
        <h1 className="text-lg font-semibold">Title</h1>
      </header>
      <main className="p-6">
        {/* content */}
      </main>
    </div>
  );
};
```

## Sidebar layout

Fixed sidebar with scrollable main area. Collapses on mobile.

```jsx
const App = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-100">
      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-zinc-900 border-r border-zinc-800
        transform transition-transform duration-200
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:relative lg:translate-x-0
      `}>
        <nav className="p-4 space-y-1">
          {/* nav items */}
        </nav>
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
        <header className="border-b border-zinc-800 px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden text-zinc-400 hover:text-zinc-100"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold">Title</h1>
        </header>
        <main className="p-6">
          {/* content */}
        </main>
      </div>
    </div>
  );
};
```

## Card

The basic content container. Use for dashboard tiles, list items, detail panels.

```jsx
const Card = ({ title, children, className = '' }) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-lg p-4 ${className}`}>
    {title && (
      <h3 className="text-sm font-medium text-zinc-400 mb-3">{title}</h3>
    )}
    {children}
  </div>
);
```

## Stat card

A card showing a single metric. Common in dashboards.

```jsx
const StatCard = ({ label, value, change, trend }) => (
  <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
    <p className="text-sm text-zinc-400">{label}</p>
    <p className="text-2xl font-semibold mt-1">{value}</p>
    {change && (
      <p className={`text-sm mt-1 ${trend === 'up' ? 'text-emerald-400' : 'text-red-400'}`}>
        {trend === 'up' ? '+' : ''}{change}
      </p>
    )}
  </div>
);
```

## Dashboard grid

Responsive grid that adapts from 1 column on mobile to 3-4 on desktop.

```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <StatCard label="Total" value="1,234" change="12%" trend="up" />
  <StatCard label="Active" value="892" change="3%" trend="up" />
  <StatCard label="Errors" value="23" change="5%" trend="down" />
  <StatCard label="Latency" value="142ms" change="8ms" trend="down" />
</div>
```

## Data table

Scrollable table with sort headers. Wraps in `overflow-x-auto` for small screens.

```jsx
const DataTable = ({ columns, data, sortKey, sortDir, onSort }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-zinc-800">
          {columns.map(col => (
            <th
              key={col.key}
              onClick={() => onSort(col.key)}
              className="text-left px-4 py-3 text-zinc-400 font-medium cursor-pointer hover:text-zinc-200"
            >
              {col.label}
              {sortKey === col.key && (
                <span className="ml-1">{sortDir === 'asc' ? '\u2191' : '\u2193'}</span>
              )}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
            {columns.map(col => (
              <td key={col.key} className="px-4 py-3">
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

## Tabs

Horizontal tab bar with content switching.

```jsx
const Tabs = ({ tabs, activeTab, onChange }) => (
  <div className="flex gap-1 border-b border-zinc-800 mb-4">
    {tabs.map(tab => (
      <button
        key={tab.id}
        onClick={() => onChange(tab.id)}
        className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
          activeTab === tab.id
            ? 'border-blue-500 text-blue-400'
            : 'border-transparent text-zinc-400 hover:text-zinc-200'
        }`}
      >
        {tab.label}
      </button>
    ))}
  </div>
);
```

Usage:

```jsx
const [activeTab, setActiveTab] = useState('overview');
const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'details', label: 'Details' },
  { id: 'logs', label: 'Logs' },
];

<Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
{activeTab === 'overview' && <OverviewPanel />}
{activeTab === 'details' && <DetailsPanel />}
{activeTab === 'logs' && <LogsPanel />}
```

## Search/filter bar

Text input with optional filter chips.

```jsx
const SearchBar = ({ query, onQueryChange, filters, activeFilters, onToggleFilter }) => (
  <div className="flex flex-col sm:flex-row gap-3 mb-4">
    <div className="relative flex-1">
      <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text"
        value={query}
        onChange={e => onQueryChange(e.target.value)}
        placeholder="Search..."
        className="w-full pl-10 pr-4 py-2 bg-zinc-800/50 border border-zinc-700/50 rounded-lg text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
      />
    </div>
    {filters && (
      <div className="flex gap-2 flex-wrap">
        {filters.map(f => (
          <button
            key={f}
            onClick={() => onToggleFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeFilters.includes(f)
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'bg-zinc-800 text-zinc-400 border border-zinc-700/50 hover:text-zinc-200'
            }`}
          >
            {f}
          </button>
        ))}
      </div>
    )}
  </div>
);
```

## Recharts wrapper

When using Recharts for data visualization. Always wrap charts in `ResponsiveContainer`.

```jsx
const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } = Recharts;

const ChartCard = ({ title, data, dataKey, color = '#10b981' }) => (
  <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
    <h3 className="text-sm font-medium text-zinc-400 mb-4">{title}</h3>
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis dataKey="name" tick={{ fill: '#71717a', fontSize: 12 }} />
          <YAxis tick={{ fill: '#71717a', fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#18181b',
              border: '1px solid #27272a',
              borderRadius: '8px',
              color: '#fafafa',
            }}
          />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  </div>
);
```

## Empty state

When a filtered list has no results.

```jsx
const EmptyState = ({ message = 'No results found' }) => (
  <div className="flex flex-col items-center justify-center py-12 text-zinc-500">
    <svg className="w-12 h-12 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <p className="text-sm">{message}</p>
  </div>
);
```

## Expandable section

Click-to-expand detail panel.

```jsx
const Expandable = ({ title, children, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border border-zinc-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 bg-zinc-900 hover:bg-zinc-800/50 transition-colors"
      >
        <span className="text-sm font-medium">{title}</span>
        <svg
          className={`w-4 h-4 text-zinc-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="px-4 py-3 border-t border-zinc-800">
          {children}
        </div>
      )}
    </div>
  );
};
```

## Loading/skeleton

For perceived responsiveness during state transitions.

```jsx
const Skeleton = ({ className = '' }) => (
  <div className={`animate-pulse bg-zinc-800 rounded ${className}`} />
);

// Usage
<Skeleton className="h-4 w-32" />
<Skeleton className="h-8 w-full mt-2" />
```
