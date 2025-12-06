import React from "react";

export default function SearchInput({ value, onChange }) {
  return (
    <div style={{ marginBottom: "12px" }}>
      <label style={{ display: "block", marginBottom: 4 }}>
        What is on your heart today?
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        style={{ width: "100%", padding: 8, resize: "vertical" }}
        placeholder="Type your question, situation, or feeling..."
      />
    </div>
  );
}