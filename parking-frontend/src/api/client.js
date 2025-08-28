import axios from "axios";

// Configuration constants
const API_BASE = "http://localhost:8000";
const API_TIMEOUT = 10000;
const STORAGE_KEYS = {
  TOKEN: "token",
  USER_EMAIL: "userEmail",
  USER_ROLE: "userRole"
};

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_EMAIL);
      localStorage.removeItem(STORAGE_KEYS.USER_ROLE);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Utility functions
export const setAuthToken = (token) => {
  localStorage.setItem(STORAGE_KEYS.TOKEN, token);
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

export const clearAuth = () => {
  localStorage.removeItem(STORAGE_KEYS.TOKEN);
  localStorage.removeItem(STORAGE_KEYS.USER_EMAIL);
  localStorage.removeItem(STORAGE_KEYS.USER_ROLE);
  delete apiClient.defaults.headers.common['Authorization'];
};

// Authentication API
export const authAPI = {
  // Health check to test backend connectivity
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/');
      return response;
    } catch (error) {
      console.error("Health check failed:", error);
      throw error;
    }
  },
  
  // Test user service connectivity
  testUserService: async () => {
    try {
      const response = await apiClient.get('/test-user-service');
      return response;
    } catch (error) {
      console.error("User service test failed:", error);
      throw error;
    }
  },
  
  login: async (email, password) => {
    // Use form data format as expected by OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append('username', email);  // OAuth2 expects 'username' field
    formData.append('password', password);
    
    const response = await apiClient.post('/login/', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
    });
    return response;
  },
  
  register: async (userData) => {
    const response = await apiClient.post('/user/users/', userData);
    return response;
  },
  
  getProfile: async () => {
    const response = await apiClient.get('/user/users/profile/me');
    return response;
  }
};

// Parking API
export const parkingAPI = {
  // Get all stations
  getStations: async () => {
    const response = await apiClient.get('/parking/stations');
    return response;
  },
  
  // Add new station (admin only)
  addStation: async (stationData) => {
    const response = await apiClient.post('/parking/stations', stationData);
    return response;
  },
  
  // Get slots for a specific station
  getSlotsByStation: async (stationId) => {
    const response = await apiClient.get(`/parking/stations/${stationId}/slots`);
    return response;
  },
  
  // Add new slot to a station
  addSlot: async (slotData) => {
    const response = await apiClient.post('/parking/slots', slotData);
    return response;
  },
  
  // Update slot availability
  toggleSlotAvailability: async (slotId) => {
    const response = await apiClient.patch(`/parking/slots/${slotId}/toggle`);
    return response;
  },
  
  // Delete a slot
  deleteSlot: async (slotId) => {
    const response = await apiClient.delete(`/parking/slots/${slotId}`);
    return response;
  },
  
  // Update slot details
  updateSlot: async (slotId, slotData) => {
    const response = await apiClient.put(`/parking/slots/${slotId}`, slotData);
    return response;
  },
  
  // Get available slots (for users)
  getAvailableSlots: async () => {
    const response = await apiClient.post('/parking/slots/available');
    return response;
  }
};

// Booking API
export const bookingAPI = {
  // Create new booking
  createBooking: async (bookingData) => {
    const response = await apiClient.post('/booking/create', bookingData);
    return response;
  },
  
  // Get user's bookings
  getUserBookings: async () => {
    const response = await apiClient.get('/booking/user');
    return response;
  },
  
  // Get bookings for a station (admin only)
  getBookingsByStation: async (stationId) => {
    const response = await apiClient.get(`/booking/station/${stationId}`);
    return response;
  },
  
  // Cancel booking
  cancelBooking: async (bookingId) => {
    const response = await apiClient.patch(`/booking/${bookingId}/cancel`);
    return response;
  },
  
  // Get booking details
  getBookingDetails: async (bookingId) => {
    const response = await apiClient.get(`/booking/${bookingId}`);
    return response;
  }
};

// Admin API
export const adminAPI = {
  // Get admin dashboard stats
  getDashboardStats: async () => {
    const response = await apiClient.get('/admin/dashboard/stats');
    return response;
  },
  
  // Get admin's station
  getAdminStation: async () => {
    const response = await apiClient.get('/admin/station');
    return response;
  },
  
  // Get admin's station slots
  getAdminStationSlots: async () => {
    const response = await apiClient.get('/admin/station/slots');
    return response;
  },
  
  // Get admin's station bookings
  getAdminStationBookings: async () => {
    const response = await apiClient.get('/admin/station/bookings');
    return response;
  }
};

export default apiClient;