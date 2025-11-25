// src/components/Navbar.jsx
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("accessToken");

  const logout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    navigate("/login");
  };

  return (
    <nav
      style={{
        display: "flex",
        gap: "1.5rem",
        padding: "1rem",
        borderBottom: "1px solid #e5e5e5",
        alignItems: "center",
        backgroundColor: "#fafafa",
      }}
    >
      {token ? (
        <>
          {/* Logged-in nav */}
          <Link to="/feed" style={{ textDecoration: "none", color: "#2563eb" }}>
            Feed
          </Link>

          <Link
            to="/create-post"
            style={{ textDecoration: "none", color: "#2563eb" }}
          >
            Create Post
          </Link>

          <Link
            to="/profile"
            style={{ textDecoration: "none", color: "#2563eb" }}
          >
            Profile
          </Link>

          <button
            onClick={logout}
            style={{
              marginLeft: "auto",
              border: "none",
              background: "transparent",
              cursor: "pointer",
              color: "#dc2626",
              fontWeight: "bold",
              fontSize: "1rem",
            }}
          >
            Logout
          </button>
        </>
      ) : (
        <>
          {/* Logged-out nav */}
          <Link to="/login" style={{ textDecoration: "none", color: "#2563eb" }}>
            Login
          </Link>

          <Link
            to="/signup"
            style={{
              textDecoration: "none",
              color: "#2563eb",
              marginLeft: "auto",
            }}
          >
            Signup
          </Link>
        </>
      )}
    </nav>
  );
}
