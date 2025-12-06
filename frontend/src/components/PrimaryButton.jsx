import React from "react";

export default function PrimaryButton({ text, onClick, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        backgroundColor: disabled ? "#aac3f5" : "#1f4b99",
        color: "white",
        border: "none",
        borderRadius: 6,
        padding: "8px 16px",
        fontSize: 16,
      }}
    >
      {text}
    </button>
  );
}