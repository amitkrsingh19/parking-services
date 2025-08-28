import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../api/client";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function submit(e) {
    e?.preventDefault();
    setErr("");
    setSuccess("");
    
    // Basic validation
    if (password !== confirmPassword) {
      setErr("Passwords do not match");
      return;
    }
    
    if (password.length < 6) {
      setErr("Password must be at least 6 characters long");
      return;
    }
    
    setLoading(true);
    try {
      const userData = { name, email, password };
      
      // Call real backend API
      const response = await authAPI.register(userData);
      
      if (response) {
        setSuccess("User created successfully! You can now login.");
        setName("");
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setTimeout(() => navigate("/login"), 2000);
      }
    } catch (error) {
      console.error("Registration error:", error);
      
      if (error.response?.status === 409) {
        setErr("User with this email already exists");
      } else if (error.response?.data?.detail) {
        setErr(error.response.data.detail);
      } else if (error.message) {
        setErr(error.message);
      } else {
        setErr("Registration failed. Please check your connection and try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <div className="login-header">
          <h2>Create Account</h2>
          <div className="lead">Join our parking system today</div>
        </div>
        
        <form className="login-form" onSubmit={submit}>
          <div className="form-group">
            <label className="field-label">Full Name</label>
            <input 
              className="input" 
              placeholder="Enter your full name" 
              value={name} 
              onChange={e => setName(e.target.value)} 
              required 
            />
          </div>
          
          <div className="form-group">
            <label className="field-label">Email Address</label>
            <input 
              className="input" 
              type="email" 
              placeholder="Enter your email address" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required 
            />
          </div>
          
          <div className="form-group">
            <label className="field-label">Password</label>
            <input 
              className="input" 
              type="password" 
              placeholder="Create a password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
            />
          </div>
          
          <div className="form-group">
            <label className="field-label">Confirm Password</label>
            <input 
              className="input" 
              type="password" 
              placeholder="Confirm your password" 
              value={confirmPassword} 
              onChange={e => setConfirmPassword(e.target.value)} 
              required 
            />
          </div>
          
          <button className="btn login-btn" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Creating Account...
              </>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        {err && <div className="error">{err}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <div className="login-footer">
          <div className="hint">
            Already have an account?{" "}
            <Link to="/login" className="link-primary">Sign in here</Link>
          </div>
        </div>
      </div>
    </div>
  );
}