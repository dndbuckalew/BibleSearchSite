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
    <div className="space-y-4 pt-2">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="text-2xl text-neutral-900">
            Help sustain this Ministry
          </div>
          <div className="text-base text-neutral-800">
            If this experience has been meaningful, you can help support continued
            access for others through a simple donation.
          </div>
        </div>

        <button
          type="button"
          onClick={onDismiss}
          className="text-sm text-neutral-500 hover:text-neutral-700"
          aria-label="Dismiss donation prompt"
        >
          Dismiss
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
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
              className={`rounded border px-4 py-2 text-sm ${
                isSelected
                  ? "border-neutral-800 bg-neutral-800 text-white"
                  : "border-neutral-800 bg-white text-neutral-800 hover:bg-neutral-100"
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
          className={`rounded border px-4 py-2 text-sm ${
            selectedAmount === "other"
              ? "border-neutral-800 bg-neutral-800 text-white"
              : "border-neutral-800 bg-white text-neutral-800 hover:bg-neutral-100"
          }`}
        >
          Other
        </button>
      </div>

      {handoffUrl && (
        <div>
          <a
            href={handoffUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded border border-neutral-800 px-4 py-2 text-base font-medium text-neutral-800 bg-white inline-block"
          >
            Continue to Secure Donation
          </a>
        </div>
      )}

      {error && (
        <div className="text-sm text-neutral-700">
          {error}
        </div>
      )}

      {!handoffUrl && (
        <div>
          <button
            type="button"
            onClick={handleDonate}
            disabled={!selectedAmount || isLoading}
            className="rounded border border-neutral-800 px-4 py-2 text-base font-medium text-neutral-800 bg-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? "Starting Donation..." : "Continue to Donate"}
          </button>
        </div>
      )}
    </div>
  );
}
