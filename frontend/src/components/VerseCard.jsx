import React from "react";

export default function VerseCard({ verse, onClick }) {
  if (!verse) return null;
  const ref = `${verse.book} ${verse.chapter}:${verse.verse}`;
  return (
    <div className="card" onClick={onClick} style={{ cursor: "pointer" }}>
      <strong>{ref}</strong>
      <p style={{ marginTop: 6 }}>{verse.text}</p>
    </div>
  );
}