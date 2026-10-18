
import { useEffect, useState } from "react";
import { Users, Plus, RefreshCw, X, AlertCircle } from "lucide-react";
import api from "../services/api";

export default function Drivers() {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");

  const [form, setForm] = useState({
    name: "",
    license_category: "",
    experience_years: "",
    working_hours: "",
    rest_hours: "",
    company_id: "",
  });

  async function fetchDrivers() {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/drivers/");
      setDrivers(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load drivers."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchDrivers();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: [
        "experience_years",
        "working_hours",
        "rest_hours",
        "company_id",
      ].includes(name)
        ? Number(value)
        : value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setFormError("");
    setFormSuccess("");

    try {
      await api.post("/drivers/", null, {
        params: form,
      });

      setFormSuccess("Driver registered successfully!");
      setForm({
        name: "",
        license_category: "",
        experience_years: 0,
        working_hours: 0,
        rest_hours: 0,
        company_id: 1,
      });
      setShowForm(false);

      await fetchDrivers();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setFormError(
        typeof detail === "string"
          ? detail
          : "Failed to register driver. Please check the fields."
      );
    } finally {
      setSaving(false);
    }
  }

  const inputClass =
    "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100";

  return (
    <div className="min-h-screen bg-slate-50 p-4 sm:p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="mb-1 text-sm font-medium text-indigo-600">
              Fleet Management
            </p>
            <h1 className="text-3xl font-bold text-slate-900">
              Drivers
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              Manage your fleet drivers and their work details.
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
              {showForm ? "Close Form" : "Add Driver"}
            </button>

            <button
              onClick={fetchDrivers}
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
              Register New Driver
            </h2>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Driver Name *
                </label>
                <input
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Enter driver name"
                  className={inputClass}
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  License Category *
                </label>
                <input
                  name="license_category"
                  value={form.license_category}
                  onChange={handleChange}
                  placeholder="e.g. Heavy Vehicle"
                  className={inputClass}
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Experience (years)
                </label>
                <input
                  type="number"
                  name="experience_years"
                  min="0"
                  value={form.experience_years}
                  onChange={handleChange}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Working Hours
                </label>
                <input
                  type="number"
                  name="working_hours"
                  min="0"
                  value={form.working_hours}
                  onChange={handleChange}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Rest Hours
                </label>
                <input
                  type="number"
                  name="rest_hours"
                  min="0"
                  value={form.rest_hours}
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
              {saving ? "Registering..." : "Register Driver"}
            </button>
          </form>
        )}

        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <Users size={22} />
            </div>
            <p className="text-sm text-slate-500">Total Drivers</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading ? "..." : drivers.length}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Experienced Drivers</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading
                ? "..."
                : drivers.filter(
                    (driver) => Number(driver.experience_years) >= 3
                  ).length}
            </p>
            <p className="mt-2 text-xs text-slate-400">
              3 or more years of experience
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">License Categories</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loading
                ? "..."
                : new Set(
                    drivers.map((driver) => driver.license_category)
                  ).size}
            </p>
            <p className="mt-2 text-xs text-slate-400">
              Unique categories in your driver list
            </p>
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 p-5">
            <h2 className="text-lg font-bold text-slate-900">
              All Drivers
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Driver records retrieved from your backend.
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
              Loading drivers...
            </p>
          ) : error ? null : drivers.length === 0 ? (
            <p className="p-8 text-center text-slate-500">
              No drivers found. Click Add Driver to register one.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-5 py-4">Driver ID</th>
                    <th className="px-5 py-4">Driver</th>
                    <th className="px-5 py-4">License Category</th>
                    <th className="px-5 py-4">Experience</th>
                    <th className="px-5 py-4">Working Hours</th>
                    <th className="px-5 py-4">Rest Hours</th>
                    <th className="px-5 py-4">Company ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {drivers.map((driver) => (
                    <tr
                      key={driver.id ?? driver.driver_id}
                      className="hover:bg-slate-50"
                    >
                      
<td className="px-5 py-4">
  {driver.id ?? driver.driver_id ?? "—"}
</td>

<td className="px-5 py-4 font-semibold text-slate-900">
  {driver.name ?? "—"}
</td>

                      <td className="px-5 py-4 text-slate-600">
                        {driver.license_category ?? "—"}
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {driver.experience_years ?? 0} years
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {driver.working_hours ?? 0}
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {driver.rest_hours ?? 0}
                      </td>
                      <td className="px-5 py-4 text-slate-600">
                        {driver.company_id ?? "—"}
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
