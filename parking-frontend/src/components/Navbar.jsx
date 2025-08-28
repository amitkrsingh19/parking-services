import React, { useState, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Navbar() {
  const { token, userEmail, userRole, isAdmin, logout } = useContext(AuthContext);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setIsMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="navbar">
      <div className="nav-inner">
        <div className="brand">
          <Link to="/" className="brand-link">
            🚗 Parking System
          </Link>
        </div>

        {/* Mobile menu button */}
        <button 
          className="mobile-menu-btn"
          onClick={toggleMobileMenu}
          aria-label="Toggle mobile menu"
        >
          <span className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}></span>
        </button>

        <nav className={`nav-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          {!token ? (
            <>
              <Link 
                className="nav-item" 
                to="/login"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Sign In
              </Link>
              <Link 
                className="nav-item cta" 
                to="/register"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Create Account
              </Link>
            </>
          ) : (
            <>
              <div className="user-section">
                <div className="user-avatar">
                  {userEmail ? userEmail.charAt(0).toUpperCase() : "U"}
                </div>
                <span className="nav-user">{userEmail || "User"}</span>
              </div>
              
              {/* Admin Navigation */}
              {isAdmin ? (
                <>
                  <Link 
                    className="nav-item" 
                    to="/admin/dashboard"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    👑 Admin Dashboard
                  </Link>
                  
                  <Link 
                    className="nav-item" 
                    to="/admin/slots"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    🚗 Manage Slots
                  </Link>
                  
                  <Link 
                    className="nav-item" 
                    to="/stations/new"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    ➕ Add Station
                  </Link>
                </>
              ) : (
                <>
                  {/* Simplified User Navigation - Only Essential Features */}
                  <Link 
                    className="nav-item" 
                    to="/dashboard"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    🏠 Dashboard
                  </Link>
                  
                  <Link 
                    className="nav-item" 
                    to="/booking"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    🅿️ Book Parking
                  </Link>
                  
                  <Link 
                    className="nav-item" 
                    to="/my-bookings"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    📋 My Bookings
                  </Link>
                </>
              )}
              
              <button 
                className="btn small logout-btn" 
                onClick={handleLogout}
              >
                Sign Out
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
