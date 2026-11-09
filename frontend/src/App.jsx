
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity, Bus, CalendarDays, ChartNoAxesCombined, CheckCircle2,
  ChevronDown, Clock3, Download, LayoutDashboard, Menu, Moon,
  RefreshCw, Search, Settings, Sun, TrendingUp, Users, X,
  AlertCircle, MapPin, CreditCard, Route
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, BarChart, Bar, PieChart, Pie, Cell, Legend
} from "recharts";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const COLORS = ["#4263eb", "#12b886", "#f59f00", "#e64980", "#7950f2", "#15aabf"];

const getFirst = (obj, keys, fallback = "") => {
  if (!obj || typeof obj !== "object") return fallback;
  for (const key of keys) {
    if (obj[key] !== undefined && obj[key] !== null) return obj[key];
  }
  return fallback;
};

const prettify = (text) =>
  String(text ?? "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

const numberFormat = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number.toLocaleString("en-IN") : "—";
};

const getLabel = (item, index) =>
  String(
    getFirst(item, [
      "date", "Ride_start_date", "day", "stop_name", "stop",
      "boarding_stop", "alighting_stop", "bus_service",
      "service", "travel_mode", "mode", "card_type", "type",
      "name", "label", "item"
    ], `Item ${index + 1}`)
  );

const getValue = (item) => {
  if (typeof item === "number") return item;
  return Number(
    getFirst(item, [
      "total_ridership", "ridership", "rides", "ride_count",
      "count", "total", "passengers", "value", "frequency",
      "support", "confidence"
    ], 0)
  ) || 0;
};

const toChartData = (items) =>
  (Array.isArray(items) ? items : []).map((item, index) => ({
    ...item,
    label: getLabel(item, index),
    value: getValue(item)
  }));

function StatCard({ icon: Icon, title, value, note, color }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span className={`stat-icon ${color}`}>
          <Icon size={21} />
        </span>
        <span className="stat-note"><TrendingUp size={14} /> Analytics</span>
      </div>
      <p className="stat-title">{title}</p>
      <h2 className="stat-value">{value}</h2>
      <p className="stat-description">{note}</p>
    </article>
  );
}

