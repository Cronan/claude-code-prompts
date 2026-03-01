import { useState, useMemo } from "react";
import { Search, ChevronDown } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

// ── Data ────────────────────────────────────────────────────
// Edit these arrays to change what the dashboard displays.

const CPU_HISTORY = [
  { time: "00:00", value: 23 }, { time: "02:00", value: 18 },
  { time: "04:00", value: 12 }, { time: "06:00", value: 31 },
  { time: "08:00", value: 54 }, { time: "10:00", value: 67 },
  { time: "12:00", value: 72 }, { time: "14:00", value: 58 },
  { time: "16:00", value: 63 }, { time: "18:00", value: 45 },
  { time: "20:00", value: 38 }, { time: "22:00", value: 27 },
];

const MEMORY_HISTORY = [
  { time: "00:00", value: 41 }, { time: "02:00", value: 42 },
  { time: "04:00", value: 40 }, { time: "06:00", value: 44 },
  { time: "08:00", value: 52 }, { time: "10:00", value: 61 },
  { time: "12:00", value: 68 }, { time: "14:00", value: 65 },
  { time: "16:00", value: 63 }, { time: "18:00", value: 55 },
  { time: "20:00", value: 48 }, { time: "22:00", value: 43 },
];

const SERVICES = [
  { name: "nginx",        status: "running", cpu: 2.1,  mem: 128, uptime: "14d 6h" },
  { name: "postgres",     status: "running", cpu: 8.4,  mem: 512, uptime: "14d 6h" },
  { name: "redis",        status: "running", cpu: 1.2,  mem: 64,  uptime: "7d 12h" },
  { name: "node-api",     status: "running", cpu: 12.3, mem: 256, uptime: "2d 8h"  },
  { name: "cron-worker",  status: "stopped", cpu: 0,    mem: 0,   uptime: "-"       },
  { name: "mqtt-broker",  status: "running", cpu: 3.7,  mem: 96,  uptime: "14d 6h" },
  { name: "grafana",      status: "running", cpu: 5.1,  mem: 192, uptime: "6d 3h"  },
  { name: "backup-agent", status: "error",   cpu: 0,    mem: 32,  uptime: "-"       },
];

const DISK_USAGE = [
  { mount: "/",        used: 12.4, total: 32,  fs: "ext4"  },
  { mount: "/home",    used: 45.2, total: 128, fs: "ext4"  },
  { mount: "/var/log", used: 2.1,  total: 8,   fs: "ext4"  },
  { mount: "/tmp",     used: 0.3,  total: 4,   fs: "tmpfs" },
];

// ── Helper components ───────────────────────────────────────

