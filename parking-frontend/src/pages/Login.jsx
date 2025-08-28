import React, {useState, useContext} from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { authAPI, setAuthToken } from "../api/client";

export default function Login(){
  const { login } = useContext(AuthContext);
  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");
  const [err,setErr] = useState("");
  const [loading,setLoading] = useState(false);
  const navigate = useNavigate();

  async function submit(e){
    e?.preventDefault();
    setErr(""); 
    setLoading(true);
    
    console.log("🔐 Login attempt for:", email); // Debug log
    
    try {
      // First, test backend connectivity
      console.log("🏥 Testing backend health..."); // Debug log
      try {
        await authAPI.healthCheck();
        console.log("✅ Backend is accessible"); // Debug log
      } catch (healthError) {
        console.error("❌ Backend health check failed:", healthError); // Debug log
        setErr("Backend service is not accessible. Please check if your services are running.");
        setLoading(false);
        return;
      }
      
      // Test user service connectivity
      console.log("🧪 Testing user service connectivity..."); // Debug log
      try {
        const userServiceTest = await authAPI.testUserService();
        console.log("✅ User service test result:", userServiceTest); // Debug log
      } catch (userServiceError) {
        console.error("❌ User service connectivity failed:", userServiceError); // Debug log
        setErr("User service is not accessible. Please check if your user service is running.");
        setLoading(false);
        return;
      }
      
      // Call real backend API
      console.log("📡 Calling authAPI.login..."); // Debug log
      const response = await authAPI.login(email, password);
      console.log("📥 Login response:", response); // Debug log
      
      if (response.access_token) {
        console.log("✅ Access token received:", response.access_token.substring(0, 20) + "..."); // Debug log
        
        // Set token in localStorage and axios headers
        setAuthToken(response.access_token);
        
        // Decode JWT token to get user info (basic implementation)
        try {
          const tokenParts = response.access_token.split('.');
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]));
            const userRole = payload.role || "user";
            console.log("🔍 Decoded token payload:", payload); // Debug log
            console.log("👤 User role:", userRole); // Debug log
            
            // Login with real data
            login(response.access_token, email, userRole);
            
            // Navigate to dashboard
            console.log("🚀 Navigating to dashboard..."); // Debug log
            navigate("/dashboard");
          } else {
            throw new Error("Invalid token format");
          }
        } catch (tokenError) {
          console.error("Token decode error:", tokenError);
          // Fallback to user role if token decode fails
          login(response.access_token, email, "user");
          navigate("/dashboard");
        }
      } else {
        console.error("❌ No access_token in response:", response); // Debug log
        setErr("Invalid response from server");
      }
    } catch(error) {
      console.error("💥 Login error:", error); // Debug log
      console.error("Error response:", error.response); // Debug log
      console.error("Error message:", error.message); // Debug log
      
      if (error.response?.status === 401) {
        setErr("Invalid email or password");
      } else if (error.response?.data?.detail) {
        setErr(error.response.data.detail);
      } else if (error.message) {
        setErr(error.message);
      } else {
        setErr("Login failed. Please check your connection and try again.");
      }
    } finally { 
      setLoading(false) 
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <div className="login-header">
          <h2>Welcome Back</h2>
          <div className="lead">Sign in to access your parking account</div>
        </div>
        
        <form className="login-form" onSubmit={submit}>
          <div className="form-group">
            <label className="field-label">Email Address</label>
            <input 
              className="input" 
              type="email"
              value={email} 
              onChange={e=>setEmail(e.target.value)} 
              placeholder="Enter your email address" 
              required 
            />
          </div>
          
          <div className="form-group">
            <label className="field-label">Password</label>
            <input 
              className="input" 
              type="password" 
              value={password} 
              onChange={e=>setPassword(e.target.value)} 
              placeholder="Enter your password" 
              required 
            />
          </div>
          
          <button className="btn login-btn" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>
          
          {err && <div className="error">{err}</div>}
          
          <div className="login-footer">
            <div className="hint">
              Don't have an account?{" "}
              <Link to="/register" className="link-primary">Create one here</Link>
            </div>
            <div className="demo-hint">
              <small>
                💡 Make sure your backend services are running on the correct ports
              </small>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}