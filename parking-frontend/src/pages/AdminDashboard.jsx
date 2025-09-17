import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { parkingAPI } from "../api/client";

export default function AdminDashboard() {
  const { token, userEmail, userRole, isAdmin } = useContext(AuthContext);
  const [adminStats, setAdminStats] = useState({
    totalStations: 0,
    totalSlots: 0,
    totalBookings: 0,
    revenue: 0
  });
  const [hasStation, setHasStation] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    if (!isAdmin) {
      navigate("/dashboard");
      return;
    }

    fetchAdminData();
  }, [token, navigate, isAdmin]);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      setError("");
      
      // Check if admin already has a station
      const stationsResponse = await parkingAPI.getStations();
      let userStations = [];
      
      if (Array.isArray(stationsResponse)) {
        userStations = stationsResponse;
      } else if (stationsResponse && Array.isArray(stationsResponse.stations)) {
        userStations = stationsResponse.stations;
      }
      
      // Filter stations owned by this admin
      const adminStations = userStations.filter(station => 
        station.posted_by === userEmail || station.admin_id === userEmail
      );
      
      setHasStation(adminStations.length > 0);
      
      if (hasStation) {
        // Fetch stats for admin's station
        const stationId = adminStations[0]._id || adminStations[0].id;
        const slotsResponse = await parkingAPI.getSlotsByStation(stationId);
        const bookingsResponse = await parkingAPI.getBookingsByStation(stationId);
        
        setAdminStats({
          totalStations: adminStations.length,
          totalSlots: slotsResponse?.length || 0,
          totalBookings: bookingsResponse?.length || 0,
          revenue: calculateRevenue(bookingsResponse || [])
        });
      }
      
    } catch (error) {
      console.error("Failed to fetch admin data:", error);
      setError("Failed to load admin data");
    } finally {
      setLoading(false);
    }
  };

  const calculateRevenue = (bookings) => {
    return bookings.reduce((total, booking) => total + (booking.total_cost || 0), 0);
  };

  if (!token || !isAdmin) {
    return null;
  }

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <div className="stat-card" style={{ borderLeftColor: color }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-value">{value}</div>
        <div className="stat-title">{title}</div>
        {subtitle && <div className="stat-subtitle">{subtitle}</div>}
      </div>
    </div>
  );

  const ActionCard = ({ title, description, icon, buttonText, onClick, color = "primary" }) => (
    <div className="action-card">
      <div className="action-icon" style={{ backgroundColor: color }}>
        {icon}
      </div>
      <div className="action-content">
        <h3>{title}</h3>
        <p>{description}</p>
        <button className="btn" onClick={onClick}>
          {buttonText}
        </button>
      </div>
    </div>
  );

  return (
    <div className="admin-dashboard-page">
      <div className="admin-header">
        <div>
          <h1>Admin Dashboard 👑</h1>
          <div className="lead">Manage your parking system and monitor performance</div>
        </div>
        <div className="admin-info">
          <span className="admin-badge">Administrator</span>
          <span className="admin-email">{userEmail}</span>
        </div>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading admin dashboard...</div>
        </div>
      )}

      {error && (
        <div className="error">
          {error}
          <button 
            className="btn small" 
            onClick={fetchAdminData}
            style={{ marginLeft: "12px" }}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Station Status */}
          <div className="station-status">
            <h2>Station Status</h2>
            {hasStation ? (
              <div className="status-card success">
                <div className="status-icon">✅</div>
                <div className="status-content">
                  <h3>Station Active</h3>
                  <p>You have successfully created your parking station. You can now manage slots and monitor bookings.</p>
                </div>
              </div>
            ) : (
              <div className="status-card warning">
                <div className="status-icon">⚠️</div>
                <div className="status-content">
                  <h3>No Station Created</h3>
                  <p>You need to create your parking station first before you can manage slots.</p>
                  <button 
                    className="btn"
                    onClick={() => navigate("/stations/new")}
                  >
                    Create Your First Station
                  </button>
                </div>
              </div>
            )}
          </div>

          {hasStation && (
            <>
              {/* Admin Statistics */}
              <div className="stats-section">
                <h2>Your Station Overview</h2>
                <div className="stats-grid">
                  <StatCard
                    title="Total Slots"
                    value={adminStats.totalSlots}
                    icon="🚗"
                    color="var(--success)"
                    subtitle="Available for booking"
                  />
                  <StatCard
                    title="Total Bookings"
                    value={adminStats.totalBookings}
                    icon="📅"
                    color="var(--warning)"
                    subtitle="This month"
                  />
                  <StatCard
                    title="Revenue"
                    value={`$${adminStats.revenue}`}
                    icon="💰"
                    color="var(--accent)"
                    subtitle="This month"
                  />
                </div>
              </div>

              {/* Admin Actions */}
              <div className="actions-section">
                <h2>Management Actions</h2>
                <div className="actions-grid">
                  <ActionCard
                    title="Manage Slots"
                    description="Add, edit, or remove parking slots in your station"
                    icon="🚗"
                    buttonText="Manage Slots"
                    onClick={() => navigate("/admin/slots")}
                    color="var(--success)"
                  />
                  
                  <ActionCard
                    title="View Bookings"
                    description="Monitor all parking bookings for your station"
                    icon="📋"
                    buttonText="View Bookings"
                    onClick={() => navigate("/admin/bookings")}
                    color="var(--warning)"
                  />
                  
                  <ActionCard
                    title="Station Analytics"
                    description="View detailed reports on usage and revenue"
                    icon="📊"
                    buttonText="View Analytics"
                    onClick={() => navigate("/admin/analytics")}
                    color="var(--accent)"
                  />
                </div>
              </div>

              {/* Quick Actions */}
              <div className="quick-actions">
                <h2>Quick Actions</h2>
                <div className="quick-actions-grid">
                  <button 
                    className="btn quick-action-btn"
                    onClick={() => navigate("/admin/slots")}
                  >
                    🚗 Manage Slots
                  </button>
                  
                  <button 
                    className="btn quick-action-btn"
                    onClick={() => navigate("/admin/bookings")}
                  >
                    📋 View Bookings
                  </button>
                  
                  <button 
                    className="btn quick-action-btn"
                    onClick={() => navigate("/admin/analytics")}
                  >
                    📊 View Analytics
                  </button>
                </div>
              </div>
            </>
          )}

          {/* Recent Activity */}
          <div className="recent-activity">
            <h2>Recent System Activity</h2>
            <div className="activity-list">
              {hasStation ? (
                <>
                  <div className="activity-item">
                    <div className="activity-icon">🚗</div>
                    <div className="activity-content">
                      <div className="activity-title">New booking received</div>
                      <div className="activity-desc">User booked slot A1 at your station</div>
                      <div className="activity-time">5 minutes ago</div>
                    </div>
                  </div>
                  
                  <div className="activity-item">
                    <div className="activity-icon">✅</div>
                    <div className="activity-content">
                      <div className="activity-title">Payment completed</div>
                      <div className="activity-desc">$25 payment received for booking #1234</div>
                      <div className="activity-time">15 minutes ago</div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="activity-item">
                  <div className="activity-icon">🏢</div>
                  <div className="activity-content">
                    <div className="activity-title">Ready to start</div>
                    <div className="activity-desc">Create your first parking station to begin managing the system</div>
                    <div className="activity-time">Just now</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
} 