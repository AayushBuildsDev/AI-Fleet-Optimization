
import { NavLink, Outlet } from "react-router-dom";
import {
  Truck,
  LayoutDashboard,
  Users,
  Package,
  Route,
  MapPin,
  Fuel,
  Settings,
} from "lucide-react";

const navigation = [
  { label: "Dashboard", path: "/", icon: LayoutDashboard },
  { label: "Trucks", path: "/trucks", icon: Truck },
  { label: "Drivers", path: "/drivers", icon: Users },
  { label: "Orders", path: "/orders", icon: Package },
  { label: "Trips", path: "/trips", icon: Route },
  { label: "GPS Tracking", path: "/gps-tracking", icon: MapPin },
  { label: "Optimization", path: "/optimization", icon: Fuel },
];

export default function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 md:flex">
      <aside className="w-full shrink-0 border-b border-slate-200 bg-white p-5 md:min-h-screen md:w-64 md:border-b-0 md:border-r">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-blue-600 text-white">
            <Truck size={24} />
          </div>

          <div>
            <h1 className="font-bold text-slate-900">FleetAI</h1>
            <p className="text-xs text-slate-500">Fleet management</p>
          </div>
        </div>

        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
          Workspace
        </p>

        <nav className="grid grid-cols-2 gap-2 md:grid-cols-1">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={label}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ${
                  isActive
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-8 hidden rounded-2xl bg-slate-50 p-4 md:block">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
            <Fuel size={17} className="text-blue-600" />
            Smart optimization
          </div>

          <p className="text-xs leading-5 text-slate-500">
            Plan loads and routes with your optimization engine.
          </p>
        </div>

        <div className="mt-5 flex items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-500 md:mt-8">
          <Settings size={18} />
          Settings
        </div>
      </aside>

      <main className="min-w-0 flex-1">
        <Outlet />
      </main>
    </div>
  );
}
