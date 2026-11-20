export type ReflectionRequest = {
  question: string;
  persona?: string;
  translation?: string;
  want_commentary?: boolean;
  scripture_option?: string;
  parent_execution?: Execution;
  signal?: AbortSignal;
};

/**
 * API base URL
 *
 * - Local dev: defined in frontend/.env.local
 * - App Runner / prod: injected via NEXT_PUBLIC_API_BASE_URL at build time
 *
 * NOTE:
 * This value is compiled into the static build.
 * Do NOT provide a localhost fallback here.
 */
const API_BASE_RAW = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_RAW) {
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL is not defined. " +
      "Ensure it is set in frontend/.env.local (dev) or at build time (prod)."
  );
}

// Normalize: remove trailing slash if present
const API_BASE = API_BASE_RAW.replace(/\/$/, "");

/**
 * Run a reflection query against the backend
 */
export async function runReflection(request: ReflectionRequest) {
    // ✅ Query Counter (Phase 11 - Usage Tracking)
    const currentCount = Number(localStorage.getItem("bta_query_count") || "0");
    const newCount = currentCount + 1;
    localStorage.setItem("bta_query_count", String(newCount));

    console.log("BTA Query Count:", newCount);

  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    signal: request.signal,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: request.question,
      translation: request.translation,
      scripture_option: request.scripture_option,
      parent_execution: request.parent_execution,
      want_commentary: request.want_commentary ?? false,
      persona: request.persona,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Reflection request failed");
  }

  return res.json();
}

// ✅ Get current query count (used for gating later)
export function getQueryCount(): number {
  return Number(localStorage.getItem("bta_query_count") || "0");
}

export type Execution = { binding: string; resolved_scripture: ScriptureOption };
export type ScriptureOption = {
  option_id: string; edition_id: string; source_id: string; edition_label: string;
  source_label: string; dataset_revision: string | null;
};
export type SectionName = "scripture" | "summary" | "context" | "reflection";
export type StreamData = {
  verses?: { reference: string; text: string }[];
  scripture_provenance?: ScriptureOption;
  scripture_issues?: { reference: string; code: string }[];
  summary?: string; context?: string; context_exploration?: string; reflection?: string;
  intent_reaffirmation?: string;
};
export type StreamEvent =
  | { event: "section"; section: SectionName; data: StreamData; success: boolean }
  | { event: "complete"; success: boolean; escalation?: string }
  | { event: "failure"; section: SectionName; code: string };

export async function scriptureOptions(signal: AbortSignal): Promise<{default: string; options: ScriptureOption[]}> {
  const response = await fetch(API_BASE + "/api/scripture/options", { signal });
  if (!response.ok) throw new Error("Translation options unavailable.");
  return response.json();
}

export async function* resultEvents(execution: Execution, signal: AbortSignal): AsyncGenerator<StreamEvent> {
  const response = await fetch(API_BASE + "/api/results/stream", {
    method: "POST", signal, headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ execution_payload: execution }),
  });
  if (!response.ok || !response.body) throw new Error("Results stream unavailable.");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let boundary = buffer.indexOf("\n");
      while (boundary !== -1) {
        const line = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 1);
        if (line.trim()) yield JSON.parse(line) as StreamEvent;
        boundary = buffer.indexOf("\n");
      }
      if (done) break;
    }
    if (buffer.trim()) throw new Error("Incomplete results event.");
  } finally {
    if (!signal.aborted) await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
