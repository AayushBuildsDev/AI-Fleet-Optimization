
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Trucks from "./pages/Trucks";
import Drivers from "./pages/Drivers";
import Orders from "./pages/Orders";
import Optimization from "./pages/Optimization";
import Trips from "./pages/Trips";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trucks" element={<Trucks />} />
          <Route path="/drivers" element={<Drivers />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/optimization" element={<Optimization />} />
          <Route path="/trips" element={<Trips />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
