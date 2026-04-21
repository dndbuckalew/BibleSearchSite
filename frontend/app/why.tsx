'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { runReflection } from './lib/btaApi';
import { getQueryCount } from "./lib/btaApi";

type DecisionResponse = {
  decision: 'PROCEED' | 'REDIRECT' | 'STOP';
  message?: string;
  execution_payload?: any;
};

export default function WhyPage() {
  const queryCount = Number(localStorage.getItem("bta_query_count") || "0");
  const router = useRouter();

  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // 🔒 Canonical source of truth for submitted input
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();

    const trimmed = inputRef.current?.value.trim() ?? '';
    if (!trimmed) return;

    setLoading(true);
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
      router.push(
        `/results?payload=${encodeURIComponent(
          JSON.stringify(responseBody)
        )}`
      );
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
    <section className="space-y-10 max-w-2xl">
      <h2 className="text-2xl font-semibold">Scripture & Reflection</h2>

      <p className="italic text-neutral-600">
        This space is designed to explore the deeper “why” behind Scripture —
        reflection, meaning, and personal understanding.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block text-sm text-neutral-700">
          What are you reflecting on?
        </label>

        <input
          ref={inputRef}
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., Genesis 1:1, hope in suffering, why faith matters"
          className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
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

        {queryCount >= 4 && (
          <div className="mt-4 p-3 border border-neutral-300 rounded">
            <p className="text-sm font-semibold">
              You’ve explored several reflections.
            </p>
            <p className="text-xs text-neutral-600">
              <p className="text-xs text-neutral-600">
              This space will always remain open to you. If you find BTA meaningful in your reflection, consider joining for updates and helping extend this experience of Scripture to others.
</p>
            </p>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="rounded-md border border-neutral-300 px-4 py-2 text-sm font-medium text-neutral-800 bg-neutral-50 hover:bg-neutral-100 disabled:opacity-50"
          >
            {loading ? 'Reflecting…' : 'Reflect →'}
          </button>
        </div>
      </form>
    </section>
  );
}
