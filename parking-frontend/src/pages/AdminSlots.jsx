import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { parkingAPI } from "../api/client";

export default function AdminSlots() {
  const { token, userEmail, isAdmin } = useContext(AuthContext);
  const [adminStation, setAdminStation] = useState(null);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddSlotForm, setShowAddSlotForm] = useState(false);
  const navigate = useNavigate();

  const [newSlot, setNewSlot] = useState({
    slot_number: "",
    slot_type: "standard",
    price_per_hour: "",
    is_available: true,
    features: []
  });

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    if (!isAdmin) {
      navigate("/dashboard");
      return;
    }

    fetchAdminStation();
  }, [token, navigate, isAdmin]);

  useEffect(() => {
    if (adminStation) {
      fetchSlots(adminStation._id || adminStation.id);
    }
  }, [adminStation]);

  const fetchAdminStation = async () => {
    try {
      setLoading(true);
      setError("");
      
      // Get all stations and find the one owned by this admin
      const response = await parkingAPI.getStations();
      let allStations = [];
      
      if (Array.isArray(response)) {
        allStations = response;
      } else if (response && Array.isArray(response.stations)) {
        allStations = response.stations;
      }
      
      // Find station owned by this admin
      const adminOwnedStation = allStations.find(station => 
        station.posted_by === userEmail || station.admin_id === userEmail
      );
      
      if (!adminOwnedStation) {
        setError("You don't have a parking station yet. Please create one first.");
        return;
      }
      
      setAdminStation(adminOwnedStation);
      
    } catch (err) {
      console.error("Failed to fetch admin station:", err);
      setError("Failed to load your station");
    } finally {
      setLoading(false);
    }
  };

  const fetchSlots = async (stationId) => {
    try {
      // Call backend API to get slots for this station
      const response = await parkingAPI.getSlotsByStation(stationId);
      
      if (Array.isArray(response)) {
        setSlots(response);
      } else if (response && Array.isArray(response.slots)) {
        setSlots(response.slots);
      } else {
        setSlots([]);
      }
    } catch (error) {
      console.error("Failed to fetch slots:", error);
      setError("Failed to load slots");
    }
  };

  const handleAddSlot = async (e) => {
    e.preventDefault();
    
    if (!newSlot.slot_number.trim()) {
      setError("Slot number is required");
      return;
    }

    try {
      // Call backend API to add slot
      const slotData = {
        ...newSlot,
        price_per_hour: parseFloat(newSlot.price_per_hour) || 0,
        station_id: adminStation._id || adminStation.id,
        admin_id: userEmail
      };

      const response = await parkingAPI.addSlot(slotData);
      
      if (response) {
        // Refresh slots list
        await fetchSlots(adminStation._id || adminStation.id);
        
        // Reset form
        setNewSlot({
          slot_number: "",
          slot_type: "standard",
          price_per_hour: "",
          is_available: true,
          features: []
        });
        setShowAddSlotForm(false);
      }
    } catch (error) {
      console.error("Failed to add slot:", error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError("Failed to add slot");
      }
    }
  };

  const toggleSlotAvailability = async (slotId) => {
    try {
      // Call backend API to toggle slot availability
      await parkingAPI.toggleSlotAvailability(slotId);
      
      // Refresh slots list
      await fetchSlots(adminStation._id || adminStation.id);
    } catch (error) {
      console.error("Failed to update slot:", error);
      setError("Failed to update slot availability");
    }
  };

  const deleteSlot = async (slotId) => {
    if (window.confirm("Are you sure you want to delete this slot?")) {
      try {
        // Call backend API to delete slot
        await parkingAPI.deleteSlot(slotId);
        
        // Refresh slots list
        await fetchSlots(adminStation._id || adminStation.id);
      } catch (error) {
        console.error("Failed to delete slot:", error);
        setError("Failed to delete slot");
      }
    }
  };

  if (!token || !isAdmin) {
    return null;
  }

  if (!adminStation) {
    return (
      <div className="admin-slots-page">
        <div className="page-header">
          <div>
            <h1>Manage Parking Slots 🚗</h1>
            <div className="lead">Configure and manage parking slots for your station</div>
          </div>
          <button 
            className="btn"
            onClick={() => navigate("/admin/dashboard")}
          >
            ← Back to Admin
          </button>
        </div>
        
        <div className="error">
          You don't have a parking station yet. Please create one first.
          <button 
            className="btn"
            onClick={() => navigate("/stations/new")}
            style={{ marginLeft: "12px" }}
          >
            Create Station
          </button>
        </div>
      </div>
    );
  }

  const getSlotTypeColor = (type) => {
    switch (type) {
      case "premium": return "var(--warning)";
      case "disabled": return "var(--muted)";
      default: return "var(--success)";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "available": return "var(--success)";
      case "occupied": return "var(--error)";
      case "maintenance": return "var(--warning)";
      default: return "var(--muted)";
    }
  };

  return (
    <div className="admin-slots-page">
      <div className="page-header">
        <div>
          <h1>Manage Parking Slots 🚗</h1>
          <div className="lead">
            Managing slots for: <strong>{adminStation.name || adminStation.station_name}</strong>
          </div>
        </div>
        <button 
          className="btn"
          onClick={() => navigate("/admin/dashboard")}
        >
          ← Back to Admin
        </button>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading your station...</div>
        </div>
      )}

      {error && (
        <div className="error">
          {error}
          <button 
            className="btn small" 
            onClick={fetchAdminStation}
            style={{ marginLeft: "12px" }}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && adminStation && (
        <>
          {/* Station Info */}
          <div className="station-info">
            <h2>Station Information</h2>
            <div className="station-details-card">
              <div className="station-detail">
                <span className="detail-label">Name:</span>
                <span className="detail-value">{adminStation.name || adminStation.station_name}</span>
              </div>
              <div className="station-detail">
                <span className="detail-label">Location:</span>
                <span className="detail-value">{adminStation.location || adminStation.address}</span>
              </div>
              <div className="station-detail">
                <span className="detail-label">Total Slots:</span>
                <span className="detail-value">{slots.length}</span>
              </div>
            </div>
          </div>

          {/* Slots Management */}
          <div className="slots-management">
            <div className="slots-header">
              <h2>Parking Slots</h2>
              <button 
                className="btn"
                onClick={() => setShowAddSlotForm(true)}
              >
                ➕ Add New Slot
              </button>
            </div>

            {/* Add Slot Form */}
            {showAddSlotForm && (
              <div className="add-slot-form">
                <h3>Add New Parking Slot</h3>
                <form onSubmit={handleAddSlot}>
                  <div className="form-row">
                    <div className="form-group">
                      <label className="field-label">Slot Number *</label>
                      <input 
                        className="input" 
                        value={newSlot.slot_number}
                        onChange={(e) => setNewSlot(prev => ({ ...prev, slot_number: e.target.value }))}
                        placeholder="e.g., A1, B2, C3"
                        required
                      />
                    </div>
                    
                    <div className="form-group">
                      <label className="field-label">Slot Type</label>
                      <select 
                        className="input"
                        value={newSlot.slot_type}
                        onChange={(e) => setNewSlot(prev => ({ ...prev, slot_type: e.target.value }))}
                      >
                        <option value="standard">Standard</option>
                        <option value="premium">Premium</option>
                        <option value="disabled">Disabled Access</option>
                        <option value="electric">Electric Vehicle</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label className="field-label">Price per Hour ($)</label>
                      <input 
                        className="input" 
                        type="number"
                        step="0.01"
                        min="0"
                        value={newSlot.price_per_hour}
                        onChange={(e) => setNewSlot(prev => ({ ...prev, price_per_hour: e.target.value }))}
                        placeholder="5.00"
                      />
                    </div>
                  </div>
                  
                  <div className="form-actions">
                    <button 
                      type="button" 
                      className="btn btn-secondary"
                      onClick={() => setShowAddSlotForm(false)}
                    >
                      Cancel
                    </button>
                    <button className="btn" type="submit">
                      Add Slot
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Slots List */}
            <div className="slots-grid">
              {slots.length === 0 ? (
                <div className="empty-slots">
                  <div className="empty-icon">🚗</div>
                  <h3>No slots created yet</h3>
                  <p>Start by adding your first parking slot to this station.</p>
                </div>
              ) : (
                slots.map((slot) => (
                  <div key={slot._id || slot.id} className="slot-card">
                    <div className="slot-header">
                      <div className="slot-number">{slot.slot_number}</div>
                      <div className="slot-status" style={{ backgroundColor: getStatusColor(slot.status || "available") }}>
                        {slot.status || "available"}
                      </div>
                    </div>
                    
                    <div className="slot-details">
                      <div className="slot-type" style={{ color: getSlotTypeColor(slot.slot_type) }}>
                        {slot.slot_type.charAt(0).toUpperCase() + slot.slot_type.slice(1)}
                      </div>
                      <div className="slot-price">${slot.price_per_hour}/hour</div>
                      {slot.features && slot.features.length > 0 && (
                        <div className="slot-features">
                          {slot.features.map((feature, index) => (
                            <span key={index} className="feature-tag">{feature}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="slot-actions">
                      <button 
                        className={`btn small ${slot.is_available ? 'btn-secondary' : 'btn-success'}`}
                        onClick={() => toggleSlotAvailability(slot._id || slot.id)}
                      >
                        {slot.is_available ? 'Disable' : 'Enable'}
                      </button>
                      <button 
                        className="btn small"
                        onClick={() => navigate(`/admin/slots/${slot._id || slot.id}/edit`)}
                      >
                        Edit
                      </button>
                      <button 
                        className="btn small"
                        style={{ backgroundColor: "var(--error)" }}
                        onClick={() => deleteSlot(slot._id || slot.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
} 