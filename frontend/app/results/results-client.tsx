// frontend/app/results/results-client.tsx
// Insert into: frontend/app/results/results-client.tsx (full file replacement)
"use client";

import { useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import QueryResultView, { QueryResponse } from "../components/QueryResultView";

/**
 * Phase 9.7 — Results is render-only:
 * - NO /api/query calls here
 * - NO /api/results calls here
 * - Binds to ONE QueryResponse passed via ?payload=
 * - If payload missing/invalid, user is never stranded: show humane message + CTA back.
 */

function safeParsePayload(raw: string): { ok: true; data: QueryResponse } | { ok: false; error: string } {
  try {
    const decoded = decodeURIComponent(raw);
    const parsed = JSON.parse(decoded);
    if (!parsed || typeof parsed !== "object") {
      return { ok: false, error: "Results payload was not recognized." };
    }
    return { ok: true, data: parsed as QueryResponse };
  } catch {
    return { ok: false, error: "Results payload could not be read. Please try again." };
  }
}

export default function ResultsClient() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Read once per navigation (no refresh model)
  const rawPayload = searchParams.get("payload");

  const parsed = useMemo(() => {
    if (!rawPayload) return { ok: false as const, error: "No results were provided for this page." };
    return safeParsePayload(rawPayload);
  }, [rawPayload]);

  // Optional: allow local UI dismiss of an error banner (no side effects)
  const [dismissed, setDismissed] = useState(false);
 
  if (!parsed.ok) {
    return (
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold">Scripture & Reflection</h2>

        {!dismissed && (
          <div className="rounded border border-neutral-200 bg-neutral-50 p-4">
            <div className="text-sm text-neutral-700">
              {parsed.error} You can return and ask again.
            </div>
            <div className="mt-3 flex gap-2">
              <button
                onClick={() => router.push("/")}
                className="rounded-md border border-neutral-300 px-4 py-2 text-sm font-medium text-neutral-800 bg-neutral-50 hover:bg-neutral-100"
              >
                Back to Reflection
              </button>
              <button
                onClick={() => setDismissed(true)}
                className="rounded-md border border-neutral-300 px-4 py-2 text-sm text-neutral-700 bg-white hover:bg-neutral-50"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        <div className="text-sm text-neutral-600 italic">
          This page displays one completed result. If you need to re-run or clarify, please return to the reflection page.
        </div>

        <button
          onClick={() => router.push("/")}
          className="mt-2 rounded border px-4 py-2"
        >
          Start New Reflection
        </button>
      </section>
    );
  }

  return (
    <section className="animate-fade-slide-in space-y-8">
      <h2 className="text-2xl font-semibold">Scripture & Reflection</h2>

      <QueryResultView data={parsed.data} />

      <button
        onClick={() => router.push("/")}
        className="mt-6 rounded border px-4 py-2"
      >
        Start New Reflection
      </button>
    </section>
  );
}
