import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Dashboard() {
  const { token, userEmail, userRole, isAdmin } = useContext(AuthContext);
  const [recentBookings, setRecentBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    // Redirect admin users to admin dashboard
    if (isAdmin) {
      navigate("/admin/dashboard");
      return;
    }

    // Load user's recent bookings
    loadUserData();
  }, [token, navigate, isAdmin]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      // For now, we'll use mock data. Later integrate with your backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setRecentBookings([
        {
          id: 1,
          slot_number: "A1",
          station_name: "Downtown Station",
          start_time: "2024-01-15T10:00:00",
          duration: 2,
          total_cost: 10,
          status: "active"
        },
        {
          id: 2,
          slot_number: "B3",
          station_name: "Airport Station",
          start_time: "2024-01-14T14:00:00",
          duration: 4,
          total_cost: 20,
          status: "completed"
        }
      ]);
    } catch (error) {
      console.error("Failed to load user data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return null;
  }

  if (isAdmin) {
    return null; // Will redirect to admin dashboard
  }

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

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'var(--success)';
      case 'completed': return 'var(--muted)';
      case 'cancelled': return 'var(--error)';
      default: return 'var(--muted)';
    }
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Welcome back, {userEmail?.split('@')[0] || 'User'}! 👋</h1>
          <div className="lead">Quick access to your parking needs</div>
        </div>
        <div className="user-role-badge">
          👤 Regular User
        </div>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading your dashboard...</div>
        </div>
      )}

      {!loading && (
        <>
          {/* Quick Actions - Only Essential Features */}
          <div className="actions-section">
            <h2>Quick Actions</h2>
            <div className="actions-grid">
              <ActionCard
                title="Find Parking"
                description="Browse available parking slots at all stations"
                icon="🔍"
                buttonText="Find Slots"
                onClick={() => navigate("/stations")}
                color="var(--accent-light)"
              />

              <ActionCard
                title="Book Parking"
                description="Reserve a parking slot for your vehicle"
                icon="🅿️"
                buttonText="Book Now"
                onClick={() => navigate("/booking")}
                color="var(--success)"
              />
              
              <ActionCard
                title="My Bookings"
                description="View and manage your parking reservations"
                icon="📋"
                buttonText="View Bookings"
                onClick={() => navigate("/my-bookings")}
                color="var(--accent)"
              />
            </div>
          </div>

          {/* Recent Bookings - Only if user has any */}
          {recentBookings.length > 0 && (
            <div className="recent-bookings">
              <h2>Recent Bookings</h2>
              <div className="bookings-list">
                {recentBookings.slice(0, 3).map((booking) => (
                  <div key={booking.id} className="booking-item">
                    <div className="booking-header">
                      <div className="booking-slot">{booking.slot_number}</div>
                      <div 
                        className="booking-status" 
                        style={{ backgroundColor: getStatusColor(booking.status) }}
                      >
                        {booking.status}
                      </div>
                    </div>
                    
                    <div className="booking-details">
                      <div className="booking-station">{booking.station_name}</div>
                      <div className="booking-time">
                        {formatDateTime(booking.start_time)} • {booking.duration}h
                      </div>
                      <div className="booking-cost">${booking.total_cost}</div>
                    </div>
                    
                    <div className="booking-actions">
                      <button 
                        className="btn small"
                        onClick={() => navigate(`/my-bookings/${booking.id}`)}
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              {recentBookings.length > 3 && (
                <div className="view-all-bookings">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => navigate("/my-bookings")}
                  >
                    View All Bookings
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Empty State for New Users */}
          {recentBookings.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">🚗</div>
              <h3>No bookings yet</h3>
              <p>Start by finding and booking your first parking slot!</p>
              <button 
                className="btn"
                onClick={() => navigate("/booking")}
              >
                Book Your First Slot
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
} 