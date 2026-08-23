import type { Metadata } from "next";
import "./globals.css";
import ThemeToggle from "./components/ThemeToggle";

const THEME_INIT_SCRIPT = `
  try {
    if (localStorage.getItem('bta-theme') === 'dark') {
      document.documentElement.classList.add('dark');
    }
  } catch (e) {}
`;

export const metadata: Metadata = {
  title: "Bible Therapy Assistant™ (BTA) — Version 4.5",
  description:
    "Bible Therapy Assistant™ is a Scripture-centered, AI-assisted experience designed to help Christians, missionaries, and seekers engage God’s Word through deeper understanding, reflection, connected meaning, and the 'why' behind Scripture while keeping God’s Word central to the journey of spiritual understanding.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const currentYear = new Date().getFullYear();

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* A raw synchronous script (not next/script) — it must execute as the browser
            parses the HTML, before first paint, or the theme flashes on every load.
            next/script's "beforeInteractive" strategy queues through Next's own runtime
            and does not run early enough for this. */}
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-screen bg-white text-neutral-900 flex flex-col dark:bg-neutral-800 dark:text-neutral-100">
        <h1 className="sr-only">Bible Therapy Assistant</h1>

        {/* Version 2 Banner */}
        <div className="relative w-full bg-blue-50 border-b border-blue-200 text-blue-700 text-xs px-4 py-1.5 text-center dark:bg-blue-950/50 dark:border-blue-900/60 dark:text-blue-300">
          v4.5 — For reflection and study, not authoritative guidance.
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <ThemeToggle />
          </div>
        </div>

        {/* Main Content */}
        <main className="flex flex-1 flex-col w-full max-w-4xl mx-auto px-4 py-8">
          {children}
        </main>

        {/* Footer / Guardrails */}
        <footer className="border-t border-neutral-200 bg-neutral-50 mt-8 dark:border-neutral-800 dark:bg-neutral-900/60">
          <div className="max-w-4xl mx-auto px-4 py-4 text-xs text-neutral-500 space-y-1.5">
            <div>
              Scripture (KJV) with contextual reflection for study — not medical
              advice, counseling, crisis support, or authoritative theological
              instruction.
            </div>

            <div>
              Questions or feedback?{" "}
              <a
                href="mailto:info@bibleta.com"
                className="underline text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
              >
                info@bibleta.com
              </a>
            </div>

            <div>
              <strong className="text-neutral-600 dark:text-neutral-400">Bible Therapy Assistant™</strong> · A product of TAD
              Concepts LLC · © {currentYear} · Patent Pending · Powered by
              OpenAI
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
