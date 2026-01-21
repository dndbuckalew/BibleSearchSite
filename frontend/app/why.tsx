'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function WhyPage() {
  const router = useRouter();
  const [question, setQuestion] = useState('');

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();

    if (!question.trim()) return;

    router.push(`/results?q=${encodeURIComponent(question.trim())}`);
  };

  return (
    <section className="space-y-10 max-w-2xl">
      <h2 className="text-2xl font-semibold">
        Scripture & Reflection
      </h2>

      <p className="italic text-neutral-600">
        This space is designed to explore the deeper “why” behind Scripture —
        reflection, meaning, and personal understanding.
      </p>

      {/* Phase 7.6 / 7.7 — Query Entry */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block text-sm text-neutral-700">
          What are you reflecting on?
        </label>

        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., Genesis 1:1, hope in suffering, why faith matters"
          className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
        />

        {/* Explicit action boundary */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="rounded-md border border-neutral-300 px-4 py-2 text-sm font-medium text-neutral-800 bg-neutral-50 hover:bg-neutral-100"
          >
            Reflect →
          </button>
        </div>
      </form>
    </section>
  );
}

