"use client";

import { useState } from "react";

type DonationPromptProps = {
  onDismiss?: () => void;
};

export default function DonationPrompt({ onDismiss }: DonationPromptProps) {
  const [selectedAmount, setSelectedAmount] = useState<number | "other" | null>(null);

  const amounts = [5, 10, 20];

  return (
    <div className="mt-6 rounded-2xl border border-stone-200 bg-stone-50 p-4 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-stone-900">
            Help sustain this ministry
          </h3>
          <p className="mt-1 text-sm leading-6 text-stone-600">
            If this experience has been meaningful, you can help support continued access
            for others through a simple donation.
          </p>
        </div>

        <button
          type="button"
          onClick={onDismiss}
          className="text-sm text-stone-400 transition hover:text-stone-600"
          aria-label="Dismiss donation prompt"
        >
          Dismiss
        </button>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {amounts.map((amount) => {
          const isSelected = selectedAmount === amount;

          return (
            <button
              key={amount}
              type="button"
              onClick={() => setSelectedAmount(amount)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                isSelected
                  ? "bg-stone-900 text-white"
                  : "bg-white text-stone-700 border border-stone-200 hover:border-stone-300"
              }`}
            >
              ${amount}
            </button>
          );
        })}

        <button
          type="button"
          onClick={() => setSelectedAmount("other")}
          className={`rounded-full px-4 py-2 text-sm font-medium transition ${
            selectedAmount === "other"
              ? "bg-stone-900 text-white"
              : "bg-white text-stone-700 border border-stone-200 hover:border-stone-300"
          }`}
        >
          Other
        </button>
      </div>

      <div className="mt-4">
        <button
          type="button"
          disabled
          className="w-full rounded-xl bg-stone-900 px-4 py-3 text-sm font-medium text-white opacity-50"
        >
          Continue to Donate
        </button>
      </div>
    </div>
  );
}
