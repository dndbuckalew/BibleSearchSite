"use client";

import { useState } from "react";

type DonationPromptProps = {
  onDismiss?: () => void;
};

export default function DonationPrompt({ onDismiss }: DonationPromptProps) {
  const [selectedAmount, setSelectedAmount] = useState<number | "other" | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [handoffUrl, setHandoffUrl] = useState<string | null>(null);

  const amounts = [5, 10, 20];

  async function handleDonate() {
    if (!selectedAmount) {
      setError("Please select a donation amount.");
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const amount = selectedAmount === "other" ? 25 : selectedAmount;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/donation/create`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            amount,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Unable to start donation.");
      }

      const data = await response.json();

      setHandoffUrl(data?.qr_payload?.donation_url ?? null);

      console.log("Donation intent created:", data);
    } catch (err) {
      setError("Unable to start donation right now. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-blue-500/30 bg-blue-500/10 px-4 py-2.5">
        <span className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
          Help sustain this ministry
        </span>

        {!handoffUrl && (
          <div className="flex items-center gap-1.5">
            {amounts.map((amount) => {
              const isSelected = selectedAmount === amount;

              return (
                <button
                  key={amount}
                  type="button"
                  onClick={() => {
                    setHandoffUrl(null);
                    setSelectedAmount(selectedAmount === amount ? null : amount);
                  }}
                  className={`rounded-full border px-2.5 py-1 text-xs ${
                    isSelected
                      ? "border-blue-500 bg-blue-600 text-white"
                      : "border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-100 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-300 dark:hover:bg-neutral-800"
                  }`}
                >
                  ${amount}
                </button>
              );
            })}

            <button
              type="button"
              onClick={() => {
                setHandoffUrl(null);
                setSelectedAmount(selectedAmount === "other" ? null : "other");
              }}
              className={`rounded-full border px-2.5 py-1 text-xs ${
                selectedAmount === "other"
                  ? "border-blue-500 bg-blue-600 text-white"
                  : "border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-100 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-300 dark:hover:bg-neutral-800"
              }`}
            >
              Other
            </button>
          </div>
        )}

        <div className="ml-auto flex items-center gap-3">
          {handoffUrl ? (
            <a
              href={handoffUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-full bg-blue-600 px-3 py-1 text-xs font-medium text-white hover:bg-blue-500"
            >
              Continue to Secure Donation
            </a>
          ) : (
            <button
              type="button"
              onClick={handleDonate}
              disabled={!selectedAmount || isLoading}
              className="rounded-full bg-blue-600 px-3 py-1 text-xs font-medium text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-neutral-300 disabled:opacity-50 dark:disabled:bg-neutral-700"
            >
              {isLoading ? "Starting…" : "Donate"}
            </button>
          )}

          <button
            type="button"
            onClick={onDismiss}
            aria-label="Dismiss donation prompt"
            className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-4 w-4"
            >
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {error && <div className="px-1 text-xs text-red-600 dark:text-red-400">{error}</div>}
    </div>
  );
}
