import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bible Therapy Assistant (BTA) — Version 2",
  description:
    "A reflective Bible study assistant designed to support understanding, context, and personal reflection in Scripture.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const currentYear = new Date().getFullYear();

  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-50 text-neutral-900 flex flex-col">
        {/* Version 2 Banner */}
        <div className="w-full bg-amber-100 border-b border-amber-300 text-amber-900 text-sm px-4 py-2 text-center">
          <strong>Version 3.1.2:</strong> This system is designed to support thoughtful reflection on Scripture. Content may continue to evolve and should not be considered authoritative guidance.
        </div>

        {/* Header */}
        <header className="border-b bg-white">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <h1 className="text-2xl font-semibold">
              Bible Therapy Assistant
            </h1>
            <p className="text-sm text-neutral-600 mt-1">
              Exploring Scripture through context, understanding, and reflection
            </p>
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
              for educational and spiritual exploration.
            </div>

            <div>
              It is <strong>not</strong> medical advice, counseling, crisis
              support, or authoritative theological instruction.
            </div>

            <div className="text-xs text-neutral-500 pt-2 space-y-1">
              <div>Powered by OpenAI</div>
              <div>© {currentYear} Bible Therapy Assistant — Version 3.1.2</div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
