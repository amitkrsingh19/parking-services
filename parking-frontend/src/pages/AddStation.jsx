import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { parkingAPI } from "../api/client";

export default function AddStation() {
  const { token, userEmail, isAdmin } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    name: "",
    location: "",
    capacity: "",
    description: "",
    contact_number: "",
    operating_hours: "24/7"
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [hasExistingStation, setHasExistingStation] = useState(false);
  const [existingStation, setExistingStation] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    if (!isAdmin()) {
      navigate("/dashboard");
      return;
    }

    checkExistingStation();
  }, [token, navigate, isAdmin]);

  const checkExistingStation = async () => {
    try {
      const response = await parkingAPI.getStations();
      let allStations = [];
      
      if (Array.isArray(response)) {
        allStations = response;
      } else if (response && Array.isArray(response.stations)) {
        allStations = response.stations;
      }
      
      // Check if admin already has a station
      const adminStation = allStations.find(station => 
        station.posted_by === userEmail || station.admin_id === userEmail
      );
      
      if (adminStation) {
        setHasExistingStation(true);
        setExistingStation(adminStation);
      }
    } catch (error) {
      console.error("Failed to check existing station:", error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError("Station name is required");
      return false;
    }
    if (!formData.location.trim()) {
      setError("Location is required");
      return false;
    }
    if (!formData.capacity || parseInt(formData.capacity) <= 0) {
      setError("Capacity must be a positive number");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    if (hasExistingStation) {
      setError("You already have a parking station. You can only manage one station at a time.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const stationData = {
        ...formData,
        capacity: parseInt(formData.capacity),
        posted_by: userEmail,
        admin_id: userEmail,
        status: "active"
      };

      const response = await parkingAPI.addStation(stationData);
      
      if (response) {
        setSuccess("Station created successfully! You can now add parking slots.");
        setFormData({
          name: "",
          location: "",
          capacity: "",
          description: "",
          contact_number: "",
          operating_hours: "24/7"
        });
        
        // Redirect to admin dashboard after a short delay
        setTimeout(() => {
          navigate("/admin/dashboard");
        }, 2000);
      }
    } catch (error) {
      console.error("Failed to create station:", error);
      if (error.response?.status === 409) {
        setError("You already have a parking station or this station name already exists.");
      } else if (error.response?.status === 403) {
        setError("You don't have permission to create stations.");
      } else if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else if (error.message) {
        setError(error.message);
      } else {
        setError("Failed to create station. Please check your connection and try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!token || !isAdmin()) {
    return null;
  }

  if (hasExistingStation) {
    return (
      <div className="add-station-page">
        <div className="page-header">
          <div>
            <h1>Add New Station 🏢</h1>
            <div className="lead">Create a new parking station in the system</div>
          </div>
          <button 
            className="btn"
            onClick={() => navigate("/admin/dashboard")}
          >
            ← Back to Admin
          </button>
        </div>

        <div className="existing-station-warning">
          <div className="warning-icon">⚠️</div>
          <div className="warning-content">
            <h3>Station Already Exists</h3>
            <p>You already have a parking station: <strong>{existingStation?.name || existingStation?.station_name}</strong></p>
            <p>According to system constraints, you can only manage one station at a time.</p>
            <div className="warning-actions">
              <button 
                className="btn"
                onClick={() => navigate("/admin/slots")}
              >
                Manage Your Station Slots
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => navigate("/admin/dashboard")}
              >
                Go to Admin Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="add-station-page">
      <div className="page-header">
        <div>
          <h1>Add New Station 🏢</h1>
          <div className="lead">Create your first parking station in the system</div>
        </div>
        <button 
          className="btn"
          onClick={() => navigate("/admin/dashboard")}
        >
          ← Back to Admin
        </button>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div className="form-container">
        <form onSubmit={handleSubmit} className="form">
          <div className="form-header">
            <h2>Station Information</h2>
            <p>Fill in the details for your parking station. You can only create one station per admin account.</p>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="field-label">Station Name *</label>
              <input 
                className="input" 
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Downtown Mall Parking"
                required
              />
              <div className="hint">Choose a unique and descriptive name for your station</div>
            </div>
            
            <div className="form-group">
              <label className="field-label">Location *</label>
              <input 
                className="input" 
                type="text"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                placeholder="e.g., 123 Main Street, Downtown"
                required
              />
              <div className="hint">Full address or location description</div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="field-label">Capacity *</label>
              <input 
                className="input" 
                type="number"
                name="capacity"
                value={formData.capacity}
                onChange={handleInputChange}
                placeholder="e.g., 50"
                min="1"
                required
              />
              <div className="hint">Maximum number of vehicles the station can accommodate</div>
            </div>
            
            <div className="form-group">
              <label className="field-label">Contact Number</label>
              <input 
                className="input" 
                type="tel"
                name="contact_number"
                value={formData.contact_number}
                onChange={handleInputChange}
                placeholder="e.g., +1-555-123-4567"
              />
              <div className="hint">Contact number for station inquiries</div>
            </div>
          </div>

          <div className="form-group">
            <label className="field-label">Operating Hours</label>
            <select 
              className="input"
              name="operating_hours"
              value={formData.operating_hours}
              onChange={handleInputChange}
            >
              <option value="24/7">24/7 (Always Open)</option>
              <option value="6AM-10PM">6:00 AM - 10:00 PM</option>
              <option value="7AM-9PM">7:00 AM - 9:00 PM</option>
              <option value="8AM-8PM">8:00 AM - 8:00 PM</option>
              <option value="custom">Custom Hours</option>
            </select>
            <div className="hint">When your parking station is open for business</div>
          </div>

          <div className="form-group">
            <label className="field-label">Description</label>
            <textarea 
              className="input" 
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe your parking station, amenities, and any special features..."
              rows="4"
            />
            <div className="hint">Optional: Add details about your station's features and services</div>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={() => navigate("/admin/dashboard")}
            >
              Cancel
            </button>
            <button 
              className="btn" 
              type="submit"
              disabled={loading}
            >
              {loading ? "Creating..." : "Create Station"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}