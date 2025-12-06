import React from "react";

export default function LoadingSpinner() {
  return (
    <div style={{ padding: 20, textAlign: "center" }}>
      <div style={{ fontSize: 18, marginBottom: 8 }}>Searching scriptures…</div>
      <div style={{ fontSize: 32 }}>⏳</div>
    </div>
  );
}