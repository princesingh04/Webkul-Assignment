// src/pages/FeedPage.jsx
import { useEffect, useState } from "react";
import api from "../api/client";

export default function FeedPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPosts = async () => {
    try {
      const res = await api.get("posts/");
      setPosts(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to load posts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, []);

  const handleReact = async (postId, reactionType) => {
    // reactionType = "like" or "dislike"
    try {
      const res = await api.post(`posts/${postId}/react/`, {
        reaction: reactionType,
      });

      const updatedPost = res.data;

      // Update that post in local state
      setPosts((prev) =>
        prev.map((p) => (p.id === updatedPost.id ? updatedPost : p))
      );
    } catch (err) {
      console.error(err);
      alert("Failed to react on post");
    }
  };

  if (loading) return <h2 style={{ textAlign: "center" }}>Loading...</h2>;

  return (
    <div style={{ maxWidth: "600px", margin: "2rem auto" }}>
      <h2 style={{ marginBottom: "1.5rem" }}>Feed</h2>
      <button
  onClick={() => window.location.href = "/create-post"}
  style={{
    padding: "0.5rem 1rem",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    marginBottom: "1rem"
  }}
>
  ➕ Create Post
</button>

      {posts.length === 0 && <p>No posts found.</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {posts.map((post) => {
          const isLiked = post.user_reaction === "like";
          const isDisliked = post.user_reaction === "dislike";

          return (
            <div
              key={post.id}
              style={{
                padding: "1rem",
                border: "1px solid #ddd",
                borderRadius: "8px",
              }}
            >
              {/* Post Image */}
              <img
                src={post.image}
                alt="post"
                style={{
                  width: "100%",
                  borderRadius: "8px",
                  objectFit: "cover",
                }}
              />

              {/* Post Details */}
              <p style={{ marginTop: "0.5rem", fontWeight: "bold" }}>
                @{post.author}
              </p>
              <p>{post.description}</p>

              {/* Reaction Buttons + Counts */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginTop: "0.75rem",
                }}
              >
                <div style={{ display: "flex", gap: "0.75rem" }}>
                  <button
                    onClick={() => handleReact(post.id, "like")}
                    style={{
                      padding: "0.25rem 0.75rem",
                      borderRadius: "999px",
                      border: isLiked ? "2px solid #2563eb" : "1px solid #ccc",
                      backgroundColor: isLiked ? "#dbeafe" : "#f9fafb",
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "0.4rem",
                    }}
                  >
                    <span style={{ lineHeight: 1 }}>👍</span>
                    <span
                      style={{
                        color: isLiked ? "#1e40af" : "#0b84ff",
                        fontWeight: 600,
                      }}
                    >
                      {post.likes_count}
                    </span>
                  </button>

                  <button
                    onClick={() => handleReact(post.id, "dislike")}
                    style={{
                      padding: "0.25rem 0.75rem",
                      borderRadius: "999px",
                      border: isDisliked
                        ? "2px solid #dc2626"
                        : "1px solid #ccc",
                      backgroundColor: isDisliked ? "#fee2e2" : "#f9fafb",
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "0.4rem",
                    }}
                  >
                    <span style={{ lineHeight: 1 }}>👎</span>
                    <span
                      style={{
                        color: isDisliked ? "#7f1d1d" : "#dc2626",
                        fontWeight: 600,
                      }}
                    >
                      {post.dislikes_count}
                    </span>
                  </button>
                </div>

                <span
                  style={{
                    fontSize: "0.8rem",
                    color: "#666",
                  }}
                >
                  {post.user_reaction
                    ? `You ${post.user_reaction}d this`
                    : "No reaction yet"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
