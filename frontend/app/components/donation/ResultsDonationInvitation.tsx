"use client";

import Link from "next/link";
import { DONATIONS_ENABLED } from "../../platform/capabilities";

type ResultsDonationInvitationProps = {
  onDismiss: () => void;
};

export default function ResultsDonationInvitation({
  onDismiss,
}: ResultsDonationInvitationProps) {
  if (!DONATIONS_ENABLED) return null;

  return (
    <section aria-label="Support this ministry" className="space-y-3 pt-2">
      <div className="flex items-start justify-between gap-3">
        <h2 className="min-w-0 flex-1 text-xl font-medium text-neutral-900">
          Help Sustain This Ministry
        </h2>
        <button
          type="button"
          onClick={onDismiss}
          className="bta-button shrink-0"
          aria-label="Dismiss donation prompt"
        >
          Dismiss
        </button>
      </div>
      <p className="text-base text-neutral-800">
        Your support helps keep Bible Therapy Assistant™ accessible to others,
        providing opportunities to explore Scripture, deepen understanding, and
        discover why God&apos;s Word matters in everyday life.
      </p>
      <Link
        href="/donation"
        className="bta-button shrink-0"
      >
        Donate
      </Link>
    </section>
  );
}
