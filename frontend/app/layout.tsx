import type { Metadata } from "next";
import "./globals.css";
import Link from "next/dist/client/link";

export const metadata: Metadata = {
  title: "Bible Therapy Assistant™",
  description:
    "Engage Scripture through deeper understanding, reflection, and the meaningful 'why' behind God's Word.",
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

    {/* ==============================================================
        Future Notification / Announcement Bar

        Reserved for future ministry announcements, release notices,
        weekly highlights, maintenance notifications, or other
        platform communications.

        The original Version 4.5 MVP banner was retired during the
        Phase 2A Platform Navigation redesign.

        This location has been intentionally preserved until the
        Web Master completes the final UI/UX design.

        ============================================================= */}

    {/*
    <div className="w-full bg-amber-100 border-b border-amber-300 text-amber-900 text-sm px-4 py-2 text-center">
      <strong>Version 4.5:</strong> This system is designed to support thoughtful reflection on Scripture. Content may continue to evolve and should not be considered authoritative guidance.
    </div>
    */}

        {/* Header */}
        <header className="border-b bg-white">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="text-center">
              <h1 className="text-2xl font-semibold">
                Bible Therapy Assistant™
              </h1>

              {/* Persistent Platform Navigation */}
              <nav
                aria-label="Primary Navigation"
                className="text-2xl font-semibold"
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  width: "100%",
                  gap: "32px",
                  marginTop: "16px",
              }}
            >
                <Link
                  href="/"
                  className="text-neutral-700 hover:text-blue-600 transition-colors"
                >
                  Home
                </Link>

                <Link
                  href="/stay-connected"
                  className="text-neutral-700 hover:text-blue-600 transition-colors"
                  style={{ marginRight: "32px", textAlign: "center" }}
                >
                  <span
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      lineHeight: "1.0",
                    }}
                >
                  <span>Stay</span>
                  <span>Connected</span>
                </span>
              </Link>

                <Link
                  href="/donation"
                  className="text-neutral-700 hover:text-blue-600 transition-colors"
                  style={{ marginRight: "32px" }}
                >
                  Donate
                </Link>

                {/*
                <button
                  className="text-neutral-700 hover:text-blue-600 transition-colors"
                  style={{ marginRight: "32px" }}
                >
                  Menu
                </button>
                */}
              </nav>
            </div>

            <div
              className="mt-6 text-center"
              style={{
                maxWidth: "900px",
                margin: "24px auto 0 auto",
                display: "flex",
                flexDirection: "column",
                gap: "20px",
              }}
            >
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
              <div>
                <strong>Bible Therapy Assistant™</strong>
              </div>
              <div>
                A product of TAD Concepts LLC
              </div>
              <div>
                © {currentYear} TAD Concepts LLC. All rights reserved.
              </div>
               <div>
                <strong>Patent Pending</strong>
              </div>
              <div>Powered by OpenAI</div>
            
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
