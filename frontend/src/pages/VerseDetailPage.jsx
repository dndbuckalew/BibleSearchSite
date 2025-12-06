import React from "react";
import BackButton from "../components/BackButton.jsx";
import PrimaryButton from "../components/PrimaryButton.jsx";

export default function VerseDetailPage({ verse, onBack }) {
  if (!verse) return null;
  const ref = `${verse.book} ${verse.chapter}:${verse.verse}`;

  return (
    <div className="container">
      <BackButton onClick={onBack} />
      <h2>{ref}</h2>
      <p style={{ marginTop: 10, fontSize: 18 }}>{verse.text}</p>
      <div style={{ marginTop: 20 }}>
        <PrimaryButton
          text="Commentary (future feature)"
          onClick={() => {}}
        />
      </div>
    </div>
  );
}