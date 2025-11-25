import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function CreatePostPage() {
  const navigate = useNavigate();

  const [image, setImage] = useState(null);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!image) {
      setError("Please select an image.");
      return;
    }

    const formData = new FormData();
    formData.append("image", image);
    formData.append("description", description);

    try {
      setLoading(true);

      const res = await api.post("posts/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      navigate("/feed"); // redirect back to feed
    } catch (err) {
      console.error(err);
      setError("Failed to upload post.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "2rem auto" }}>
      <h2>Create New Post</h2>

      {error && (
        <div
          style={{
            backgroundColor: "#ffe5e5",
            padding: "10px",
            borderRadius: "5px",
            marginBottom: "1rem",
            color: "#a10000",
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label>Upload Image</label>
          <input
            type="file"
            onChange={(e) => setImage(e.target.files[0])}
            accept="image/*"
            style={{ display: "block", marginTop: "0.5rem" }}
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="3"
            style={{
              width: "100%",
              padding: "0.5rem",
              marginTop: "0.5rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
            }}
          ></textarea>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.6rem 1.5rem",
            backgroundColor: "#10b981",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          {loading ? "Uploading..." : "Post"}
        </button>
      </form>
    </div>
  );
}