function Panel({ title, subtitle, children, action }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h3>{title}</h3>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function EmptyChart({ message = "No data available for this selection." }) {
  return <div className="empty-chart">{message}</div>;
}

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [startDate, setStartDate] = useState("2018-02-01");
  const [endDate, setEndDate] = useState("2018-02-28");
  const [lastUpdated, setLastUpdated] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();
      if (startDate) params.set("start_date", startDate);
      if (endDate) params.set("end_date", endDate);

      const response = await fetch(
        `${API_URL}/api/dashboard?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const result = await response.json();
      setData(result);
      setLastUpdated(new Date());
    } catch (err) {
      setError(
        `Unable to load dashboard data. Check that the backend is running at ${API_URL}.`
      );
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const summary = data?.summary || {};

  const dailyData = useMemo(
    () => toChartData(data?.daily_ridership),
    [data]
  );
  const boardingData = useMemo(
    () => toChartData(data?.top_boarding_stops),
    [data]
  );
  const alightingData = useMemo(
    () => toChartData(data?.top_alighting_stops),
    [data]
  );
  const travelData = useMemo(
    () => toChartData(data?.travel_modes),
    [data]
  );
  const cardData = useMemo(
    () => toChartData(data?.card_types),
    [data]
  );
  const serviceData = useMemo(
    () => toChartData(data?.top_bus_services),
    [data]
  );

  const rules = useMemo(() => {
    const list = Array.isArray(data?.association_rules)
      ? data.association_rules
      : [];
    const term = search.trim().toLowerCase();

    return list.filter((rule) =>
      JSON.stringify(rule).toLowerCase().includes(term)
    );
  }, [data, search]);

  const totalRides = getFirst(summary, [
    "total_ridership", "total_rides", "total_trips",
    "total_records", "total_passengers", "total"
  ], null);

  const totalStops = getFirst(summary, [
    "total_stops", "unique_stops", "stop_count"
  ], null);

  const totalServices = getFirst(summary, [
    "total_bus_services", "unique_bus_services", "service_count"
  ], null);

  const averageRides = getFirst(summary, [
    "average_daily_ridership", "avg_daily_ridership",
    "average_ridership", "daily_average"
  ], null);

  const stats = [
    {
      icon: Activity,
      title: "Total Ridership",
      value: numberFormat(totalRides ?? dailyData.reduce((sum, row) => sum + row.value, 0)),
      note: "Across the selected period",
      color: "blue"
    },
    {
      icon: MapPin,
      title: "Boarding Stops",
      value: numberFormat(totalStops ?? boardingData.length),
      note: "Stops in the available results",
      color: "green"
    },
    {
      icon: Bus,
      title: "Bus Services",
      value: numberFormat(totalServices ?? serviceData.length),
      note: "Services in the available results",
      color: "purple"
    },
    {
      icon: Users,
      title: "Average Daily Ridership",
      value: numberFormat(averageRides ?? (
        dailyData.length
          ? Math.round(dailyData.reduce((sum, row) => sum + row.value, 0) / dailyData.length)
          : 0
      )),
      note: "Daily average for displayed data",
      color: "orange"
    }
  ];

  const downloadCSV = () => {
    if (!rules.length) return;

    const headers = [...new Set(rules.flatMap((row) => Object.keys(row)))];
    const escapeCSV = (value) =>
      `"${String(value ?? "").replaceAll('"', '""')}"`;

    const csv = [
      headers.map(escapeCSV).join(","),
      ...rules.map((row) =>
        headers.map((header) => escapeCSV(row[header])).join(",")
      )
    ].join("\n");

    const blob = new Blob(["\uFEFF" + csv], {
      type: "text/csv;charset=utf-8;"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "association_rules.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
    setSidebarOpen(false);
  };

  return (
    <div className={`app-shell ${darkMode ? "dark-theme" : ""}`}>
      {sidebarOpen && (
        <button
          className="mobile-overlay"
          aria-label="Close menu"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><Bus size={25} /></div>
          <div>
            <h2>TransitIQ</h2>
            <span>RIDERSHIP ANALYTICS</span>
          </div>
          <button
            className="icon-button close-sidebar"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        <p className="nav-label">WORKSPACE</p>
        <nav className="side-nav">
          <button className="nav-item active" onClick={() => scrollToSection("overview")}>
            <LayoutDashboard size={19} /> Overview
          </button>
          <button className="nav-item" onClick={() => scrollToSection("ridership")}>
            <ChartNoAxesCombined size={19} /> Ridership Trends
          </button>
          <button className="nav-item" onClick={() => scrollToSection("stops")}>
            <MapPin size={19} /> Bus Stops
          </button>
          <button className="nav-item" onClick={() => scrollToSection("patterns")}>
            <Route size={19} /> Travel Patterns
          </button>
          <button className="nav-item" onClick={() => scrollToSection("rules")}>
            <Activity size={19} /> Association Rules
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-info">
            <span className="status-dot" />
            <div>
              <strong>{error ? "Connection issue" : loading ? "Connecting..." : data ? "Analytics service" : "Waiting for data"}</strong>
              <small>{error ? "Check your backend" : "Local API connection"}</small>
            </div>
          </div>
          <button className="nav-item" onClick={() => setShowSettings(true)}>
            <Settings size={19} /> Settings
          </button>
          <div className="sidebar-footer">Public Transport Analytics<br />Data Intelligence Dashboard</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button menu-button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <Menu size={22} />
            </button>
            <div>
              <p className="breadcrumb">Workspace / <span>Overview</span></p>
              <h1>Ridership Dashboard</h1>
            </div>
          </div>

          <div className="topbar-actions">
            <button
              className="icon-button theme-button"
              onClick={() => setDarkMode((value) => !value)}
              title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
              aria-label="Toggle theme"
            >
              {darkMode ? <Sun size={19} /> : <Moon size={19} />}
            </button>
            <button
              className="settings-button"
              onClick={() => setShowSettings(true)}
            >
              <Settings size={17} /> Settings
            </button>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-row" id="overview">
            <div>
              <div className="eyebrow"><span className="eyebrow-dot" /> TRANSPORT INTELLIGENCE</div>
              <h2>Understand your ridership.</h2>
              <p>Explore passenger activity, popular stops and travel patterns in one place.</p>
            </div>
            <button className="primary-button" onClick={fetchDashboard} disabled={loading}>
              <RefreshCw size={17} className={loading ? "spin" : ""} />
              {loading ? "Refreshing..." : "Refresh data"}
            </button>
          </section>

          <section className="filter-bar">
            <div className="filter-title">
              <CalendarDays size={19} />
              <div>
                <strong>Date range</strong>
                <span>Choose your analysis period</span>
              </div>
            </div>
            <div className="date-inputs">
              <label>
                <span>From</span>
                <input
                  type="date"
                  value={startDate}
                  max={endDate || undefined}
                  onChange={(event) => setStartDate(event.target.value)}
                />
              </label>
              <label>
                <span>To</span>
                <input
                  type="date"
                  value={endDate}
                  min={startDate || undefined}
                  onChange={(event) => setEndDate(event.target.value)}
                />
              </label>
              <button className="apply-button" onClick={fetchDashboard} disabled={loading}>
                Apply filters
              </button>
            </div>
          </section>

          {error && (
            <div className="error-banner">
              <AlertCircle size={20} />
              <div>
                <strong>Unable to load dashboard data</strong>
                <p>{error}</p>
              </div>
              <button className="apply-button" onClick={fetchDashboard} disabled={loading}>
                Retry
              </button>
            </div>
          )}

          <div className="section-heading">
            <div>
              <h3>Key performance indicators</h3>
              <p>A quick snapshot of transport activity</p>
            </div>
            <span className="live-badge">
              <span className="status-dot" /> {loading ? "Updating" : data ? "Data loaded" : "Waiting"}
            </span>
          </div>

          <section className="stats-grid">
            {stats.map((stat) => (
              <StatCard key={stat.title} {...stat} />
            ))}
          </section>

          <section className="charts-grid" id="ridership">
            <Panel
              title="Daily ridership"
              subtitle="Passenger activity over time"
              action={<span className="chart-tag">TREND</span>}
            >
              {dailyData.length ? (
                <div className="chart-area">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={dailyData} margin={{ top: 12, right: 10, left: -15, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--chart-grid)" />
                      <XAxis dataKey="label" tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid var(--border)", background: "var(--card)" }} />
                      <Line type="monotone" dataKey="value" name="Ridership" stroke="#4263eb" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : <EmptyChart message={loading ? "Loading ridership trends..." : undefined} />}
            </Panel>

            <Panel
              title="Travel modes"
              subtitle="Distribution by travel category"
              action={<span className="chart-tag">MIX</span>}
            >
              {travelData.length ? (
                <div className="chart-area">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={travelData} dataKey="value" nameKey="label" cx="50%" cy="46%" innerRadius={57} outerRadius={88} paddingAngle={3}>
                        {travelData.map((entry, index) => (
                          <Cell key={entry.label + index} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend verticalAlign="bottom" height={35} formatter={(value) => <span className="legend-text">{value}</span>} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : <EmptyChart message={loading ? "Loading travel modes..." : undefined} />}
            </Panel>
          </section>

          <section className="charts-grid" id="stops">
            <Panel title="Top boarding stops" subtitle="Most frequently used boarding locations">
              {boardingData.length ? (
                <div className="chart-area tall-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={boardingData.slice(0, 8)} layout="vertical" margin={{ top: 4, right: 15, left: 8, bottom: 4 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--chart-grid)" />
                      <XAxis type="number" tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="label" width={110} tick={{ fill: "var(--muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <Tooltip />
                      <Bar dataKey="value" name="Boardings" fill="#4263eb" radius={[0, 5, 5, 0]} barSize={18} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : <EmptyChart />}
            </Panel>

            <Panel title="Top alighting stops" subtitle="Most frequently used exit locations">
              {alightingData.length ? (
                <div className="chart-area tall-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={alightingData.slice(0, 8)} layout="vertical" margin={{ top: 4, right: 15, left: 8, bottom: 4 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--chart-grid)" />
                      <XAxis type="number" tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="label" width={110} tick={{ fill: "var(--muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <Tooltip />
                      <Bar dataKey="value" name="Alightings" fill="#12b886" radius={[0, 5, 5, 0]} barSize={18} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : <EmptyChart />}
            </Panel>
          </section>

          <section className="charts-grid" id="patterns">
            <Panel title="Ridership by card type" subtitle="Passenger ticket and card usage">
              {cardData.length ? (
                <div className="chart-area">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={cardData} margin={{ top: 12, right: 8, left: -18, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--chart-grid)" />
                      <XAxis dataKey="label" tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip />
                      <Bar dataKey="value" name="Usage" fill="#7950f2" radius={[5, 5, 0, 0]} barSize={35} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : <EmptyChart />}
            </Panel>

            <Panel title="Top bus services" subtitle="Services with the highest recorded activity">
              {serviceData.length ? (
                <div className="service-list">
                  {serviceData.slice(0, 6).map((item, index) => {
                    const max = Math.max(...serviceData.map((row) => row.value), 1);
                    return (
                      <div className="service-row" key={item.label + index}>
                        <span className="service-rank">{String(index + 1).padStart(2, "0")}</span>
                        <div className="service-detail">
                          <div className="service-name">{item.label}</div>
                          <div className="progress-track">
                            <div className="progress-fill" style={{ width: `${(item.value / max) * 100}%` }} />
                          </div>
                        </div>
                        <strong>{numberFormat(item.value)}</strong>
                      </div>
                    );
                  })}
                </div>
              ) : <EmptyChart />}
            </Panel>
          </section>

          <section id="rules">
            <Panel
              title="Association rule insights"
              subtitle="Explore relationships discovered in the ridership data"
              action={
                <button className="export-button" onClick={downloadCSV} disabled={!rules.length}>
                  <Download size={16} /> Export CSV
                </button>
              }
            >
              <div className="table-toolbar">
                <div className="search-box">
                  <Search size={17} />
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search rules..."
                    aria-label="Search association rules"
                  />
                  {search && (
                    <button className="clear-search" onClick={() => setSearch("")} aria-label="Clear search">
                      <X size={15} />
                    </button>
                  )}
                </div>
                <span className="result-count">{rules.length} results</span>
              </div>

              {rules.length ? (
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(rules[0]).map((key) => (
                          <th key={key}>{prettify(key)}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rules.slice(0, 100).map((rule, index) => (
                        <tr key={index}>
                          {Object.keys(rules[0]).map((key) => (
                            <td key={key}>
                              {typeof rule[key] === "number"
                                ? Number(rule[key]).toLocaleString("en-IN", { maximumFractionDigits: 3 })
                                : String(rule[key] ?? "—")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <EmptyChart message={loading ? "Loading association rules..." : "No matching rules found."} />
              )}
              <div className="table-footer">
                Showing up to 100 rows. Use Export CSV to download all filtered results.
              </div>
            </Panel>
          </section>

          <footer className="page-footer">
            <span>TransitIQ · Public Transport Ridership Analytics</span>
            <span><Clock3 size={14} /> {lastUpdated ? `Last updated ${lastUpdated.toLocaleTimeString()}` : "Waiting for first update"}</span>
          </footer>
        </div>
      </main>

      {showSettings && (
        <div className="modal-backdrop" onClick={() => setShowSettings(false)}>
          <section
            className="settings-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="settings-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-heading">
              <div>
                <h2 id="settings-title">Dashboard settings</h2>
                <p>Personalize your analytics workspace.</p>
              </div>
              <button className="icon-button" onClick={() => setShowSettings(false)} aria-label="Close settings">
                <X size={20} />
              </button>
            </div>

            <div className="setting-row">
              <div className="setting-icon"><Sun size={20} /></div>
              <div className="setting-copy">
                <strong>Appearance</strong>
                <span>Switch between light and dark themes.</span>
              </div>
              <button
                className={`toggle-switch ${darkMode ? "toggle-on" : ""}`}
                onClick={() => setDarkMode((value) => !value)}
                aria-label="Toggle dark mode"
                aria-pressed={darkMode}
              >
                <span />
              </button>
            </div>

            <div className="setting-row">
              <div className="setting-icon"><RefreshCw size={20} /></div>
              <div className="setting-copy">
                <strong>Data connection</strong>
                <span>{error ? "Backend connection needs attention." : data ? "Dashboard data has loaded." : "Waiting for the API response."}</span>
              </div>
              {error ? <AlertCircle size={20} color="#e03131" /> : data ? <CheckCircle2 size={20} color="#12b886" /> : <Activity size={20} />}
            </div>

            <div className="settings-note">
              <strong>API endpoint</strong>
              <code>{API_URL}/api/dashboard</code>
            </div>

            <div className="modal-actions">
              <button className="settings-button" onClick={() => setShowSettings(false)}>Close</button>
              <button className="primary-button" onClick={() => { setShowSettings(false); fetchDashboard(); }}>
                <RefreshCw size={16} /> Refresh data
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
