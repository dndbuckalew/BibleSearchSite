"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

type Confirmation = {
  transaction_id: string;
  status: string;
  amount_total: number | null;
  currency: string | null;
  receipt_url: string | null;
};

export default function DonationSuccessPage() {
  const sessionToken = useRef<string | null>(null);
  const [confirmation, setConfirmation] = useState<Confirmation | null>(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const sessionId = new URLSearchParams(window.location.search).get("session_id");
    // Keep the bearer capability out of copied URLs and subsequent Referer headers.
    if (sessionId) {
      sessionToken.current = sessionId;
      window.history.replaceState(null, "", window.location.pathname);
    }
    try {
      if (sessionId) sessionStorage.setItem("bta-donation-confirmation", sessionId);
      sessionToken.current ??= sessionStorage.getItem("bta-donation-confirmation");
    } catch { /* Verification still works when browser storage is unavailable. */ }
    const token = sessionToken.current;
    const base = process.env.NEXT_PUBLIC_API_BASE_URL;
    let timer: ReturnType<typeof setTimeout> | undefined;
    async function verify(remaining: number) {
      try {
        if (!base || !token) throw new Error("Missing confirmation");
        const response = await fetch(`${base.replace(/\/$/, "")}/donation/verify`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: token }),
          signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15000)]),
          cache: "no-store",
          referrerPolicy: "no-referrer",
        });
        if (!response.ok) throw new Error("Confirmation unavailable");
        const data: Confirmation = await response.json();
        if (controller.signal.aborted) return;
        setConfirmation(data);
        if (["qr_ready", "pending", "processing"].includes(data.status) && remaining > 0) {
          timer = setTimeout(() => verify(remaining - 1), 2000);
        }
      } catch {
        if (!controller.signal.aborted) setError(true);
      }
    }
    void verify(4);
    return () => { controller.abort(); if (timer) clearTimeout(timer); };
  }, [attempt]);

  const paid = confirmation?.status === "completed";
  let receipt: string | null = null;
  try {
    if (paid && confirmation.receipt_url) {
      const url = new URL(confirmation.receipt_url);
      if (url.protocol === "https:" && ["pay.stripe.com", "receipt.stripe.com"].includes(url.hostname) && !url.username && !url.password && !url.port) receipt = url.href;
    }
  } catch { /* Never render an invalid receipt destination. */ }

  return (
    <section className="mx-auto max-w-2xl space-y-6" aria-live="polite">
      <h1 className="text-2xl font-semibold">{paid ? "Thank you for your support" : "Donation confirmation"}</h1>
      {error ? <p role="alert">We could not verify your payment right now. Please check again before attempting another donation.</p> :
        paid ? <p>Your donation has been confirmed. Thank you for helping sustain this ministry.</p> :
        confirmation?.status === "failed" ? <p>Your payment was not completed. Please check your payment details in Stripe.</p> :
        confirmation?.status === "expired" ? <p>This checkout session has expired.</p> :
        <p>Your payment has not yet been confirmed. You can check again shortly.</p>}
      {paid && confirmation.amount_total !== null && <p>{new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(confirmation.amount_total / 100)}</p>}
      {confirmation && <p className="break-all text-sm">BTA reference: {confirmation.transaction_id}</p>}
      {receipt && <a href={receipt} rel="noreferrer" referrerPolicy="no-referrer" className="inline-flex min-h-11 items-center rounded border px-4 py-2 underline focus-visible:outline-2 focus-visible:outline-offset-4">View Stripe receipt</a>}
      {!paid && <button type="button" onClick={() => { setError(false); setAttempt(value => value + 1); }} className="bta-button">Check payment status</button>}
      <div><Link href="/" className="bta-button">Return Home</Link></div>
    </section>
  );
}
