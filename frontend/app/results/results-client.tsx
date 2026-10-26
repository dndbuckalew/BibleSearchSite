// frontend/app/results/results-client.tsx
// Insert into: frontend/app/results/results-client.tsx (full file replacement)
"use client";

import { useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ResultsDonationInvitation from "../components/donation/ResultsDonationInvitation";
import ExpandableSection from "../components/ExpandableSection";
import ListeningControls, { listeningStatus } from "../components/ListeningControls";
import { referenceForSpeech } from "../lib/resultsReader";
import { useResultsReader } from "../lib/useResultsReader";

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

  // --- Section helpers (Phase 9.7: never render blank containers) ---
const Section = ({
    title,
    blurb,
    children,
    listening,
  }: {
    title: string;
    blurb: string;
    children: React.ReactNode;
    listening?: React.ReactNode;
  }) => (
    <div className="space-y-2">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2">
        <h3 className="text-xl font-medium">{title}</h3>
        {listening}
      </div>
      <div className="text-sm text-neutral-600">{blurb}</div>
      {children}
    </div>
  );

const EmptyText = ({ text }: { text: string }) => (
  <div className="text-sm text-neutral-600 italic">{text}</div>
  );


export default function ResultsClient() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Read once per navigation (no refresh model)
  const rawPayload = searchParams.get("payload");
  const reader = useResultsReader(rawPayload);

  const parsed = useMemo(() => {
    if (!rawPayload) return { ok: false as const, error: "No results were provided for this page." };
    return safeParsePayload(rawPayload);
  }, [rawPayload]);

  const [donationDismissed, setDonationDismissed] = useState(false);

  // Optional: allow local UI dismiss of an error banner (no side effects)
  const [dismissed, setDismissed] = useState(false);
  const backToHome = (
    <button
      type="button"
      onClick={() => { reader.stop(); router.push("/"); }}
      className="bta-button mb-4"
    >
      <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="m3 10 9-7 9 7M5 9v12h14V9M9 21v-8h6v8" />
      </svg>
      Back to Home
    </button>
  );
 
  if (!parsed.ok) {
    return (
      <section className="space-y-6">
        {backToHome}
        <h2 className="text-2xl font-semibold">Scripture & Reflection</h2>

        {!dismissed && (
          <div className="rounded border border-neutral-200 bg-neutral-50 p-4">
            <div className="text-sm text-neutral-700">
              {parsed.error} You can return and ask again.
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                onClick={() => { reader.stop(); router.push("/"); }}
                className="bta-button"
              >
                Back to Reflection
              </button>
              <button
                onClick={() => setDismissed(true)}
                className="bta-button"
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
          onClick={() => { reader.stop(); router.push("/"); }}
          className="bta-button mt-2"
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

  // Use response content, never page text: controls and unrelated UI cannot enter speech.
  // Match the displayed testament grouping, including its order within each group.
  const scriptureText = [
    ot.length ? ['Old Testament', ...ot.map(v => `${referenceForSpeech(v.reference)}. ${v.text}`)].join('\n\n') : '',
    nt.length ? ['New Testament', ...nt.map(v => `${referenceForSpeech(v.reference)}. ${v.text}`)].join('\n\n') : '',
    unknown.length ? ['Scripture', ...unknown.map(v => `${referenceForSpeech(v.reference)}. ${v.text}`)].join('\n\n') : '',
  ].filter(Boolean).join('\n\n');
  const contextText = context ? [context, contextExploration].filter(Boolean).join('\n\n') : '';
  const introduction = data.intent_reaffirmation ?? '';
  const entireText = [
    introduction,
    scriptureText ? `${scriptureHeading}.\n${scriptureText}` : '',
    summary?.trim() ? `Summary.\n${summary}` : '',
    contextText.trim() ? `Context.\n${contextText}` : '',
    reflection?.trim() ? `Reflection.\n${reflection}` : '',
  ].filter(Boolean).join('\n\n\n');
  const controls = (selection: string, label: string, text: string) => (
    <ListeningControls reader={reader} selection={selection} label={label} text={text} />
  );



  return (
  <>
    {backToHome}
    {data.intent_reaffirmation && (
      <div
        style={{
          marginTop: "28px",
          marginBottom: "48px",
          paddingLeft: "8px",
          paddingRight: "8px",
        }}
      >
        <p
          style={{
            margin: 0,
            fontSize: "1.05rem",
            lineHeight: "1.8",
            color: "#374151",
            textAlign: "left",
          }}
        >
          {data.intent_reaffirmation}
        </p>
        <div className="mt-2 flex justify-end">{controls("introduction", "Introduction", introduction)}</div>
      </div>
    )}

  <section className="space-y-8">
  <h2
    style={{
      textAlign: "center",
      fontSize: "clamp(1.5rem, 1.25rem + 1vw, 2rem)",
      fontWeight: 700,
      marginBottom: "32px",
    }}
  >
    Scripture & Reflection
  </h2>

      <div className="space-y-2">
        {controls("entire", "Entire Response", entireText)}
        <p role="status" aria-live="polite" className={reader.state.selection ? "sr-only" : "text-sm text-neutral-600"}>
          {reader.state.available === false ? 'Listening is unavailable in this browser. You can continue reading the response.'
            : reader.state.message || listeningStatus(reader.state.phase, reader.state.selection,
              reader.state.selection === 'scripture' ? scriptureHeading : reader.state.selection ? reader.state.selection.charAt(0).toUpperCase() + reader.state.selection.slice(1) : '')}
        </p>
      </div>

      {/* 1) Scripture */}
      <Section
        title={scriptureHeading}
        listening={controls("scripture", scriptureHeading, scriptureText)}
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
        listening={controls("summary", "Summary", summary ?? "")}
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
        listening={controls("context", "Context", contextText)}
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
        listening={controls("reflection", "Reflection", reflection ?? "")}
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

          <button
        onClick={() => { reader.stop(); router.push("/"); }}
        className="bta-button mt-6"
      >
        Start New Reflection
      </button>

    {!donationDismissed && (
      <ResultsDonationInvitation onDismiss={() => setDonationDismissed(true)} />
    )}  
    </section>
  </>
  );
} 
