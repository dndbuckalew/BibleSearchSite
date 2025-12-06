import React from "react";
import VerseCard from "../components/VerseCard.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import BackButton from "../components/BackButton.jsx";

export default function ResultsPage({ verses, loading, error, onSelectVerse, onBack }) {
  if (loading) return <LoadingSpinner />;

  return (
    <div className="container">
      <BackButton onClick={onBack} />
      <h2>Results</h2>
      {error && (
        <div
          style={{
            background: "#ffefef",
            padding: 10,
            borderRadius: 6,
            color: "#a30000",
            marginBottom: 15,
          }}
        >
          {error}
        </div>
      )}
      {verses.length === 0 && !error && (
        <p>No verses found yet. Try asking a question from the home screen.</p>
      )}
      {verses.map((v, idx) => (
        <VerseCard key={idx} verse={v} onClick={() => onSelectVerse(v)} />
      ))}
    </div>
  );
}