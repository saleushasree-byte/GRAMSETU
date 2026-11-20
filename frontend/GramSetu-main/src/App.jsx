

import { useState, useEffect } from "react";
import "./App.css";

const modules = [
  {
    name: "Krishi Sahayak",
    icon: "🌾",
    description: "Agriculture Assistance",
    services: [
      "Crop Recommendation",
      "Crop Disease Detection",
      "Fertilizer Recommendation",
      "Weather Forecast",
      "Crop Yield Prediction",
      "Market Price Information",
    ],
  },
  {
    name: "Vikas Naksha",
    icon: "🏗️",
    description: "Village Infrastructure",
    services: [
      "Road Development",
      "Drinking Water Facilities",
      "Electricity Availability",
      "School Infrastructure",
      "Sanitation Facilities",
      "Village Development Complaints",
    ],
  },
  {
    name: "Swasthya Mitra",
    icon: "🏥",
    description: "Healthcare Assistance",
    services: [
      "Symptom Checker",
      "Nearby Health Centres",
      "Medicine Information",
      "Health Camp Schedules",
      "Vaccination Information",
      "Emergency Contacts",
    ],
  },
  {
    name: "Gyan Dhara",
    icon: "🎓",
    description: "Education Support",
    services: [
      "Online Learning",
      "Scholarship Information",
      "Digital Learning Materials",
      "Skill Development Courses",
      "Career Guidance",
      "Education Schemes",
    ],
  },
  {
    name: "Yojana Sathi",
    icon: "🏛️",
    description: "Government Schemes",
    services: [
      "PM-KISAN",
      "Ayushman Bharat",
      "PM Awas Yojana",
      "MGNREGA",
      "Social Assistance Programme",
      "Scholarship Schemes",
    ],
  },
  {
    name: "Bazaar Setu",
    icon: "🛒",
    description: "Market Linkage",
    services: [
      "Daily Crop Market Prices",
      "Nearby Agricultural Markets",
      "Online Product Selling",
      "Buyer Connections",
      "Seasonal Job Opportunities",
      "Farmer Business Support",
    ],
  },
];

