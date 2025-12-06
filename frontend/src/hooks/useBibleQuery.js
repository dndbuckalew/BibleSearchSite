import { useState } from "react";
import { queryBible } from "../services/bibleApi.js";

export function useBibleQuery() {
  const [loading, setLoading] = useState(false);
  const [verses, setVerses] = useState([]);
  const [error, setError] = useState("");

  async function runQuery(params) {
    try {
      setLoading(true);
      setError("");
      const result = await queryBible(params);
      setVerses(result.verses || []);
    } catch (err) {
      console.error(err);
      setError("Something went wrong contacting the Bible API.");
    } finally {
      setLoading(false);
    }
  }

  return { loading, verses, error, runQuery };
}