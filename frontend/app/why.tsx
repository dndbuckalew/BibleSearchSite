'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { runReflection } from './lib/btaApi';
import { getQueryCount } from "./lib/btaApi";
import DonationPrompt from "./components/donation/DonationPrompt";

type DecisionResponse = {
  decision: 'PROCEED' | 'REDIRECT' | 'STOP';
  message?: string;
  execution_payload?: any;
};

export default function WhyPage() {
  const [queryCount, setQueryCount] = useState(0);
  useEffect(() => {
  if (typeof window !== "undefined") {
    const count = Number(localStorage.getItem("bta_query_count") || "0");
    setQueryCount(count);
  }
}, []);
  const router = useRouter();
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [isFinalStage, setIsFinalStage] = useState(false);

  // 🔒 Canonical source of truth for submitted input
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();

    const trimmed = inputRef.current?.value.trim() ?? '';
    if (!trimmed) return;

    setLoading(true);
    setLoadingMessage(
      'Searching Scripture and preparing your response...'
    );

    setTimeout(() => {
      setLoadingMessage(
        'Looking at surrounding passages and deeper context...'
      );
    }, 5000);

    setTimeout(() => {
      setLoadingMessage(
        'Building reflection and preparing insight from the passages found'
      );

      setIsFinalStage(true);
    }, 12500);

    setMessage(null);

    try {
      // --------------------------------------------------
      // HEART: /api/query
      // --------------------------------------------------
      const decisionResult: DecisionResponse = await runReflection({
        question: trimmed,
        want_commentary: true,
      });

      if (
        decisionResult.decision === 'REDIRECT' ||
        decisionResult.decision === 'STOP'
      ) {
        setMessage(
          decisionResult.message ??
            'That question may need a little more clarity. Could you share more about what you’re reflecting on?'
        );
        setLoading(false);
        return;
      }

      if (!decisionResult.execution_payload) {
        setMessage(
          'Something unexpected occurred while preparing your reflection. Please try again.'
        );
        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // HANDS: /api/results
      // --------------------------------------------------
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/results`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            execution_payload: decisionResult.execution_payload,
          }),
        }
      );

      const responseBody = await res.json();

      // --------------------------------------------------
      // Structured 422 clarification (WHY gate)
      // --------------------------------------------------
      if (res.status === 422 && typeof responseBody?.detail === 'string') {
        setMessage(responseBody.detail);
        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // True system-level failure (not structured application response)
      // --------------------------------------------------
      if (!res.ok) {
        setMessage(
          'We ran into an issue while processing your request. Please try again.'
        );
        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // Normal Success Path
      // --------------------------------------------------
      
      setLoadingMessage(
        'Preparing your response for display...'
      );

      setTimeout(() => {
        router.push(
          `/results?payload=${encodeURIComponent(
            JSON.stringify(responseBody)
          )}`
        );
      }, 250);

    } catch (err: any) {
      // Network-level failure only
      setMessage(
        'We ran into an issue while processing your request. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-10 max-w-2xl pl-4">
      <h2 className="text-2xl font-semibold">
        Explore Scripture & Understanding
      </h2>

      <div className="space-y-5 text-neutral-700">
        <p>
          BTA allows Christians, missionaries, and spiritually searching individuals
          to explore Scripture in multiple ways — whether entering a Bible verse,
          exploring an entire chapter, asking questions naturally, searching by topic
          or emotion, or seeking deeper understanding behind God’s Word.
        </p>

        <p className="text-sm text-neutral-500 py-2">
          Examples: John 3:16, Psalm 23, Romans 8:28–39,
          “What does God say about fear?”, “I feel anxious and need peace.”
        </p>

        <p className="text-neutral-700">
          In contrast to traditional Bible search apps or concordances, BTA helps people
          move beyond isolated verse searching into thoughtful understanding,
          connected meaning, reflection, and the deeper “why” behind Scripture
          while keeping God’s Word central to the experience.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block text-sm text-neutral-700">
          What would you like to explore in Scripture?
        </label>

        <input
          ref={inputRef}
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., Genesis 1:1, hope in suffering, why faith matters"
          className="w-full rounded-md border border-neutral-400 px-4 py-3 text-base text-neutral-900 bg-white shadow-sm placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-neutral-300"
          disabled={loading}
        />

        {message && (
          <div className="space-y-1">
            <p className="text-sm text-neutral-600 italic">{message}</p>
            <p className="text-xs text-neutral-500">
              You can clarify your question by adding more detail to your initial
              question, then clicking{' '}
              <span className="font-medium">Reflect →</span> again.
            </p>
          </div>
        )}

        {loading && loadingMessage && (
          <div className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2">
            <p className="text-sm text-neutral-700 italic">
              {loadingMessage}
              {isFinalStage && (
                <span className="inline-block animate-pulse">...</span>
              )}
            </p>
          </div>
        )}

        <div className="flex justify-center pt-4">
          <button
            type="submit"
            disabled={loading}
            style={{
              border: "1px solid #a3a3a3",
              borderRadius: "8px",
              padding: "12px 24px",
              backgroundColor: "#ffffff",
              color: "#262626",
              fontSize: "14px",
              fontWeight: 500,
              cursor: "pointer",
              boxShadow: "0 1px 2px rgba(0,0,0,0.08)",
            }}
          >
            {loading ? "Exploring Scripture..." : "Explore Scripture"}
          </button>
        </div>
      </form>
    </section>
  );
}