function App() {
  const [page, setPage] = useState("home");
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selectedService, setSelectedService] = useState("");

  const [form, setForm] = useState({
    name: "",
    mobile: "",
    email: "",
    state: "",
    district: "",
    village: "",
    password: "",
    confirmPassword: "",
  });

  const [loginData, setLoginData] = useState({
    mobile: "",
    password: "",
  });

  
  // CONNECT TO FLASK BACKEND AND RESTORE LOGIN SESSION
  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend response error");
        }
        return response.json();
      })
      .then((data) => {
        setBackendStatus(data.message || "Connected successfully");

        return fetch("http://127.0.0.1:5000/api/auth/me", {
          method: "GET",
          credentials: "include",
        });
      })
      .then(async (response) => {
        if (response && response.ok) {
          const data = await response.json();
          setUser(data.user);
          setPage("dashboard");
        }
      })
      .catch(() => {
        setBackendStatus("Backend connection failed");
      });
  }, []);


  const updateForm = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const updateLogin = (e) => {
    setLoginData({ ...loginData, [e.target.name]: e.target.value });
  };

  const goTo = (nextPage) => {
    setError("");
    setSuccess("");
    setPage(nextPage);
  };

 
  const registerUser = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!/^[0-9]{10}$/.test(form.mobile)) {
      setError("Please enter a valid 10-digit mobile number.");
      return;
    }

    if (form.password.length < 8) {
      setError("Password must have at least 8 characters.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: form.name,
            mobile: form.mobile,
            password: form.password,
            email: form.email,
            state: form.state,
            district: form.district,
            village: form.village,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Registration failed.");
        return;
      }

      setForm({
        name: "",
        mobile: "",
        email: "",
        state: "",
        district: "",
        village: "",
        password: "",
        confirmPassword: "",
      });

      setSuccess("Registration successful! Please login.");
      setPage("login");

    } catch (error) {
      setError("Cannot connect to server. Please try again.");
    }
  };


  
  const loginUser = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!/^[0-9]{10}$/.test(loginData.mobile)) {
      setError("Please enter a valid 10-digit mobile number.");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            mobile: loginData.mobile,
            password: loginData.password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Incorrect mobile number or password.");
        return;
      }

      setUser(data.user);
      setLoginData({ mobile: "", password: "" });
      setSelectedService("");
      setPage("dashboard");

    } catch (error) {
      setError("Cannot connect to server. Please try again.");
    }
  };


  const logout = async () => {
    try {
      await fetch("http://127.0.0.1:5000/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout request failed:", error);
    }

    setUser(null);
    setSelectedService("");
    setLoginData({ mobile: "", password: "" });
    setError("");
    setSuccess("");
    goTo("home");
  };


  // HOMEPAGE
  if (page === "home") {
    return (
      <div className="home-page">
        <nav className="home-navbar">
          <h2>🌱 GRAMSETU</h2>
          <div>
            <button onClick={() => goTo("login")}>Login</button>
            <button onClick={() => goTo("register")}>Register</button>
          </div>
        </nav>

        <section className="hero">
          <div className="hero-content">
            <span className="hero-tag">BRIDGE TO THE VILLAGE</span>
            <h1>Empowering Villages, Building Futures</h1>
            <p>
              One digital platform for agriculture, healthcare,
              education, government schemes and village development.
              Making rural services easier and accessible to everyone.
            </p>

            <button
              className="primary-btn"
              onClick={() => goTo("register")}
            >
              Get Started →
            </button>

            <button
              className="secondary-btn"
              onClick={() => goTo("login")}
            >
              Login
            </button>

            <p className="backend-status">
              Backend Status: {backendStatus}
            </p>
          </div>
        </section>

        <section className="about-section">
          <h2>About GramSetu</h2>
          <p>
            GramSetu connects rural communities with useful
            digital services and opportunities through one platform.
          </p>
        </section>

        <section className="home-services">
          <h2>Explore Our Services</h2>
          <p className="section-subtitle">
            Six important areas of village development
          </p>

          <div className="home-service-grid">
            {modules.map((module) => (
              <div className="home-service-card" key={module.name}>
                <span>{module.icon}</span>
                <h3>{module.name}</h3>
                <p>{module.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="join-section">
          <h2>Start Your Journey with GramSetu</h2>
          <p>Register today to explore rural development services.</p>
          <button onClick={() => goTo("register")}>
            Create Account
          </button>
        </section>

        <footer className="home-footer">
          <h2>🌱 GRAMSETU</h2>
          <p>Bridge to the Village</p>
          <p>© 2026 GramSetu. All rights reserved.</p>
        </footer>
      </div>
    );
  }

  // DASHBOARD
  if (page === "dashboard" && user) {
    return (
      <div className="dashboard">
        <nav className="navbar">
          <h2>🌱 GRAMSETU</h2>
          <div>
            <span>Welcome, {user.name}</span>
            <button onClick={logout}>Logout</button>
          </div>
        </nav>

        <main className="dashboard-content">
          <h1>Welcome to GramSetu!</h1>
          <p>Your village development platform.</p>

          <div className="profile-card">
            <h2>Your Profile</h2>
            <p><b>Name:</b> {user.name}</p>
            <p><b>Mobile:</b> {user.mobile}</p>
            <p><b>Village:</b> {user.village}</p>
            <p><b>District:</b> {user.district}</p>
            <p><b>State:</b> {user.state}</p>
          </div>

          <h2 className="module-heading">Explore GramSetu Services</h2>

          <div className="module-grid">
            {modules.map((module) => (
              <div className="module-card" key={module.name}>
                <h2>{module.icon} {module.name}</h2>
                <p>{module.description}</p>

                {module.services.map((service) => (
                  <button
                    className="service-option"
                    key={service}
                    onClick={() => setSelectedService(service)}
                  >
                    {service} →
                  </button>
                ))}
              </div>
            ))}
          </div>

          {selectedService && (
            <div className="selected-service">
              <h2>{selectedService}</h2>
              <p>
                You have selected this service.
                More features will be available here soon.
              </p>
              <button onClick={() => setSelectedService("")}>
                Close
              </button>
            </div>
          )}
        </main>
      </div>
    );
  }

  // LOGIN AND REGISTRATION
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>🌱 GRAMSETU</h1>
        <p>Bridge to the Village</p>

        <button
          type="button"
          className="back-home"
          onClick={() => goTo("home")}
        >
          ← Back to Home
        </button>

        {page === "login" ? (
          <>
            <h2>Login to Your Account</h2>

            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}

            <form onSubmit={loginUser}>
              <input
                type="tel"
                name="mobile"
                placeholder="Mobile Number"
                value={loginData.mobile}
                onChange={updateLogin}
                maxLength="10"
                required
              />

              <input
                type="password"
                name="password"
                placeholder="Password"
                value={loginData.password}
                onChange={updateLogin}
                required
              />

              <button type="submit">Login</button>
            </form>

            <p className="switch-text">
              Don't have an account?
              <button type="button" onClick={() => goTo("register")}>
                Register
              </button>
            </p>
          </>
        ) : (
          <>
            <h2>Create Your Account</h2>

            {error && <p className="error-message">{error}</p>}

            <form onSubmit={registerUser}>
              <input
                name="name"
                placeholder="Full Name"
                value={form.name}
                onChange={updateForm}
                required
              />

              <input
                type="tel"
                name="mobile"
                placeholder="10-digit Mobile Number"
                value={form.mobile}
                onChange={updateForm}
                maxLength="10"
                required
              />

              <input
                type="email"
                name="email"
                placeholder="Email (Optional)"
                value={form.email}
                onChange={updateForm}
              />

              <input
                name="state"
                placeholder="State"
                value={form.state}
                onChange={updateForm}
                required
              />

              <input
                name="district"
                placeholder="District"
                value={form.district}
                onChange={updateForm}
                required
              />

              <input
                name="village"
                placeholder="Village"
                value={form.village}
                onChange={updateForm}
                required
              />

              <input
                type="password"
                name="password"
                placeholder="Create Password (Minimum 8 characters)"
                value={form.password}
                onChange={updateForm}
                required
              />

              <input
                type="password"
                name="confirmPassword"
                placeholder="Confirm Password"
                value={form.confirmPassword}
                onChange={updateForm}
                required
              />

              <button type="submit">Register</button>
            </form>

            <p className="switch-text">
              Already have an account?
              <button type="button" onClick={() => goTo("login")}>
                Login
              </button>
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
