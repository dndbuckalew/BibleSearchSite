// frontend/app/lib/btaApi.ts
export type ReflectionRequest = {
  question: string;
  persona?: string;
  translation?: string;
  want_commentary?: boolean;
};

export async function runReflection(request: ReflectionRequest) {
  const res = await fetch("http://localhost:8000/api/query", {
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
