import { useEffect, useState } from "react";
import {
  Truck,
  Users,
  Package,
  Route,
  MapPin,
  Fuel,
  Bell,
  Search,
  ArrowUpRight,
  Clock3,
  CheckCircle2,
} from "lucide-react";
import api from "../services/api";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/dashboard/summary")
      .then((response) => {
        setSummary(response.data);
        setError("");
      })
      .catch((err) => {
        console.error("Dashboard API error:", err);
        setError("Unable to load dashboard statistics.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const stats = [
    {
      label: "Total Trucks",
      value: summary?.total_trucks ?? 0,
      change: "Fleet capacity",
      icon: Truck,
      color: "bg-blue-50 text-blue-600",
    },
    {
      label: "Available Drivers",
      value: summary?.available_drivers ?? 0,
      change: "Ready for dispatch",
      icon: Users,
      color: "bg-emerald-50 text-emerald-600",
    },
    {
      label: "Pending Orders",
      value: summary?.pending_orders ?? 0,
      change: "Awaiting allocation",
      icon: Package,
      color: "bg-amber-50 text-amber-600",
    },
    {
      label: "Active Trips",
      value: summary?.active_trips ?? 0,
      change: "Currently in progress",
      icon: Route,
      color: "bg-violet-50 text-violet-600",
    },
  ];

  return (
    <div className="min-w-0 flex-1 p-5 text-slate-800 sm:p-8">
      {/* Dashboard Header */}
      <header className="mb-8 flex flex-wrap items-center justify-between gap-5">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
            Fleet overview
          </p>

          <h2 className="text-3xl font-bold tracking-tight text-slate-900">
            Dashboard
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Monitor your fleet and manage daily logistics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            aria-label="Search"
            className="rounded-xl border border-slate-200 bg-white p-3 text-slate-600 hover:bg-slate-100"
          >
            <Search size={19} />
          </button>

          <button
            aria-label="Notifications"
            className="relative rounded-xl border border-slate-200 bg-white p-3 text-slate-600 hover:bg-slate-100"
          >
            <Bell size={19} />
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500" />
          </button>

          <div className="grid h-11 w-11 place-items-center rounded-full bg-blue-100 font-bold text-blue-700">
            FA
          </div>
        </div>
      </header>

      {/* API Error */}
      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Statistics Cards */}
      <section className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map(({ label, value, change, icon: Icon, color }) => (
          <article
            key={label}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="mb-5 flex items-center justify-between">
              <div
                className={`grid h-12 w-12 place-items-center rounded-xl ${color}`}
              >
                <Icon size={23} />
              </div>

              <ArrowUpRight size={18} className="text-slate-400" />
            </div>

            <p className="text-sm text-slate-500">{label}</p>

            <h3 className="mt-1 text-3xl font-bold text-slate-900">
              {loading ? "..." : value}
            </h3>

            <p className="mt-3 text-xs text-slate-500">{change}</p>
          </article>
        ))}
      </section>

      {/* Main Dashboard Panels */}
      <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Fleet Activity */}
        <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-slate-900">
                Fleet activity
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Overview of trip operations
              </p>
            </div>

            <span className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-500">
              Trip overview
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl bg-blue-50/70 p-4">
              <Truck className="mb-3 text-blue-600" size={21} />
              <p className="text-sm text-slate-500">On the road</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {loading ? "..." : summary?.active_trips ?? 0}
              </p>
            </div>

            <div className="rounded-xl bg-emerald-50/70 p-4">
              <CheckCircle2
                className="mb-3 text-emerald-600"
                size={21}
              />
              <p className="text-sm text-slate-500">Completed orders</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {loading
                  ? "..."
                  : summary?.completed_orders ?? 0}
              </p>
            </div>

            <div className="rounded-xl bg-amber-50/70 p-4">
              <Clock3 className="mb-3 text-amber-600" size={21} />
              <p className="text-sm text-slate-500">Awaiting dispatch</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {loading ? "..." : summary?.pending_orders ?? 0}
              </p>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-dashed border-slate-300 p-8 text-center">
            <MapPin className="mx-auto mb-3 text-slate-400" size={30} />

            <p className="font-medium text-slate-700">Fleet route map</p>

            <p className="mt-1 text-sm text-slate-500">
              Map integration will be added in a later step.
            </p>
          </div>
        </article>

        {/* Route Optimization */}
        <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <div className="mb-3 grid h-12 w-12 place-items-center rounded-xl bg-indigo-50 text-indigo-600">
              <Route size={24} />
            </div>

            <h3 className="text-lg font-bold text-slate-900">
              Route optimization
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-500">
              Generate route and load recommendations using your existing
              backend.
            </p>
          </div>

          <div className="mb-5 space-y-3 rounded-xl bg-slate-50 p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Distance planning</span>
              <span className="font-semibold text-slate-700">
                Available
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Fuel estimates</span>
              <span className="font-semibold text-slate-700">
                Available
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">ML predictions</span>
              <span className="font-semibold text-slate-700">
                Not used
              </span>
            </div>
          </div>

          <p className="rounded-xl bg-blue-50 p-3 text-sm leading-5 text-blue-700">
            Your existing optimization engine will be connected here.
          </p>
        </article>
      </section>

      <footer className="mt-8 text-center text-xs text-slate-400">
        AI Fleet Optimization · Logistics workspace
      </footer>
    </div>
  );
}
