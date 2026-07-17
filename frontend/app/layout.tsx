import type { Metadata } from "next";
import "./globals.css";

import Header from "./components/header/header";
import Navigation from "./components/navigation/navigation";
import Footer from "./components/footer/footer";

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

        <header className="border-b bg-white">
          <div className="max-w-4xl mx-auto px-6 py-4">
            <Header />
            <Navigation />
          </div>
        </header>

        <main className="flex-1 w-full max-w-4xl mx-auto px-4 py-8">
          {children}
        </main>

        <Footer />
      </body>
    </html>
  );
}
