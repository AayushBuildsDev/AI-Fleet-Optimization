
import { useState } from "react";
import { Package, Route, Truck, Play, AlertCircle, LoaderCircle } from "lucide-react";
import api from "../services/api";

export default function Optimization() {
  const [truckId, setTruckId] = useState(1);
  const [driverId, setDriverId] = useState(1);
  const [fuelPrice, setFuelPrice] = useState(90);

  const [activeAction, setActiveAction] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function runOptimization(action) {
    setActiveAction(action);
    setResult(null);
    setError("");

    try {
      let response;

      if (action === "load") {
        response = await api.get("/optimization/load-allocation");
      } else if (action === "route") {
        response = await api.post("/optimization/route", null, {
          params: {
            truck_id: Number(truckId),
            driver_id: Number(driverId),
            fuel_price: Number(fuelPrice),
          },
        });
      } else {
        response = await api.post("/optimization/fleet-route", null, {
          params: {
            fuel_price: Number(fuelPrice),
          },
        });
      }

      setResult({
        action,
        data: response.data,
      });
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : JSON.stringify(detail ?? err.message, null, 2)
      );
    } finally {
      setActiveAction("");
    }
  }

  const inputClass =
    "mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100";

  const actions = [
    {
      id: "load",
      title: "Load Allocation",
      description:
        "Run the existing load-allocation endpoint and inspect its results.",
      icon: Package,
      color: "bg-blue-50 text-blue-600",
      button: "Run Load Allocation",
    },
    {
      id: "route",
      title: "Route Optimization",
      description:
        "Calculate an optimized route for a selected truck and driver.",
      icon: Route,
      color: "bg-violet-50 text-violet-600",
      button: "Calculate Route",
    },
    {
      id: "fleet",
      title: "Fleet Route Optimization",
      description:
        "Calculate routes for the fleet using your existing backend.",
      icon: Truck,
      color: "bg-emerald-50 text-emerald-600",
      button: "Optimize Fleet Routes",
    },
  ];

  return (
    <div className="min-w-0 flex-1 p-5 text-slate-800 sm:p-8">
      <header className="mb-8">
        <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
          Intelligent Logistics
        </p>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Optimization Center
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Run your existing load allocation and OR-Tools route optimization
          endpoints.
        </p>
      </header>

      <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold text-slate-900">
          Optimization Parameters
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Use IDs that exist in your database. Fuel price uses your backend's
          expected units.
        </p>

        <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div>
            <label className="text-sm font-medium text-slate-700">
              Truck ID
            </label>
            <input
              type="number"
              min="1"
              value={truckId}
              onChange={(event) => setTruckId(event.target.value)}
              className={inputClass}
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Driver ID
            </label>
            <input
              type="number"
              min="1"
              value={driverId}
              onChange={(event) => setDriverId(event.target.value)}
              className={inputClass}
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Fuel Price
            </label>
            <input
              type="number"
              min="0"
              step="any"
              value={fuelPrice}
              onChange={(event) => setFuelPrice(event.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        {actions.map(({ id, title, description, icon: Icon, color, button }) => (
          <article
            key={id}
            className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div
              className={`mb-4 grid h-12 w-12 place-items-center rounded-xl ${color}`}
            >
              <Icon size={24} />
            </div>

            <h2 className="text-lg font-bold text-slate-900">{title}</h2>
            <p className="mt-2 flex-1 text-sm leading-6 text-slate-500">
              {description}
            </p>

            <button
              disabled={Boolean(activeAction)}
              onClick={() => runOptimization(id)}
              className="mt-6 flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {activeAction === id ? (
                <LoaderCircle size={18} className="animate-spin" />
              ) : (
                <Play size={17} />
              )}
              {activeAction === id ? "Running..." : button}
            </button>
          </article>
        ))}
      </section>

      {error && (
        <section className="mt-8 rounded-2xl border border-red-200 bg-red-50 p-5">
          <div className="flex items-center gap-2 font-semibold text-red-700">
            <AlertCircle size={20} />
            Optimization failed
          </div>
          <pre className="mt-3 whitespace-pre-wrap break-words text-sm text-red-700">
            {error}
          </pre>
        </section>
      )}

      {result && (
        <section className="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-5">
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Optimization Results
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Actual response returned by FastAPI
              </p>
            </div>

            <button
              onClick={() => {
                navigator.clipboard?.writeText(
                  JSON.stringify(result.data, null, 2)
                );
              }}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Copy JSON
            </button>
          </div>

          <div className="p-5">
            <pre className="max-h-125 overflow-auto rounded-xl bg-slate-950 p-5 text-sm leading-6 text-emerald-300">
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </div>
        </section>
      )}

      <p className="mt-8 text-center text-xs text-slate-400">
        AI Fleet Optimization · Existing backend algorithms
      </p>
    </div>
  );
}
