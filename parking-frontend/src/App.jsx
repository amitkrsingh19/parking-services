import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AdminDashboard from "./pages/AdminDashboard";
import AdminSlots from "./pages/AdminSlots";
import UserBooking from "./pages/UserBooking";
import MyBookings from "./pages/MyBookings";
import Stations from "./pages/Stations";
import Register from "./pages/Register";
import AddStation from "./pages/AddStation";
import Navbar from "./components/Navbar";
import { useContext } from "react";
import { AuthContext } from "./context/AuthContext";

export default function App() {
  const { token, isAdmin } = useContext(AuthContext);

  return (
    <div className="app-root">
      <Navbar />
      <main>
        <Routes>
          <Route
            path="/"
            element={<Navigate to={token ? "/dashboard" : "/login"} replace />}
          />
          <Route
            path="/login"
            element={token ? <Navigate to="/dashboard" replace /> : <Login />}
          />
          <Route
            path="/register"
            element={token ? <Navigate to="/dashboard" replace /> : <Register />}
          />

          {/* Dashboard Routes */}
          <Route
            path="/dashboard"
            element={token ? <Dashboard /> : <Navigate to="/login" replace />}
          />

          {/* Admin Routes */}
          <Route
            path="/admin/dashboard"
            element={token && isAdmin ? <AdminDashboard /> : <Navigate to="/dashboard" replace />}
          />
          <Route
            path="/admin/slots"
            element={token && isAdmin ? <AdminSlots /> : <Navigate to="/dashboard" replace />}
          />
          <Route
            path="/admin/slots/new"
            element={token && isAdmin ? <AdminSlots /> : <Navigate to="/dashboard" replace />}
          />

          {/* User Routes */}
          <Route
            path="/booking"
            element={token ? <UserBooking /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/my-bookings"
            element={token ? <MyBookings /> : <Navigate to="/login" replace />}
          />

          {/* Station Routes */}
          <Route
            path="/stations"
            element={token ? <Stations /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/stations/new"
            element={token && isAdmin ? <AddStation /> : <Navigate to="/dashboard" replace />}
          />
        </Routes>
      </main>
    </div>
  );
}
