// src/pages/ProfilePage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function ProfilePage() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [profileForm, setProfileForm] = useState({
    username: "",
    bio: "",
    location: "",
    phone: "",
    date_of_birth: "",
  });
  const [profileImageFile, setProfileImageFile] = useState(null);

  const [myPosts, setMyPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const accessToken = localStorage.getItem("accessToken");

  // If no token, send to login (guard)
  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
    }
  }, [accessToken, navigate]);

  const fetchProfileAndPosts = async () => {
    try {
      setLoading(true);
      setError("");

      // 1) Fetch profile
      const profileRes = await api.get("profile/");
      const p = profileRes.data;
      setProfile(p);
      setProfileForm({
        username: p.username || "",
        bio: p.bio || "",
        location: p.location || "",
        phone: p.phone || "",
        date_of_birth: p.date_of_birth || "",
      });

      // 2) Fetch posts and filter only this user's posts
      const postsRes = await api.get("posts/");
      const allPosts = postsRes.data || [];
      const mine = allPosts.filter((post) => post.author === p.username);
      setMyPosts(mine);
    } catch (err) {
      console.error(err);
      setError("Failed to load profile.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfileAndPosts();
  }, []);

  const handleChange = (e) => {
    setProfileForm({
      ...profileForm,
      [e.target.name]: e.target.value,
    });
  };

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");

    try {
      setSaving(true);

      const formData = new FormData();
      formData.append("username", profileForm.username);
      formData.append("bio", profileForm.bio);
      formData.append("location", profileForm.location);
      formData.append("phone", profileForm.phone);

      if (profileForm.date_of_birth) {
        formData.append("date_of_birth", profileForm.date_of_birth);
      }

      if (profileImageFile) {
        formData.append("profile_image", profileImageFile);
      }

      const res = await api.patch("profile/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setProfile(res.data);
      setSuccessMsg("Profile updated successfully.");
      fetchProfileAndPosts(); // refresh posts if username changed
    } catch (err) {
      console.error(err);
      setError("Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm("Delete this post?")) return;

    try {
      await api.delete(`posts/${postId}/`);
      setMyPosts((prev) => prev.filter((p) => p.id !== postId));
    } catch (err) {
      console.error(err);
      alert("Failed to delete post.");
    }
  };

  if (loading) {
    return (
      <h2 style={{ textAlign: "center", marginTop: "2rem" }}>
        Loading profile...
      </h2>
    );
  }

  if (!profile) {
    return (
      <h2 style={{ textAlign: "center", marginTop: "2rem" }}>
        No profile found.
      </h2>
    );
  }

  return (
    <div className="app-main">
      <div className="profile-layout">
        {/* Left: profile info + form */}
        <div className="profile-left">
          <h2>My Profile</h2>

          {error && (
            <div className="banner-error">
              {error}
            </div>
          )}

          {successMsg && (
            <div className="banner-success">
              {successMsg}
            </div>
          )}

          {/* Current avatar */}
          <div style={{ margin: "1rem 0" }}>
            <p>Profile picture:</p>
            {profile.profile_image ? (
              <img
                src={profile.profile_image}
                alt="Profile"
                style={{
                  width: "100px",
                  height: "100px",
                  borderRadius: "50%",
                  objectFit: "cover",
                  border: "2px solid #ddd",
                }}
              />
            ) : (
              <div
                style={{
                  width: "100px",
                  height: "100px",
                  borderRadius: "50%",
                  backgroundColor: "#eee",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#777",
                  fontSize: "0.8rem",
                }}
              >
                No image
              </div>
            )}
          </div>

          {/* Edit form */}
          <form onSubmit={handleProfileSave}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                name="username"
                value={profileForm.username}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Bio</label>
              <textarea
                name="bio"
                value={profileForm.bio}
                onChange={handleChange}
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>Location</label>
              <input
                type="text"
                name="location"
                value={profileForm.location}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Phone</label>
              <input
                type="text"
                name="phone"
                value={profileForm.phone}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Date of Birth</label>
              <input
                type="date"
                name="date_of_birth"
                value={profileForm.date_of_birth}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Change Profile Image</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setProfileImageFile(e.target.files[0])}
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="btn-primary"
            >
              {saving ? "Saving..." : "Save Profile"}
            </button>
          </form>
        </div>

        {/* Right: user's posts */}
        <div className="profile-right">
          <h3>My Posts</h3>
          {myPosts.length === 0 && <p>You haven't posted anything yet.</p>}

          <div className="posts-list">
            {myPosts.map((post) => (
              <div key={post.id} className="post-card">
                <img
                  src={post.image}
                  alt="post"
                  className="post-image"
                />
                <p style={{ marginTop: "0.5rem" }}>{post.description}</p>
                <div className="post-footer">
                  <span style={{ color: "#111", fontWeight: 500 }}>
                    👍 {post.likes_count} · 👎 {post.dislikes_count}
                  </span>
                  <button
                    onClick={() => handleDeletePost(post.id)}
                    className="btn-danger-chip"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
