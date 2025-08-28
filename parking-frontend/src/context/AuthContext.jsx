import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("userEmail") || "");

  useEffect(() => {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");

    if (userEmail) localStorage.setItem("userEmail", userEmail);
    else localStorage.removeItem("userEmail");
  }, [token, userEmail]);

  const logout = () => {
    setToken(null);
    setUserEmail("");
  };

  return (
    <AuthContext.Provider value={{ token, setToken, userEmail, setUserEmail, logout }}>
      {children}
    </AuthContext.Provider>
  );
}