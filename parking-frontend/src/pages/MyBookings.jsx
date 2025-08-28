import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { bookingAPI } from "../api/client";

export default function MyBookings() {
  const { token, userEmail } = useContext(AuthContext);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    fetchUserBookings();
  }, [token, navigate]);

  const fetchUserBookings = async () => {
    try {
      setLoading(true);
      setError("");
      
      // For now, we'll use mock data. Later integrate with your backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setBookings([
        {
          id: 1,
          slot_number: "A1",
          station_name: "Downtown Station",
          start_time: "2024-01-15T10:00:00",
          duration: 2,
          total_cost: 10,
          status: "active",
          vehicle_number: "ABC-1234",
          vehicle_type: "car"
        },
        {
          id: 2,
          slot_number: "B3",
          station_name: "Airport Station",
          start_time: "2024-01-14T14:00:00",
          duration: 4,
          total_cost: 20,
          status: "completed",
          vehicle_number: "XYZ-789",
          vehicle_type: "car"
        },
        {
          id: 3,
          slot_number: "C2",
          station_name: "Mall Station",
          start_time: "2024-01-13T09:00:00",
          duration: 1,
          total_cost: 5,
          status: "cancelled",
          vehicle_number: "DEF-456",
          vehicle_type: "motorcycle"
        }
      ]);
      
    } catch (error) {
      console.error("Failed to fetch bookings:", error);
      setError("Failed to load your bookings");
    } finally {
      setLoading(false);
    }
  };

  const cancelBooking = async (bookingId) => {
    if (window.confirm("Are you sure you want to cancel this booking?")) {
      try {
        // Call backend API to cancel booking
        await bookingAPI.cancelBooking(bookingId);
        
        // Update local state
        setBookings(prev => prev.map(booking => 
          booking.id === bookingId 
            ? { ...booking, status: "cancelled" }
            : booking
        ));
        
        alert("Booking cancelled successfully!");
      } catch (error) {
        console.error("Failed to cancel booking:", error);
        alert("Failed to cancel booking. Please try again.");
      }
    }
  };

  if (!token) {
    return null;
  }

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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return '✅';
      case 'completed': return '🏁';
      case 'cancelled': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="my-bookings-page">
      <div className="page-header">
        <div>
          <h1>My Bookings 📋</h1>
          <div className="lead">View and manage your parking reservations</div>
        </div>
        <button 
          className="btn"
          onClick={() => navigate("/dashboard")}
        >
          ← Back to Dashboard
        </button>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading your bookings...</div>
        </div>
      )}

      {error && (
        <div className="error">
          {error}
          <button 
            className="btn small" 
            onClick={fetchUserBookings}
            style={{ marginLeft: "12px" }}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {bookings.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <h3>No bookings found</h3>
              <p>You haven't made any parking reservations yet.</p>
              <button 
                className="btn"
                onClick={() => navigate("/booking")}
              >
                Book Your First Slot
              </button>
            </div>
          ) : (
            <div className="bookings-container">
              <div className="bookings-header">
                <h2>Your Parking Reservations</h2>
                <div className="bookings-count">
                  {bookings.length} booking{bookings.length !== 1 ? 's' : ''}
                </div>
              </div>
              
              <div className="bookings-list">
                {bookings.map((booking) => (
                  <div key={booking.id} className="booking-card">
                    <div className="booking-header">
                      <div className="booking-slot">
                        <span className="slot-number">{booking.slot_number}</span>
                        <span className="slot-station">{booking.station_name}</span>
                      </div>
                      <div 
                        className="booking-status" 
                        style={{ backgroundColor: getStatusColor(booking.status) }}
                      >
                        {getStatusIcon(booking.status)} {booking.status}
                      </div>
                    </div>
                    
                    <div className="booking-details">
                      <div className="detail-row">
                        <span className="detail-label">Date & Time:</span>
                        <span className="detail-value">{formatDateTime(booking.start_time)}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Duration:</span>
                        <span className="detail-value">{booking.duration} hour{booking.duration !== 1 ? 's' : ''}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Vehicle:</span>
                        <span className="detail-value">{booking.vehicle_number} ({booking.vehicle_type})</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Total Cost:</span>
                        <span className="detail-value cost">${booking.total_cost}</span>
                      </div>
                    </div>
                    
                    <div className="booking-actions">
                      {booking.status === 'active' && (
                        <button 
                          className="btn small"
                          style={{ backgroundColor: "var(--error)" }}
                          onClick={() => cancelBooking(booking.id)}
                        >
                          Cancel Booking
                        </button>
                      )}
                      
                      <button 
                        className="btn small btn-secondary"
                        onClick={() => navigate(`/my-bookings/${booking.id}`)}
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
} 