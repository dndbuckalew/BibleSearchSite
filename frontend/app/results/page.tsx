'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { runReflection } from '../lib/btaApi';

interface VerseItem {
  reference: string;
  text: string;
  testament?: 'OT' | 'NT';
  book_order?: number;
  chapter?: number;
  verse?: number;
}

export default function ResultsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const query =
    searchParams.get('q') ?? 'comfort in times of trouble';
  const persona =
    searchParams.get('persona') ?? 'pastoral';

  const [verses, setVerses] = useState<VerseItem[]>([]);
  const passageLabel = verses.length === 1 ? "This passage" : "These passages";
  const [context, setContext] = useState<string | null>(null);
  const [reflection, setReflection] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const startNewReflection = () => {
    router.push('/');
  };

  // ------------------------------------------------------------
  // Fetch scripture + context + reflection
  // ------------------------------------------------------------
  useEffect(() => {
    let isMounted = true;

    const fetchResults = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await runReflection({
          question: query,
          persona,
        });

        if (!isMounted) return;

        setVerses(data?.verses ?? []);
        setContext(data?.summary ?? null);
        setReflection(data?.commentary ?? null);
      } catch (err: any) {
        if (isMounted) {
          setError(err?.message ?? 'Failed to load reflection');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchResults();

    return () => {
      isMounted = false;
    };
  }, [query, persona]);

  // Group verses by Testament (canonical order already applied)
  const oldTestamentVerses = verses.filter(
    (v) => v.testament === 'OT'
  );

  const newTestamentVerses = verses.filter(
    (v) => v.testament === 'NT'
  );

  // ------------------------------------------------------------
  // Render
  // ------------------------------------------------------------
  return (
    <section className="space-y-10">
      <h2 className="text-2xl font-semibold">
        Scripture & Reflection
      </h2>

      {/* Scripture */}
      <div className="space-y-4">
        <h3 className="text-xl font-medium">Scripture (KJV)</h3>

        {loading && <p>Loading Scripture…</p>}

        {error && (
          <p className="text-red-600">
            Error: {error}
          </p>
        )}

        {!loading && !error && verses.length === 0 && (
          <p className="italic text-neutral-600">
            No verses returned.
          </p>
        )}

        {!loading && !error && verses.length > 0 && (
          <div className="space-y-4">
            {oldTestamentVerses.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">
                  Old Testament
                </h4>
                {oldTestamentVerses.map((v, idx) => (
                  <p key={`ot-${idx}`} className="text-neutral-700">
                    <strong>{v.reference}</strong> — {v.text}
                  </p>
                ))}
              </div>
            )}

            {newTestamentVerses.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">
                  New Testament
                </h4>
                {newTestamentVerses.map((v, idx) => (
                  <p key={`nt-${idx}`} className="text-neutral-700">
                    <strong>{v.reference}</strong> — {v.text}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Context */}
      <div className="space-y-2">
        <h3 className="text-xl font-medium">Context</h3>
        <p className="text-neutral-700">
          {context
            ? `${passageLabel} are connected by a shared theme found across Scripture, showing continuity in how the Bible addresses this question.`
            : "Contextual analysis is not available."}
        </p>
      </div>
          
      {/* Reflection */}
      <div className="space-y-2">
        <h3 className="text-xl font-medium">Reflection</h3>
        <p className="text-neutral-700">
          {reflection ??
            'Reflective guidance is not available.'}
        </p>
      </div>

      {/* Start New Reflection */}
      <div className="mt-10 border-t pt-6">
        <div className="flex items-center justify-between">
          <p className="text-sm text-neutral-600">
            Want to explore a different question or perspective?
          </p>

          <button
            onClick={startNewReflection}
            className="rounded-md border border-neutral-300 px-4 py-2 text-sm font-medium text-neutral-800 bg-neutral-50 hover:bg-neutral-100"
          >
            Start New Reflection
          </button>
        </div>
      </div>
    </section>
  );
}