const StatusBadge = ({ status }) => {
  const styles = {
    running: "bg-emerald-900/30 text-emerald-400",
    stopped: "bg-zinc-700 text-zinc-300",
    error:   "bg-red-900/30 text-red-400",
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${styles[status] || styles.stopped}`}>
      {status}
    </span>
  );
};

const StatCard = ({ label, value, sub, color = "text-white" }) => (
  <div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
    <p className="text-sm text-zinc-400">{label}</p>
    <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    {sub && <p className="text-xs text-zinc-500 mt-1">{sub}</p>}
  </div>
);

const ChartCard = ({ title, data, color }) => (
  <div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
    <h3 className="text-sm text-zinc-400 mb-4">{title}</h3>
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
          <XAxis dataKey="time" stroke="#71717a" fontSize={12} />
          <YAxis stroke="#71717a" fontSize={12} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#27272a",
              border: "1px solid #3f3f46",
              borderRadius: "8px",
              color: "#fafafa",
            }}
            formatter={(val) => [`${val}%`]}
          />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  </div>
);

const DiskBar = ({ mount, used, total }) => {
  const pct = Math.round((used / total) * 100);
  const barColor = pct > 90 ? "bg-red-500" : pct > 70 ? "bg-amber-500" : "bg-blue-500";
  return (
    <div className="flex items-center gap-4 py-2">
      <span className="text-sm font-mono w-24 text-zinc-300 shrink-0">{mount}</span>
      <div className="flex-1 bg-zinc-700 rounded-full h-2 overflow-hidden">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-zinc-400 w-28 text-right shrink-0">
        {used}G / {total}G ({pct}%)
      </span>
    </div>
  );
};

// ── Main ────────────────────────────────────────────────────

export default function App() {
  const [tab, setTab] = useState("services");
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState("name");
  const [sortDir, setSortDir] = useState("asc");

  const filteredServices = useMemo(() => {
    let list = SERVICES;
    if (filter !== "all") list = list.filter(s => s.status === filter);
    if (search) list = list.filter(s => s.name.toLowerCase().includes(search.toLowerCase()));
    list = [...list].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      const cmp = typeof aVal === "string" ? aVal.localeCompare(bVal) : aVal - bVal;
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [filter, search, sortKey, sortDir]);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(d => d === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const runningCount = SERVICES.filter(s => s.status === "running").length;
  const errorCount = SERVICES.filter(s => s.status === "error").length;

  const filters = ["all", "running", "stopped", "error"];
  const tabs = ["services", "charts", "disk"];

  return (
    <div className="min-h-screen bg-zinc-900 text-white">
      <div className="max-w-5xl mx-auto p-3 md:p-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <div>
            <h1 className="text-xl md:text-2xl font-bold">System Monitor</h1>
            <p className="text-xs text-zinc-500">raspberrypi.local</p>
          </div>
          <span className="text-xs text-zinc-500 mt-1 sm:mt-0">Last updated: just now</span>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <StatCard label="CPU Usage" value="45%" sub="4 cores @ 1.5 GHz" />
          <StatCard label="Memory" value="1.8 / 4 GB" sub="45% used" />
          <StatCard
            label="Services"
            value={`${runningCount} / ${SERVICES.length}`}
            sub={errorCount > 0 ? `${errorCount} error` : "all healthy"}
            color={errorCount > 0 ? "text-amber-400" : "text-emerald-400"}
          />
          <StatCard label="Uptime" value="14d 6h" sub="since Feb 14" />
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-zinc-800 rounded-lg p-1 mb-6">
          {tabs.map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${
                tab === t
                  ? "bg-zinc-700 text-white"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Services tab */}
        {tab === "services" && (
          <div className="bg-zinc-800 rounded-xl border border-zinc-700">
            <div className="p-4 border-b border-zinc-700">
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                  <input
                    type="text"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Search services..."
                    className="w-full pl-10 pr-4 py-2 bg-zinc-800/50 border border-zinc-700 rounded-lg text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500"
                  />
                </div>
                <div className="flex gap-2">
                  {filters.map(f => (
                    <button
                      key={f}
                      onClick={() => setFilter(f)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                        filter === f
                          ? "bg-blue-600 text-white"
                          : "bg-zinc-700 text-zinc-400 hover:text-zinc-200"
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-zinc-700 text-zinc-400">
                    {[
                      { key: "name",   label: "Service" },
                      { key: "status", label: "Status" },
                      { key: "cpu",    label: "CPU %" },
                      { key: "mem",    label: "Memory (MB)" },
                      { key: "uptime", label: "Uptime" },
                    ].map(col => (
                      <th
                        key={col.key}
                        onClick={() => handleSort(col.key)}
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
                  {filteredServices.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="text-center py-8 text-zinc-500">
                        No services match the current filter.
                      </td>
                    </tr>
                  ) : (
                    filteredServices.map(svc => (
                      <tr key={svc.name} className="border-b border-zinc-700/50 hover:bg-zinc-800/50">
                        <td className="px-4 py-3 font-mono text-sm text-zinc-300">{svc.name}</td>
                        <td className="px-4 py-3"><StatusBadge status={svc.status} /></td>
                        <td className="px-4 py-3 text-zinc-300">{svc.cpu}</td>
                        <td className="px-4 py-3 text-zinc-300">{svc.mem}</td>
                        <td className="px-4 py-3 text-zinc-400">{svc.uptime}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Charts tab */}
        {tab === "charts" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ChartCard title="CPU % (24h)" data={CPU_HISTORY} color="#3b82f6" />
            <ChartCard title="Memory % (24h)" data={MEMORY_HISTORY} color="#8b5cf6" />
          </div>
        )}

        {/* Disk tab */}
        {tab === "disk" && (
          <div className="bg-zinc-800 rounded-xl p-4 border border-zinc-700">
            <h3 className="text-sm text-zinc-400 mb-3">Disk Usage</h3>
            <div className="space-y-1">
              {DISK_USAGE.map(d => (
                <DiskBar key={d.mount} {...d} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
