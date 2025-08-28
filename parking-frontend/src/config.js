// Frontend Configuration
export const config = {
  // Backend API Configuration
  API_BASE: import.meta.env.VITE_API_BASE || "http://localhost:8000",
  
  // Service URLs (for reference)
  GATEWAY_API: "http://localhost:8000",
  USER_SERVICES: "http://localhost:8002", 
  PARKING_SERVICES: "http://localhost:8001",
  BOOKING_SERVICES: "http://localhost:8003",
  
  // App Configuration
  APP_NAME: "Parking System",
  VERSION: "1.0.0",
  
  // Timeout Configuration
  API_TIMEOUT: 10000,
  
  // Local Storage Keys
  STORAGE_KEYS: {
    TOKEN: "token",
    USER_EMAIL: "userEmail", 
    USER_ROLE: "userRole"
  }
};

export default config; 