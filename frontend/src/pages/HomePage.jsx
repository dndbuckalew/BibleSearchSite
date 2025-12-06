import React, { useState } from "react";
import SearchInput from "../components/SearchInput.jsx";
import Dropdown from "../components/Dropdown.jsx";
import ToggleSwitch from "../components/ToggleSwitch.jsx";
import PrimaryButton from "../components/PrimaryButton.jsx";

export default function HomePage({ onSearch }) {
  const [question, setQuestion] = useState("");
  const [translation, setTranslation] = useState("kjv");
  const [persona, setPersona] = useState("pastor");
  const [wantCommentary, setWantCommentary] = useState(true);

  function handleSearch() {
    onSearch({
      question,
      translation,
      persona,
      wantCommentary,
    });
  }

  return (
    <div className="container">
      <h2>Ask a Bible question</h2>
      <SearchInput value={question} onChange={setQuestion} />
      <Dropdown
        label="Translation"
        value={translation}
        options={["kjv", "niv", "esv"]}
        onChange={setTranslation}
      />
      <Dropdown
        label="Persona"
        value={persona}
        options={["pastor", "teacher", "counselor", "scholar"]}
        onChange={setPersona}
      />
      <ToggleSwitch
        label="Include commentary"
        value={wantCommentary}
        onChange={setWantCommentary}
      />
      <PrimaryButton
        text="Search"
        onClick={handleSearch}
        disabled={!question.trim()}
      />
    </div>
  );
}