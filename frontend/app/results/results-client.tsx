// frontend/app/results/results-client.tsx
// Insert into: frontend/app/results/results-client.tsx (full file replacement)
"use client";

import { useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import DonationPrompt from "../components/donation/DonationPrompt";
import ExpandableSection from "../components/ExpandableSection";

/**
 * Phase 9.7 — Results is render-only:
 * - NO /api/query calls here
 * - NO /api/results calls here
 * - Binds to ONE QueryResponse passed via ?payload=
 * - If payload missing/invalid, user is never stranded: show humane message + CTA back.
 */

interface VerseItem {
  reference: string;
  text: string;
  testament?: "OT" | "NT";
}

/**
 * Minimal QueryResponse shape (do NOT rename backend fields).
 * We keep this permissive to avoid breaking when backend adds fields.
 */
type QueryResponse = {
  intent_reaffirmation?: string | null;
  verses?: VerseItem[];
  context?: string | null;
  context_exploration?: string | null;
  summary?: string | null;
  reflection?: string | null;
  commentary?: string | null;
  want_commentary?: boolean;
};

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

  const [donationDismissed, setDonationDismissed] = useState(false);

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

  const data = parsed.data;

  const verses: VerseItem[] = Array.isArray(data.verses) ? data.verses : [];
  const summary = data.summary ?? null;
  const context = data.context ?? null;
  const contextExploration = data.context_exploration ?? null;
  const reflection = data.reflection ?? null;
  const commentary = data.commentary ?? null;
  const wantCommentary = Boolean(data.want_commentary);

  // Group by testament if provided (OT/NT), but keep original order within each group.
  const ot = verses.filter((v) => v.testament === "OT");
  const nt = verses.filter((v) => v.testament === "NT");
  const unknown = verses.filter((v) => !v.testament);

  const distinctReferences = new Set(verses.map((v) => v.reference));
  const verseCount = distinctReferences.size;
  const scriptureHeading = verseCount === 1 ? "Scripture (KJV)" : "Scriptures (KJV)";

  // --- Section helpers (Phase 9.7: never render blank containers) ---
  const Section = ({
    title,
    blurb,
    children,
  }: {
    title: string;
    blurb: string;
    children: React.ReactNode;
  }) => (
    <div className="space-y-2">
      <h3 className="text-xl font-medium">{title}</h3>
      <div className="text-sm text-neutral-600">{blurb}</div>
      {children}
    </div>
  );

  const EmptyText = ({ text }: { text: string }) => (
  <div className="text-sm text-neutral-600 italic">{text}</div>
  );

  return (
  <>
  {data.intent_reaffirmation && (
    <>
      <div className="max-w-3xl">
        <p className="text-lg leading-relaxed text-gray-700 dark:text-gray-300">
          {data.intent_reaffirmation}
        </p>
      </div>

      <div className="h-24 bg-yellow-200" />
    </>
  )}

  <section className="space-y-8">
    <h2 className="text-2xl font-semibold">
      Scripture & Reflection
    </h2>

      {/* 1) Scripture */}
      <Section
        title={scriptureHeading}
        blurb="These are the verses BTA selected for your request."
      >
        {verses.length === 0 ? (
          <EmptyText text="No verses were returned for this request. Please go back and try a different wording." />
        ) : (
          <div className="space-y-4">
            {ot.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">Old Testament</h4>
                {ot.map((v, i) => (
                  <div key={`ot-${i}`}>
                    <strong>{v.reference}</strong> — {v.text}
                  </div>
                ))}
              </div>
            )}

            {nt.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">New Testament</h4>
                {nt.map((v, i) => (
                  <div key={`nt-${i}`}>
                    <strong>{v.reference}</strong> — {v.text}
                  </div>
                ))}
              </div>
            )}

            {unknown.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">Scripture</h4>
                {unknown.map((v, i) => (
                  <div key={`u-${i}`}>
                    <strong>{v.reference}</strong> — {v.text}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </Section>
      
      <Section
        title="Summary"
        blurb="A brief summary of the theme or idea these verses are pointing to."
      >
        {summary ? (
          <ExpandableSection
            preview={
              <div className="whitespace-pre-line">
                {summary.split("\n\n")[0]}
              </div>
            }
            expanded={
              summary.split("\n\n").length > 1 ? (
                <div className="space-y-4">
                  <div className="h-4" />

                  <div className="whitespace-pre-line">
                    {summary.split("\n\n").slice(1).join("\n\n")}
                  </div>
                </div>
              ) : (
                <div />
              )
            }
          />
        ) : (
          <EmptyText text="Summary is not available for this result." />
        )}
      </Section>

      {/* --------------------------------------------------------------
   Phase 2.0 — Context Independent Render Domain
   Context restored as an independent presentation domain.
   QueryService orchestration unchanged.
   Context generation unchanged.
-------------------------------------------------------------- */}

      <Section
        title="Context"
        blurb="Understanding the surrounding circumstances helps explain why these verses are being expressed in this moment."
      >
       {context ? (
      <ExpandableSection
        preview={
          <div className="whitespace-pre-line">
            {context}
          </div>
        }
        expanded={
          contextExploration ? (
            <div className="space-y-4">
              <div className="h-4" />

              <div className="whitespace-pre-line">
                {contextExploration}
              </div>
            </div>
          ) : (
            <div />
          )
        }
      />  
      ) : (
        <EmptyText text="Context is not available for this result." />
      )}

      </Section>

      {/* 4) Reflection */}
      <Section
        title="Reflection"
        blurb="A gentle prompt to help you reflect on what this means personally."
      >        
        {reflection ? (
          <div className="whitespace-pre-line">
            {reflection}
          </div>
        ) : (
          <EmptyText text="Reflection is not available for this result." />
        )}

      </Section>

{/* --------------------------------------------------------------
   Phase 9.1F — Commentary Hidden (Deferred)
-------------------------------------------------------------- */}
{/*
{wantCommentary && (
  <Section
    title="Commentary"
    blurb="Commentary is an optional future-facing layer that may be provided when requested."
  >
{commentary ? (
  <div className="whitespace-pre-line">{commentary}</div>
) : (
  <EmptyText text="Commentary is not available yet. This section will be expanded in a future release." />
)}

  </Section>
)}
*/}

          <button
        onClick={() => router.push("/")}
        className="mt-6 rounded border px-4 py-2"
      >
        Start New Reflection
      </button>

      {/* ## DEV_LOG_START */}
      {/* console.log("Results payload (render-only):", data); */}
      {/* ## DEV_LOG_END */}

    {!donationDismissed && (
      <DonationPrompt onDismiss={() => setDonationDismissed(true)} />
    )}  
    </section>
  </>
  );
} 
