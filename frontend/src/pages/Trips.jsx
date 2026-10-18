
import { useEffect, useState } from "react";
import {
  Route,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Truck,
  Users,
  Package,
} from "lucide-react";
import api from "../services/api";

export default function Trips() {
  const [trips, setTrips] = useState([]);
  const [orders, setOrders] = useState([]);
  const [orderId, setOrderId] = useState("");
  const [loading, setLoading] = useState(true);
  const [allocating, setAllocating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);

  async function fetchData() {
    try {
      setLoading(true);
      setError("");

      const [tripsResponse, ordersResponse] = await Promise.all([
        api.get("/trips/"),
        api.get("/orders/"),
      ]);

      setTrips(
        Array.isArray(tripsResponse.data)
          ? tripsResponse.data
          : []
      );

      setOrders(
        Array.isArray(ordersResponse.data)
          ? ordersResponse.data
          : []
      );
    } catch (err) {
      console.error("Failed to load trips or orders:", err);
      setError(
        err.response?.data?.detail ||
          "Unable to load trips or orders. Check your backend."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
  }, []);

  async function handleAutoAllocate(event) {
    event.preventDefault();
    setError("");
    setSuccess(null);

    if (!orderId) {
      setError("Please select an order first.");
      return;
    }

    try {
      setAllocating(true);

      const response = await api.post(
        "/trips/auto-allocate",
        null,
        {
          params: {
            order_id: Number(orderId),
          },
        }
      );

      setSuccess(response.data.trip);
      setOrderId("");

      await fetchData();
    } catch (err) {
      console.error("Automatic allocation failed:", err);

      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "Automatic allocation failed. Please try again."
      );
    } finally {
      setAllocating(false);
    }
  }

  const activeTrips = trips.filter(
    (trip) =>
      ["planned", "in_progress"].includes(
        String(trip.status).toLowerCase()
      )
  );

  const inputClass =
    "mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-indigo-500";

  return (
    <div className="min-h-screen bg-slate-50 p-5 text-slate-800 sm:p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-widest text-indigo-600">
              Fleet Management
            </p>
            <h1 className="text-3xl font-bold text-slate-900">
              Trips
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              Allocate available trucks and drivers to orders.
            </p>
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold hover:bg-slate-100 disabled:opacity-50"
          >
            <RefreshCw size={17} />
            Refresh
          </button>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <Route size={22} className="mb-3 text-indigo-600" />
            <p className="text-sm text-slate-500">Total Trips</p>
            <p className="mt-1 text-3xl font-bold">
              {trips.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <Truck size={22} className="mb-3 text-emerald-600" />
            <p className="text-sm text-slate-500">Reserved Trips</p>
            <p className="mt-1 text-3xl font-bold">
              {activeTrips.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <Users size={22} className="mb-3 text-amber-600" />
            <p className="text-sm text-slate-500">Available Orders</p>
            <p className="mt-1 text-3xl font-bold">
              {
                orders.filter(
                  (order) =>
                    !trips.some(
                      (trip) => trip.order_id === order.id
                    )
                ).length
              }
            </p>
          </div>
        </div>

        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-xl bg-indigo-50 p-3 text-indigo-600">
              <Package size={22} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Automatic Allocation
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Select an order and let the backend choose eligible resources.
              </p>
            </div>
          </div>

          <form
            onSubmit={handleAutoAllocate}
            className="flex flex-col gap-4 sm:flex-row sm:items-end"
          >
            <label className="flex-1 text-sm font-medium">
              Select Order
              <select
                value={orderId}
                onChange={(event) => setOrderId(event.target.value)}
                className={inputClass}
                required
              >
                <option value="">Choose an order...</option>
                {orders
                  .filter(
                    (order) =>
                      !trips.some(
                        (trip) => trip.order_id === order.id
                      )
                  )
                  .map((order) => (
                    <option key={order.id} value={order.id}>
                      Order #{order.id} — {order.pickup_location ?? "Pickup"} →{" "}
                      {order.delivery_location ?? "Delivery"}
                    </option>
                  ))}
              </select>
            </label>

            <button
              type="submit"
              disabled={allocating || loading || !orderId}
              className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {allocating ? "Allocating..." : "Auto Allocate Trip"}
            </button>
          </form>

          {error && (
            <div className="mt-4 flex items-start gap-2 rounded-xl bg-red-50 p-4 text-sm text-red-700">
              <AlertCircle size={18} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
              <div className="mb-3 flex items-center gap-2 font-semibold text-emerald-800">
                <CheckCircle size={19} />
                Trip allocated successfully!
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                <p>Trip ID: <strong>{success.id}</strong></p>
                <p>Truck ID: <strong>{success.truck_id}</strong></p>
                <p>Driver ID: <strong>{success.driver_id}</strong></p>
                <p>Order ID: <strong>{success.order_id}</strong></p>
              </div>
            </div>
          )}

          {!loading && orders.length === 0 && (
            <p className="mt-4 text-sm text-amber-700">
              No orders found. Add an order before allocating a trip.
            </p>
          )}
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-5">
            <h2 className="font-bold text-slate-900">
              All Trips
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Trip assignments and current status.
            </p>
          </div>

          {loading ? (
            <p className="p-8 text-center text-slate-500">
              Loading trips...
            </p>
          ) : trips.length === 0 ? (
            <p className="p-8 text-center text-slate-500">
              No trips found.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-5 py-4">Trip ID</th>
                    <th className="px-5 py-4">Truck ID</th>
                    <th className="px-5 py-4">Driver ID</th>
                    <th className="px-5 py-4">Order ID</th>
                    <th className="px-5 py-4">Distance</th>
                    <th className="px-5 py-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {trips.map((trip) => (
                    <tr key={trip.id} className="hover:bg-slate-50">
                      <td className="px-5 py-4 font-semibold">
                        {trip.id}
                      </td>
                      <td className="px-5 py-4">{trip.truck_id}</td>
                      <td className="px-5 py-4">{trip.driver_id}</td>
                      <td className="px-5 py-4">{trip.order_id}</td>
                      <td className="px-5 py-4">
                        {trip.distance ?? 0} km
                      </td>
                      <td className="px-5 py-4">
                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold">
                          {trip.status ?? "Unknown"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
