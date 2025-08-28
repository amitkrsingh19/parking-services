import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { parkingAPI, bookingAPI } from "../api/client";

export default function UserBooking() {
  const { token, userEmail } = useContext(AuthContext);
  const [stations, setStations] = useState([]);
  const [allSlots, setAllSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedStation, setSelectedStation] = useState(null);
  const navigate = useNavigate();

  const [bookingData, setBookingData] = useState({
    start_time: "",
    duration: 1,
    vehicle_number: "",
    vehicle_type: "car"
  });

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    fetchAllData();
  }, [token, navigate]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      setError("");
      
      // Fetch all stations
      const stationsResponse = await parkingAPI.getStations();
      let allStations = [];
      
      if (Array.isArray(stationsResponse)) {
        allStations = stationsResponse;
      } else if (stationsResponse && Array.isArray(stationsResponse.stations)) {
        allStations = stationsResponse.stations;
      }
      
      setStations(allStations);
      
      // Fetch all available slots from all stations
      const allAvailableSlots = [];
      
      for (const station of allStations) {
        try {
          const stationId = station._id || station.id;
          const slotsResponse = await parkingAPI.getSlotsByStation(stationId);
          
          if (Array.isArray(slotsResponse)) {
            const availableSlots = slotsResponse
              .filter(slot => slot.is_available && slot.status !== "occupied")
              .map(slot => ({
                ...slot,
                station_name: station.name || station.station_name,
                station_location: station.location || station.address,
                station_id: stationId
              }));
            
            allAvailableSlots.push(...availableSlots);
          }
        } catch (slotError) {
          console.error(`Failed to fetch slots for station ${station.name}:`, slotError);
        }
      }
      
      setAllSlots(allAvailableSlots);
      
    } catch (err) {
      console.error("Failed to fetch data:", err);
      setError("Failed to load stations and slots");
    } finally {
      setLoading(false);
    }
  };

  const handleSlotSelection = (slot) => {
    setSelectedSlot(slot);
    setSelectedStation(stations.find(s => s._id === slot.station_id || s.id === slot.station_id));
    setShowBookingForm(true);
    
    // Pre-fill duration-based cost
    setBookingData(prev => ({
      ...prev,
      estimated_cost: slot.price_per_hour * prev.duration
    }));
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedSlot) {
      setError("Please select a parking slot");
      return;
    }

    if (!bookingData.vehicle_number.trim()) {
      setError("Vehicle number is required");
      return;
    }

    try {
      // Call backend API to create booking
      const bookingPayload = {
        slot_id: selectedSlot._id || selectedSlot.id,
        station_id: selectedSlot.station_id,
        user_email: userEmail,
        start_time: bookingData.start_time,
        duration: bookingData.duration,
        vehicle_number: bookingData.vehicle_number,
        vehicle_type: bookingData.vehicle_type,
        total_cost: selectedSlot.price_per_hour * bookingData.duration
      };

      const response = await bookingAPI.createBooking(bookingPayload);
      
      if (response) {
        // Show success and redirect
        alert(`Booking confirmed! Your slot ${selectedSlot.slot_number} at ${selectedSlot.station_name} is reserved.`);
        navigate("/my-bookings");
      }
      
    } catch (error) {
      console.error("Failed to create booking:", error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else if (error.message) {
        setError(error.message);
      } else {
        setError("Failed to create booking. Please check your connection and try again.");
      }
    }
  };

  const updateDuration = (duration) => {
    setBookingData(prev => ({
      ...prev,
      duration: parseInt(duration),
      estimated_cost: selectedSlot ? selectedSlot.price_per_hour * parseInt(duration) : 0
    }));
  };

  if (!token) {
    return null;
  }

  const getSlotTypeColor = (type) => {
    switch (type) {
      case "premium": return "var(--warning)";
      case "disabled": return "var(--muted)";
      default: return "var(--success)";
    }
  };

  const groupSlotsByStation = () => {
    const grouped = {};
    allSlots.forEach(slot => {
      const stationKey = slot.station_id;
      if (!grouped[stationKey]) {
        grouped[stationKey] = {
          station: stations.find(s => s._id === stationKey || s.id === stationKey),
          slots: []
        };
      }
      grouped[stationKey].slots.push(slot);
    });
    return grouped;
  };

  const groupedSlots = groupSlotsByStation();

  return (
    <div className="user-booking-page">
      <div className="page-header">
        <div>
          <h1>Book Parking Slot 🅿️</h1>
          <div className="lead">Find and reserve available parking slots</div>
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
          <div className="loading-text">Loading available slots...</div>
        </div>
      )}

      {error && (
        <div className="error">
          {error}
          <button 
            className="btn small" 
            onClick={fetchAllData}
            style={{ marginLeft: "12px" }}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Available Slots by Station */}
          <div className="available-slots">
            <h2>Available Slots</h2>
            
            {Object.keys(groupedSlots).length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🚗</div>
                <h3>No available slots found</h3>
                <p>All parking slots are currently occupied. Please check back later.</p>
              </div>
            ) : (
              Object.entries(groupedSlots).map(([stationId, stationData]) => (
                <div key={stationId} className="station-slots-section">
                  <div className="station-header">
                    <h3>{stationData.station?.name || stationData.station?.station_name}</h3>
                    <div className="station-location">
                      📍 {stationData.station?.location || stationData.station?.address}
                    </div>
                  </div>
                  
                  <div className="slots-grid">
                    {stationData.slots.map((slot) => (
                      <div key={slot._id || slot.id} className="slot-card available">
                        <div className="slot-header">
                          <div className="slot-number">{slot.slot_number}</div>
                          <div className="slot-type" style={{ color: getSlotTypeColor(slot.slot_type) }}>
                            {slot.slot_type.charAt(0).toUpperCase() + slot.slot_type.slice(1)}
                          </div>
                        </div>
                        
                        <div className="slot-details">
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
                            className="btn"
                            onClick={() => handleSlotSelection(slot)}
                          >
                            Book This Slot
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Simplified Booking Form */}
          {showBookingForm && selectedSlot && selectedStation && (
            <div className="booking-form">
              <h2>Complete Your Booking</h2>
              <div className="booking-summary">
                <h3>Selected Slot: {selectedSlot.slot_number}</h3>
                <p><strong>Station:</strong> {selectedStation.name || selectedStation.station_name}</p>
                <p><strong>Price:</strong> ${selectedSlot.price_per_hour}/hour</p>
              </div>
              
              <form onSubmit={handleBookingSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label className="field-label">Start Time *</label>
                    <input 
                      className="input" 
                      type="datetime-local"
                      value={bookingData.start_time}
                      onChange={(e) => setBookingData(prev => ({ ...prev, start_time: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label className="field-label">Duration (hours) *</label>
                    <select 
                      className="input"
                      value={bookingData.duration}
                      onChange={(e) => updateDuration(e.target.value)}
                    >
                      <option value={1}>1 hour</option>
                      <option value={2}>2 hours</option>
                      <option value={4}>4 hours</option>
                      <option value={8}>8 hours</option>
                      <option value={24}>24 hours</option>
                    </select>
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label className="field-label">Vehicle Number *</label>
                    <input 
                      className="input" 
                      value={bookingData.vehicle_number}
                      onChange={(e) => setBookingData(prev => ({ ...prev, vehicle_number: e.target.value }))}
                      placeholder="e.g., ABC-1234"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label className="field-label">Vehicle Type</label>
                    <select 
                      className="input"
                      value={bookingData.vehicle_type}
                      onChange={(e) => setBookingData(prev => ({ ...prev, vehicle_type: e.target.value }))}
                    >
                      <option value="car">Car</option>
                      <option value="motorcycle">Motorcycle</option>
                      <option value="truck">Truck</option>
                      <option value="van">Van</option>
                    </select>
                  </div>
                </div>
                
                <div className="cost-summary">
                  <h3>Total Cost</h3>
                  <div className="cost-breakdown">
                    <div className="cost-item total">
                      <span>Total:</span>
                      <span>${selectedSlot.price_per_hour * bookingData.duration}</span>
                    </div>
                  </div>
                </div>
                
                <div className="form-actions">
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => setShowBookingForm(false)}
                  >
                    Cancel
                  </button>
                  <button className="btn" type="submit">
                    Confirm Booking
                  </button>
                </div>
              </form>
            </div>
          )}
        </>
      )}
    </div>
  );
} 