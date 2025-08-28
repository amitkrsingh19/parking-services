import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { parkingAPI } from "../api/client";

export default function Stations() {
  const { token } = useContext(AuthContext);
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    
    const fetchStations = async () => {
      try {
        setLoading(true);
        setError("");
        
        // Call real backend API
        const response = await parkingAPI.getStations();
        
        // Handle different response formats
        if (Array.isArray(response)) {
          setStations(response);
        } else if (response && Array.isArray(response.stations)) {
          setStations(response.stations);
        } else if (response && response.data && Array.isArray(response.data)) {
          setStations(response.data);
        } else {
          setStations([]);
        }
      } catch (err) {
        console.error("Failed to fetch stations:", err);
        
        if (err.response?.status === 401) {
          navigate("/login");
          return;
        } else if (err.response?.status === 403) {
          setError("You don't have permission to view stations");
        } else if (err.response?.data?.detail) {
          setError(err.response.data.detail);
        } else {
          setError("Failed to load stations. Please check your connection and try again.");
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchStations();
  }, [token, navigate]);

  if (!token) {
    return null;
  }

  const getAvailabilityColor = (slots, capacity) => {
    if (capacity === 0) return "var(--muted)";
    const percentage = (slots / capacity) * 100;
    if (percentage >= 80) return "var(--error)";
    if (percentage >= 60) return "var(--warning)";
    return "var(--success)";
  };

  const getAvailabilityText = (slots, capacity) => {
    if (capacity === 0) return "No capacity info";
    const available = capacity - slots;
    return `${available} of ${capacity} slots available`;
  };

  return (
    <div className="stations-page">
      <div className="card">
        <div className="stations-header">
          <div>
            <h2>Parking Stations</h2>
            <div className="lead">Find and manage parking locations</div>
          </div>
          <button 
            className="btn" 
            onClick={() => navigate("/stations/new")}
          >
            Add New Station
          </button>
        </div>

        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading stations...</div>
          </div>
        )}

        {error && (
          <div className="error">
            {error}
            <button 
              className="btn small" 
              onClick={() => window.location.reload()}
              style={{ marginLeft: "12px" }}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && stations.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🚗</div>
            <h3>No stations found</h3>
            <p>Get started by adding your first parking station.</p>
            <button 
              className="btn" 
              onClick={() => navigate("/stations/new")}
            >
              Add First Station
            </button>
          </div>
        )}

        {!loading && !error && stations.length > 0 && (
          <div className="station-list">
            {stations.map((station, index) => (
              <div key={station._id || station.id || station.station_id || index} className="station">
                <div className="station-header">
                  <div className="station-name">{station.name || station.station_name || `Station ${index + 1}`}</div>
                  <div 
                    className="availability-badge"
                    style={{ 
                      backgroundColor: getAvailabilityColor(station.slots || 0, station.capacity || 0),
                      color: "white"
                    }}
                  >
                    {getAvailabilityText(station.slots || 0, station.capacity || 0)}
                  </div>
                </div>
                
                <div className="station-details">
                  {station.location && (
                    <div className="station-detail">
                      <span className="detail-label">📍 Location:</span>
                      <span className="detail-value">{station.location}</span>
                    </div>
                  )}
                  
                  {station.address && (
                    <div className="station-detail">
                      <span className="detail-label">🏠 Address:</span>
                      <span className="detail-value">{station.address}</span>
                    </div>
                  )}
                  
                  {station.capacity && (
                    <div className="station-detail">
                      <span className="detail-label">🚗 Capacity:</span>
                      <span className="detail-value">{station.capacity} slots</span>
                    </div>
                  )}
                  
                  {station.price && (
                    <div className="station-detail">
                      <span className="detail-label">💰 Price:</span>
                      <span className="detail-value">{station.price}</span>
                    </div>
                  )}
                  
                  {station.station_id && (
                    <div className="station-detail">
                      <span className="detail-label">🆔 Station ID:</span>
                      <span className="detail-value">{station.station_id}</span>
                    </div>
                  )}
                </div>
                
                <div className="station-actions">
                  <button className="btn small">View Details</button>
                  <button className="btn small" style={{ backgroundColor: "var(--accent-light)" }}>Book Slot</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}