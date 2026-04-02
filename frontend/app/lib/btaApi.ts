export type ReflectionRequest = {
  question: string;
  persona?: string;
  translation?: string;
  want_commentary?: boolean;
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
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: request.question,
      translation: request.translation ?? "KJV",
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
