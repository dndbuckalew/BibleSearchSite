"use client";

import { useEffect, useId, useRef, useState, type MouseEvent } from "react";
import { createDonationIdempotencyKey } from "./idempotency";

const controlClass = "bta-button disabled:cursor-wait";

export default function DonationPrompt({ children }: { children?: React.ReactNode }) {
  const dialog = useRef<HTMLDialogElement | null>(null);
  const trigger = useRef<HTMLButtonElement | null>(null);
  const pendingTab = useRef<Window | null>(null);
  const requestController = useRef<AbortController | null>(null);
  const checkoutUrl = useRef<string | null>(null);
  const titleId = useId();
  const descriptionId = useId();
  const busy = useRef(false);
  const attempt = useRef<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [needsRecovery, setNeedsRecovery] = useState(false);

  useEffect(() => () => {
    requestController.current?.abort();
    pendingTab.current?.close();
  }, []);

  function showConfirmation(event: MouseEvent<HTMLButtonElement>) {
    if (busy.current) return;
    trigger.current = event.currentTarget;
    dialog.current?.showModal();
  }

  function closeConfirmation() {
    dialog.current?.close();
  }

  async function continueToStripe() {
    if (busy.current) return;
    busy.current = true;
    setLoading(true);
    setError(null);
    setNeedsRecovery(false);
    closeConfirmation();
    let tab: Window | null = null;
    try {
      if (!checkoutUrl.current) attempt.current ??= createDonationIdempotencyKey();
      const base = process.env.NEXT_PUBLIC_API_BASE_URL;
      if (!base) throw new Error("Donation service unavailable");
      // Open synchronously in the visitor's gesture. Passing noopener to open
      // can discard the navigation handle, so sever opener before any await.
      tab = window.open("about:blank", "_blank");
      if (!tab) {
        setError("Your browser blocked the checkout tab. Allow popups for BTA, then select Open Stripe Checkout.");
        setNeedsRecovery(true);
        return;
      }
      tab.opener = null;
      if (tab.opener !== null) throw new Error("Unable to isolate checkout tab");
      pendingTab.current = tab;
      tab.document.title = "Opening Stripe Checkout";

      if (!checkoutUrl.current) {
        const controller = new AbortController();
        requestController.current = controller;
        const response = await fetch(`${base.replace(/\/$/, "")}/donation/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "Idempotency-Key": attempt.current! },
          body: JSON.stringify({ source: "donation_page" }),
          signal: AbortSignal.any([controller.signal, AbortSignal.timeout(20000)]),
        });
        if (!response.ok) throw new Error("Donation service unavailable");
        const data = await response.json();
        const url = new URL(data.qr_payload.donation_url);
        if (url.protocol !== "https:" || url.hostname !== "checkout.stripe.com" || url.username || url.password || url.port) {
          throw new Error("Invalid checkout destination");
        }
        checkoutUrl.current = url.href;
      }
      if (tab.closed) {
        setError("The checkout tab was closed. Select Open Stripe Checkout to continue.");
        setNeedsRecovery(true);
        return;
      }
      tab.location.replace(checkoutUrl.current);
      pendingTab.current = null;
    } catch {
      tab?.close();
      setNeedsRecovery(Boolean(checkoutUrl.current));
      setError("Unable to start donation right now. Please try again.");
    } finally {
      pendingTab.current = null;
      requestController.current = null;
      busy.current = false;
      setLoading(false);
    }
  }

  const button = <button type="button" onClick={showConfirmation} disabled={loading} aria-busy={loading} className={controlClass}>Donate Securely</button>;
  return (
    <div className="space-y-8">
      {button}
      {error && <p role="alert" className="text-base text-red-800">{error}</p>}
      {needsRecovery && <button type="button" onClick={continueToStripe} disabled={loading} className={controlClass}>Open Stripe Checkout</button>}
      {children}
      <dialog
        ref={dialog}
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
        style={{ margin: "auto" }}
        onCancel={(event) => { event.preventDefault(); closeConfirmation(); }}
        onClose={() => trigger.current?.focus({ preventScroll: true })}
        className="m-auto max-h-[calc(100dvh_-_2rem)] w-[calc(100%_-_2rem)] max-w-lg overflow-y-auto rounded-lg border border-neutral-300 bg-white p-6 text-neutral-800 shadow-xl backdrop:bg-black/40"
      >
        <h2 id={titleId} className="mb-4 text-2xl font-semibold">Secure Donation Checkout</h2>
        <div id={descriptionId} className="space-y-4 text-base leading-relaxed">
          <p>You are about to leave Bible Therapy Assistant™ and continue to Stripe&apos;s secure checkout.</p>
          <p>BTA does not collect or store your credit card information. Your payment details are entered and processed directly through Stripe.</p>
          <p>By selecting Continue to Stripe, you acknowledge this information.</p>
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <button type="button" onClick={continueToStripe} disabled={loading} className={controlClass}>Continue to Stripe</button>
          <button type="button" onClick={closeConfirmation} className={controlClass}>Cancel</button>
        </div>
      </dialog>
      {button}
    </div>
  );
}
