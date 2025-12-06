import { useState } from "react";
import { askBibleQuestion } from "./services/bibleApi";
import "./styles/global.css";
import Loader from "./components/Loader";
import ErrorMessage from "./components/ErrorMessage";

function App() {
  const [question, setQuestion] = useState("");
  const [translation, setTranslation] = useState("kjv");
  const [persona, setPersona] = useState("pastor");
  const [wantCommentary, setWantCommentary] = useState(true);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  // ---------------------------
  // Submit Handler
  // ---------------------------
  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setResults(null);

    try {
      const payload = {
        question,
        translation,
        persona,
        want_commentary: wantCommentary,
      };

      const data = await askBibleQuestion(payload);
      setResults(data);
    } catch (err) {
      setError("Unable to connect to the Bible backend. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------
  // UI Layout
  // ---------------------------
  return (
    <div className="container">
      <h1>Ask a Bible question</h1>

      {/* Question textarea */}
      <label>What is on your heart today?</label>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Type your question, situation, or feeling..."
      />

      {/* Translation */}
      <label>Translation</label>
      <select
        value={translation}
        onChange={(e) => setTranslation(e.target.value)}
      >
        <option value="kjv">KJV</option>
        <option value="niv">NIV</option>
        <option value="esv">ESV</option>
      </select>

      {/* Persona */}
      <label>Persona</label>
      <select
        value={persona}
        onChange={(e) => setPersona(e.target.value)}
      >
        <option value="pastor">PASTOR</option>
        <option value="teacher">TEACHER</option>
        <option value="counselor">COUNSELOR</option>

        {/* NEW PERSONA OPTIONS */}
        <option value="plain">PLAIN</option>
        <option value="friend">FRIEND</option>
        <option value="devotional">DEVOTIONAL GUIDE</option>
        <option value="layperson">LAYPERSON</option>
      </select>

      {/* Commentary toggle */}
      <div style={{ marginTop: "10px", marginBottom: "10px" }}>
        <label>
          <input
            type="checkbox"
            checked={wantCommentary}
            onChange={(e) => setWantCommentary(e.target.checked)}
          />
          {" "}
          Include commentary
        </label>
      </div>

      {/* Submit button */}
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Searching..." : "Search"}
      </button>

      {/* Loader & Error */}
      {loading && <Loader />}
      {error && <ErrorMessage message={error} />}

      {/* Results */}
      {results && (
        <div className="results">
          <h2>Verses</h2>
          {results.verses?.map((v, idx) => (
            <div key={idx} className="verse-block">
              <strong>
                {v.book} {v.chapter}:{v.verse}
              </strong>
              <p>{v.text}</p>
            </div>
          ))}

          {results.summary && (
            <div className="summary-block">
              <h2>Summary</h2>
              <p>{results.summary}</p>
            </div>
          )}

          {results.commentary && (
            <div className="commentary-block">
              <h2>Commentary</h2>
              <p>{results.commentary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;