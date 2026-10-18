
import { useEffect, useState } from "react";
import {
  Package,
  Plus,
  RefreshCw,
  X,
  MapPin,
  AlertCircle,
  Truck,
} from "lucide-react";
import api from "../services/api";

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");

  const [form, setForm] = useState({
    pickup_location: "",
    delivery_location: "",
    weight: "",
    deadline: "",
    distance_km: 0,
    pickup_latitude: "",
    pickup_longitude: "",
    delivery_latitude: "",
    delivery_longitude: "",
    company_id: 1,
  });

  async function fetchOrders() {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/orders/");
      setOrders(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load orders."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchOrders();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setFormError("");
    setFormSuccess("");

    const params = {
      ...form,
      weight: Number(form.weight),
      distance_km: Number(form.distance_km),
      company_id: Number(form.company_id),
    };

    for (const field of [
      "pickup_latitude",
      "pickup_longitude",
      "delivery_latitude",
      "delivery_longitude",
    ]) {
      if (params[field] === "") {
        delete params[field];
      }
    }

    try {
      await api.post("/orders/", null, { params });

      setFormSuccess("Order created successfully!");
      setForm({
        pickup_location: "",
        delivery_location: "",
        weight: "",
        deadline: "",
        distance_km: 0,
        pickup_latitude: "",
        pickup_longitude: "",
        delivery_latitude: "",
        delivery_longitude: "",
        company_id: 1,
      });
      setShowForm(false);

      await fetchOrders();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setFormError(
        typeof detail === "string"
          ? detail
          : "Failed to create order. Check the entered values."
      );
    } finally {
      setSaving(false);
    }
  }

  const inputClass =
    "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100";

  function displayValue(value) {
    if (value === null || value === undefined || value === "") {
      return "—";
    }
    return value;
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 sm:p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="mb-1 text-sm font-medium text-indigo-600">
              Fleet Management
            </p>
            <h1 className="text-3xl font-bold text-slate-900">
              Orders
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              Manage pickups, deliveries, and shipment details.
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                setFormError("");
                setFormSuccess("");
                setShowForm(!showForm);
              }}
              className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700"
            >
              {showForm ? <X size={18} /> : <Plus size={18} />}
              {showForm ? "Close Form" : "Create Order"}
            </button>

            <button
              onClick={fetchOrders}
              className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-100"
            >
              <RefreshCw size={17} />
              Refresh
            </button>
          </div>
        </div>

        {formSuccess && (
          <p className="mb-5 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">
            {formSuccess}
          </p>
        )}

        {showForm && (
          <form
            onSubmit={handleSubmit}
            className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h2 className="mb-5 text-lg font-bold text-slate-900">
              Create New Order
            </h2>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Pickup Location *
                </label>
                <input
                  name="pickup_location"
                  value={form.pickup_location}
                  onChange={handleChange}
                  placeholder="Enter pickup location"
                  className={inputClass}
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Delivery Location *
                </label>
                <input
                  name="delivery_location"
                  value={form.delivery_location}
                  onChange={handleChange}
                  placeholder="Enter delivery location"
                  className={inputClass}
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Weight (kg) *
                </label>
                <input
                  type="number"
                  name="weight"
                  value={form.weight}
                  onChange={handleChange}
                  placeholder="Enter shipment weight"
                  min="0.01"
                  step="any"
                  className={inputClass}
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Deadline *
                </label>
                <input
                  name="deadline"
                  value={form.deadline}
                  onChange={handleChange}
                  placeholder="Use the format accepted by your API"
                  className={inputClass}
                  required
                />
                <p className="mt-1 text-xs text-slate-400">
                  Enter the deadline in your backend's expected format.
                </p>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Distance (km)
                </label>
                <input
                  type="number"
                  name="distance_km"
                  min="0"
                  value={form.distance_km}
                  onChange={handleChange}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Company ID
                </label>
                <input
                  type="number"
                  name="company_id"
                  min="1"
                  value={form.company_id}
                  onChange={handleChange}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Pickup Latitude
                </label>
                <input
                  name="pickup_latitude"
                  value={form.pickup_latitude}
                  onChange={handleChange}
                  placeholder="Optional"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Pickup Longitude
                </label>
                <input
                  name="pickup_longitude"
                  value={form.pickup_longitude}
                  onChange={handleChange}
                  placeholder="Optional"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Delivery Latitude
                </label>
                <input
                  name="delivery_latitude"
                  value={form.delivery_latitude}
                  onChange={handleChange}
                  placeholder="Optional"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Delivery Longitude
                </label>
                <input
                  name="delivery_longitude"
                  value={form.delivery_longitude}
                  onChange={handleChange}
                  placeholder="Optional"
                  className={inputClass}
                />
              </div>
            </div>

            {formError && (
              <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">
                {formError}
              </p>
            )}

            <button
              type="submit"
              disabled={saving}
              className="mt-6 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60"
            >
              {saving ? "Creating..." : "Create Order"}
            </button>
          </form>
        )}

        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <Package size={22} />
            </div>
            <p className="text-sm text-slate-500">Total Orders</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading ? "..." : orders.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Total Shipment Weight</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading
                ? "..."
                : orders
                    .reduce(
                      (total, order) =>
                        total + (Number(order.weight) || 0),
                      0
                    )
                    .toLocaleString()}{" "}
              <span className="text-base font-medium text-slate-500">
                kg
              </span>
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <Truck size={22} />
            </div>
            <p className="text-sm text-slate-500">Orders Loaded</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading
                ? "..."
                : orders.filter(
                    (order) =>
                      order.status &&
                      ["loaded", "assigned", "in_transit", "completed"].includes(
                        String(order.status).toLowerCase()
                      )
                  ).length}
            </p>
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 p-5">
            <h2 className="text-lg font-bold text-slate-900">
              All Orders
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Order records retrieved from your backend.
            </p>
          </div>

          {error && (
            <div className="m-5 flex items-center gap-3 rounded-xl bg-red-50 p-4 text-sm text-red-700">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {loading ? (
            <p className="p-8 text-center text-slate-500">
              Loading orders...
            </p>
          ) : error ? null : orders.length === 0 ? (
            <p className="p-8 text-center text-slate-500">
              No orders found. Click Create Order to add one.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-5 py-4">Order ID</th>
                    <th className="px-5 py-4">Pickup</th>
                    <th className="px-5 py-4">Delivery</th>
                    <th className="px-5 py-4">Weight</th>
                    <th className="px-5 py-4">Distance</th>
                    <th className="px-5 py-4">Deadline</th>
                    <th className="px-5 py-4">Company ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {orders.map((order) => (
                    <tr
                      key={order.id ?? order.order_id}
                      className="hover:bg-slate-50"
                    >
                      <td className="px-5 py-4 font-semibold text-slate-900">
                        #{displayValue(order.id ?? order.order_id)}
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        <span className="inline-flex items-center gap-1">
                          <MapPin size={14} />
                          {displayValue(order.pickup_location)}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {displayValue(order.delivery_location)}
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {displayValue(order.weight)} kg
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {displayValue(order.distance_km)} km
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {displayValue(order.deadline)}
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {displayValue(order.company_id)}
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
