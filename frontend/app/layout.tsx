import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bible Therapy Assistant (BTA) — Version 4.5",
  description:
    "A Scripture-centered, AI-assisted experience designed to help Christians, missionaries, and seekers engage God’s Word through deeper understanding, reflection, connected meaning, and the 'why' behind Scripture while keeping God’s Word central to the journey of spiritual understanding.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const currentYear = new Date().getFullYear();

  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-50 text-neutral-800 flex flex-col">
        {/* Version 2 Banner */}
        <div className="w-full bg-amber-100 border-b border-amber-300 text-amber-900 text-sm px-4 py-2 text-center">
          <strong>Version 4.5:</strong> This system is designed to support thoughtful reflection on Scripture. Content may continue to evolve and should not be considered authoritative guidance.
        </div>

        {/* Header */}
        <header className="border-b bg-white">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <h1 className="text-2xl font-semibold">
              Bible Therapy Assistant
            </h1>

            <div className="mt-2 space-y-2">
              <p className="text-sm text-neutral-700">
                Helping Christians, missionaries, and spiritually searching individuals
                engage Scripture through deeper understanding, reflection, and the
                meaningful “why” behind God’s Word.
              </p>

              <p className="text-sm text-neutral-600">
                Unlike traditional Bible search apps or concordances, BTA uses carefully
                guided AI assistance to help people explore Scripture through connected
                meaning, continuity, and thoughtful reflection while keeping God’s Word
                at the center of the experience.
              </p>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-4xl mx-auto px-4 py-8">
          {children}
        </main>

        {/* Footer / Guardrails */}
        <footer className="border-t bg-white mt-12">
          <div className="max-w-4xl mx-auto px-4 py-6 text-sm text-neutral-600 space-y-2">
            <div>
              This application provides Scripture (KJV) and contextual reflection
              for educational and spiritual exploration. It is <strong>not</strong> medical advice, counseling, crisis
              support, or authoritative theological instruction.
            </div>

            <div className="pt-3">
              Questions, feedback, ministry inquiries, church partnerships, or
              suggestions? Contact us at{" "}
              <a
                href="mailto:info@bibleta.com"
                className="text-lg font-semibold underline text-blue-600 hover:text-blue-800"
              >
                info@bibleta.com
              </a>
            </div>

            <div className="text-xs text-neutral-500 pt-2 space-y-1">
              <div>Powered by OpenAI</div>
              <div>© {currentYear} Bible Therapy Assistant — Version 4.5</div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
