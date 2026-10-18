import { useEffect, useState } from "react";
import { Truck, RefreshCw, AlertCircle, Plus, X } from "lucide-react";
import api from "../services/api";

function Trucks() {
const [showForm, setShowForm] = useState(false);
const [saving, setSaving] = useState(false);
const [formError, setFormError] = useState("");
const [formSuccess, setFormSuccess] = useState("");

const [form, setForm] = useState({
  registration_number: "",
  capacity: "",
  fuel_type: "Diesel",
  fuel_efficiency: "",
  company_id: "1",
});
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchTrucks() {
    try {
      setLoading(true);
      setError("");
      const response = await api.get("/trucks/");
      setTrucks(response.data);
    } catch (err) {
      console.error("Failed to fetch trucks:", err);
      setError("Unable to load trucks. Please check the backend.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchTrucks();
  }, []);

  async function handleSubmit(event) {
  event.preventDefault();
  setSaving(true);
  setFormError("");
  setFormSuccess("");

  try {
    const params = {
      registration_number: form.registration_number.trim(),
      capacity: Number(form.capacity),
      fuel_type: form.fuel_type.trim(),
      company_id: Number(form.company_id),
    };

    if (form.fuel_efficiency !== "") {
      params.fuel_efficiency = Number(form.fuel_efficiency);
    }

    await api.post("/trucks/", null, { params });

    setFormSuccess("Truck registered successfully!");
    setForm({
      registration_number: "",
      capacity: "",
      fuel_type: "Diesel",
      fuel_efficiency: "",
      company_id: "1",
    });

    setShowForm(false);
    await fetchTrucks();
  } catch (err) {
    console.error("Create truck failed:", err);
    setFormError(
      err.response?.data?.detail
        ? JSON.stringify(err.response.data.detail)
        : "Unable to register truck. Check the entered values and backend."
    );
  } finally {
    setSaving(false);
  }
}

  return (
    <div className="min-h-screen bg-slate-50 p-5 text-slate-800 sm:p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-widest text-blue-600">
              Fleet management
            </p>
            <h1 className="text-3xl font-bold text-slate-900">
              Trucks
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              View and monitor your registered fleet vehicles.
            </p>
          </div>


<div className="flex gap-3">
  <button
    onClick={() => {
      setShowForm(!showForm);<th className="px-5 py-4">Truck</th>
      setFormError("");
      setFormSuccess("");
    }}
    className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700"
  >
    {showForm ? <X size={17} /> : <Plus size={17} />}
    {showForm ? "Cancel" : "Add Truck"}
  </button>

  <button
    onClick={fetchTrucks}
    disabled={loading}
    className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold hover:bg-slate-100 disabled:opacity-50"
  >
    <RefreshCw size={17} />
    Refresh
  </button>
</div>

{showForm && (
  <form
    onSubmit={handleSubmit}
    className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
  >
    <h2 className="mb-5 text-lg font-bold text-slate-900">
      Register a new truck
    </h2>

    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <label className="text-sm font-medium text-slate-700">
        Registration number *
        <input
          required
          value={form.registration_number}
          onChange={(e) =>
            setForm({ ...form, registration_number: e.target.value })
          }
          placeholder="MP07AB1234"
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2.5 outline-none focus:border-blue-500"
        />
      </label>

      <label className="text-sm font-medium text-slate-700">
        Capacity *
        <input
          required
          type="number"
          min="1"
          value={form.capacity}
          onChange={(e) => setForm({ ...form, capacity: e.target.value })}
          placeholder="20000"
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2.5 outline-none focus:border-blue-500"
        />
      </label>

      <label className="text-sm font-medium text-slate-700">
        Fuel type *
        <select
          required
          value={form.fuel_type}
          onChange={(e) => setForm({ ...form, fuel_type: e.target.value })}
          className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 outline-none focus:border-blue-500"
        >
          <option value="Diesel">Diesel</option>
          <option value="Petrol">Petrol</option>
          <option value="CNG">CNG</option>
          <option value="Electric">Electric</option>
        </select>
      </label>

      <label className="text-sm font-medium text-slate-700">
        Fuel efficiency (km/L)
        <input
          type="number"
          min="0"
          step="any"
          value={form.fuel_efficiency}
          onChange={(e) =>
            setForm({ ...form, fuel_efficiency: e.target.value })
          }
          placeholder="8"
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2.5 outline-none focus:border-blue-500"
        />
      </label>

      <label className="text-sm font-medium text-slate-700">
        Company ID
        <input
          type="number"
          min="1"
          value={form.company_id}
          onChange={(e) => setForm({ ...form, company_id: e.target.value })}
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2.5 outline-none focus:border-blue-500"
        />
      </label>
    </div>

    {formError && (
      <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
        {formError}
      </p>
    )}

    <button
      type="submit"
      disabled={saving}
      className="mt-5 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
    >
      {saving ? "Registering..." : "Register Truck"}
    </button>
  </form>
)}

{formSuccess && (
  <p className="mb-5 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">
    {formSuccess}
  </p>
)}

</div>

        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 grid h-11 w-11 place-items-center rounded-xl bg-blue-50 text-blue-600">
              <Truck size={22} />
            </div>
            <p className="text-sm text-slate-500">Total registered trucks</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading ? "..." : trucks.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 grid h-11 w-11 place-items-center rounded-xl bg-emerald-50 text-emerald-600">
              <Truck size={22} />
            </div>
            <p className="text-sm text-slate-500">Available trucks</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading
                ? "..."
                : trucks.filter(
                    (truck) =>
                      truck.status?.toLowerCase() === "available"
                  ).length}
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-5 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-5">
            <h2 className="font-bold text-slate-900">Registered vehicles</h2>
            <p className="mt-1 text-sm text-slate-500">
              Truck information retrieved from your backend.
            </p>
          </div>

          {loading ? (
            <p className="p-8 text-center text-slate-500">
              Loading trucks...
            </p>
          ) : trucks.length === 0 && !error ? (
            <p className="p-8 text-center text-slate-500">
              No trucks found in the database.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-5 py-4">Truck ID</th>
                    <th className="px-5 py-4">Truck</th>
                    <th className="px-5 py-4">Capacity</th>
                    <th className="px-5 py-4">Fuel type</th>
                    <th className="px-5 py-4">Efficiency</th>
                    <th className="px-5 py-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {trucks.map((truck) => (
                    <tr key={truck.id} className="hover:bg-slate-50">
                      
<td className="px-5 py-4">
  {truck.id ?? truck.truck_id ?? "—"}
</td>

<td className="whitespace-nowrap px-5 py-4 font-semibold text-slate-800">
  {truck.registration_number ?? `Truck #${truck.id}`}
</td>

                      <td className="px-5 py-4">
                        {truck.capacity ?? "—"}
                      </td>
                      <td className="px-5 py-4">
                        {truck.fuel_type ?? "—"}
                      </td>
                      <td className="px-5 py-4">
                        {truck.fuel_efficiency != null
                          ? `${truck.fuel_efficiency} km/L`
                          : "—"}
                      </td>
                      <td className="px-5 py-4">
                        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                          {truck.status ?? "Unknown"}
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

export default Trucks;
