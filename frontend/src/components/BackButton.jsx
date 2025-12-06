import React from "react";

export default function BackButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: "none",
        border: "none",
        color: "#1f4b99",
        fontSize: 16,
        marginBottom: 10,
        cursor: "pointer",
      }}
    >
      ← Back
    </button>
  );
}