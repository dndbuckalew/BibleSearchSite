"use client";

import ExpandableSection from "./ExpandableSection";

interface VerseItem {
  reference: string;
  text: string;
  testament?: "OT" | "NT";
}

/**
 * Minimal QueryResponse shape (do NOT rename backend fields).
 * We keep this permissive to avoid breaking when backend adds fields.
 */
export type QueryResponse = {
  verses?: VerseItem[];
  context?: string | null;
  context_exploration?: string | null;
  summary?: string | null;
  reflection?: string | null;
  commentary?: string | null;
  want_commentary?: boolean;
};

export default function QueryResultView({ data }: { data: QueryResponse }) {
  const verses: VerseItem[] = Array.isArray(data.verses) ? data.verses : [];
  const summary = data.summary ?? null;
  const context = data.context ?? null;
  const contextExploration = data.context_exploration ?? null;
  const reflection = data.reflection ?? null;

  const summaryBlurb = "A brief summary of the theme or idea these verses are pointing to.";
  const contextBlurb = "Understanding the surrounding circumstances helps explain why these verses are being expressed in this moment.";
  const reflectionBlurb = "A gentle prompt to help you reflect on what this means personally.";

  // Group by testament if provided (OT/NT), but keep original order within each group.
  const ot = verses.filter((v) => v.testament === "OT");
  const nt = verses.filter((v) => v.testament === "NT");
  const unknown = verses.filter((v) => !v.testament);

  const distinctReferences = new Set(verses.map((v) => v.reference));
  const verseCount = distinctReferences.size;
  const scriptureHeading = verseCount === 1 ? "Scripture (KJV)" : "Scriptures (KJV)";

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
      <h3 className="text-xl font-medium text-neutral-900 dark:text-neutral-50">{title}</h3>
      <div className="text-sm text-neutral-600 dark:text-neutral-400">{blurb}</div>
      {children}
    </div>
  );

  const EmptyText = ({ text }: { text: string }) => (
    <div className="text-sm text-neutral-500 italic">{text}</div>
  );

  return (
    <div className="space-y-8">
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
                <h4 className="font-semibold text-neutral-700 dark:text-neutral-200">Old Testament</h4>
                {ot.map((v, i) => (
                  <div key={`ot-${i}`}>
                    <strong className="text-blue-600 dark:text-blue-400">{v.reference}</strong> — {v.text}
                  </div>
                ))}
              </div>
            )}

            {nt.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-neutral-700 dark:text-neutral-200">New Testament</h4>
                {nt.map((v, i) => (
                  <div key={`nt-${i}`}>
                    <strong className="text-blue-600 dark:text-blue-400">{v.reference}</strong> — {v.text}
                  </div>
                ))}
              </div>
            )}

            {unknown.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-neutral-700 dark:text-neutral-200">Scripture</h4>
                {unknown.map((v, i) => (
                  <div key={`u-${i}`}>
                    <strong className="text-blue-600 dark:text-blue-400">{v.reference}</strong> — {v.text}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Section>

      {summary ? (
        <ExpandableSection
          title="Summary"
          blurb={summaryBlurb}
          text={summary}
        />
      ) : (
        <Section title="Summary" blurb={summaryBlurb}>
          <EmptyText text="Summary is not available for this result." />
        </Section>
      )}

      {context ? (
        <ExpandableSection
          title="Context"
          blurb={contextBlurb}
          text={contextExploration ? `${context}\n\n${contextExploration}` : context}
        />
      ) : (
        <Section title="Context" blurb={contextBlurb}>
          <EmptyText text="Context is not available for this result." />
        </Section>
      )}

      {reflection ? (
        <ExpandableSection
          title="Reflection"
          blurb={reflectionBlurb}
          text={reflection}
        />
      ) : (
        <Section title="Reflection" blurb={reflectionBlurb}>
          <EmptyText text="Reflection is not available for this result." />
        </Section>
      )}
    </div>
  );
}
