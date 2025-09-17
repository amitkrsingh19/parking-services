import React, { createContext, useState, useEffect } from "react";
import { setAuthToken, clearAuth } from "../api/client";

export const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token") || null);
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("userEmail") || "");
  const [userRole, setUserRole] = useState(() => localStorage.getItem("userRole") || null);

  // decode JWT payload helper
  const decodeJwtPayload = (t) => {
    try {
      if (!t) return null;
      const parts = t.split(".");
      if (parts.length !== 3) return null;
      const payload = parts[1];
      const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
      return JSON.parse(decoded);
    } catch (e) {
      console.error("Failed to decode token", e);
      return null;
    }
  };

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      setAuthToken(token);
      const payload = decodeJwtPayload(token);
      if (payload) {
        const email = payload.sub || payload.email || "";
        if (email) setUserEmail(email);
        if (payload.role) setUserRole(payload.role);
        else if (payload.roles && Array.isArray(payload.roles)) setUserRole(payload.roles[0]);
      }
    } else {
      localStorage.removeItem("token");
      clearAuth();
    }
  }, [token]);

  useEffect(() => {
    if (userEmail) localStorage.setItem("userEmail", userEmail);
    else localStorage.removeItem("userEmail");
  }, [userEmail]);

  useEffect(() => {
    if (userRole) localStorage.setItem("userRole", userRole);
    else localStorage.removeItem("userRole");
  }, [userRole]);

  const isAdmin = userRole === "admin" || userRole === "superadmin";

  const login = (tokenValue) => {
    if (!tokenValue) return;
    setToken(tokenValue);
    const payload = decodeJwtPayload(tokenValue);
    if (payload) {
      const email = payload.sub || payload.email || "";
      if (email) setUserEmail(email);
      if (payload.role) setUserRole(payload.role);
      else if (payload.roles && Array.isArray(payload.roles)) setUserRole(payload.roles[0]);
    }
  };

  const logout = () => {
    setToken(null);
    setUserEmail("");
    setUserRole(null);
  };

  return (
    <AuthContext.Provider
      value={{ token, setToken, userEmail, setUserEmail, userRole, setUserRole, isAdmin, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}