"use client";

import { useEffect, useRef } from "react";
import ListeningControls, { listeningStatus } from "./ListeningControls";
import { useResultsReader } from "../lib/useResultsReader";
import type { StreamData, SectionName } from "../lib/btaApi";

export const sectionNames = ["scripture", "summary", "context", "reflection"] as const;
const title = (name: SectionName) => name.charAt(0).toUpperCase() + name.slice(1);

export type ActiveResult = {
  id: number;
  question: string;
  status: "pending" | "complete" | "partial" | "interrupted" | "failed";
  data: StreamData;
  ready: SectionName[];
  failed: SectionName[];
  code?: string;
  escalation?: string;
  announcement: string;
};

export default function IncrementalReader({
  result, onEdit, onStop, onExplore, onReturn, onRetry, restoreFocus,
}: {
  result: ActiveResult;
  onEdit: () => void;
  onStop: () => void;
  onExplore: (reference: string, index: number) => void;
  onReturn?: () => void;
  onRetry?: () => void;
  restoreFocus?: number;
}) {
  const reader = useResultsReader(String(result.id));
  const heading = useRef<HTMLHeadingElement>(null);
  const referenceButtons = useRef(new Map<number, HTMLButtonElement>());
  useEffect(() => {
    const target = restoreFocus === undefined ? null : referenceButtons.current.get(restoreFocus);
    (target ?? heading.current)?.focus();
  }, [result.id, restoreFocus]);

  const { data, status, ready, failed } = result;
  const provenance = data.scripture_provenance;
  const verses = data.verses ?? [];
  const scriptureTitle = provenance ? "Scripture · " + provenance.edition_label : "Scripture";
  const texts: Record<SectionName, string> = {
    scripture: verses.map(verse => verse.reference + ". " + verse.text).join("\n\n"),
    summary: data.summary ?? "",
    context: [data.context, data.context_exploration].filter(Boolean).join("\n\n"),
    reflection: data.reflection ?? "",
  };
  const complete = status === "complete";
  const stopAnd = (action: () => void) => { reader.stop(); action(); };

  return (
    <section className="space-y-6">
      <h2 tabIndex={-1} ref={heading} className="text-2xl font-semibold">
        {onReturn ? "Passage exploration" : "Scripture & Reflection"}
      </h2>
      <p className="whitespace-pre-wrap" dir="auto"><strong>Your question</strong>{"\n"}{result.question}</p>
      <div className="flex flex-wrap gap-2">
        {onReturn && <button className="bta-button" onClick={() => stopAnd(onReturn)}>Back to original result</button>}
        <button className="bta-button" onClick={() => stopAnd(onEdit)}>Edit question</button>
        {status === "pending" && <button className="bta-button" onClick={onStop}>Stop waiting</button>}
        <button className="bta-button" onClick={() => stopAnd(onEdit)}>Back to Home</button>
      </div>
      <p role="status" aria-live="polite">{result.announcement}</p>
      {(result.code === "source_unavailable" || result.code === "edition_unverified") && onRetry &&
        <button className="bta-button" onClick={onRetry}>Retry</button>}
      {result.escalation && <p>{result.escalation}</p>}
      {data.intent_reaffirmation && <p>{data.intent_reaffirmation}</p>}
      {complete && <ListeningControls reader={reader} selection="entire" label="Entire Response"
        text={sectionNames.map(name => title(name) + ". " + texts[name]).join("\n\n")} />}
      <p role="status" className="text-sm text-neutral-600">
        {reader.state.available === false ? "Listening is unavailable in this browser. You can continue reading the response."
          : reader.state.message || listeningStatus(reader.state.phase, reader.state.selection, reader.state.selection ?? "")}
      </p>
      {!result.escalation && sectionNames.map(name => {
        const sectionTitle = name === "scripture" ? scriptureTitle : title(name);
        const arrived = ready.includes(name) || failed.includes(name);
        return <section key={name} aria-label={title(name)} className="space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-xl font-medium">{sectionTitle}</h3>
            {texts[name] && <ListeningControls reader={reader} selection={name} label={sectionTitle} text={texts[name]} />}
          </div>
          {name === "scripture" && provenance && <p>Source: {provenance.source_label}</p>}
          {name === "scripture" ? verses.map((verse, index) => <p key={index} className="whitespace-pre-line">
            {complete ? <button type="button" className="font-semibold underline underline-offset-2"
              ref={element => { if (element) referenceButtons.current.set(index, element); else referenceButtons.current.delete(index); }}
              onClick={() => stopAnd(() => onExplore(verse.reference, index))}>{verse.reference}</button>
              : <strong>{verse.reference}</strong>}{" — "}{verse.text}
          </p>) : <p className="whitespace-pre-wrap" dir="auto">{texts[name]}</p>}
          {name === "scripture" && data.scripture_issues?.map((issue, index) =>
            <p key={index}>{issue.reference}: {issue.code === "missing_passage" ? "Passage not found." : "Scripture could not be verified."}</p>)}
          {failed.includes(name) ? <p>{title(name)} couldn’t be prepared.</p>
            : !arrived && <p>{status === "pending" ? "Preparing " + title(name) + "…" : "This section was not completed."}</p>}
        </section>;
      })}
    </section>
  );
}
