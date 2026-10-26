'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { runReflection } from './lib/btaApi';
import { getQueryCount } from "./lib/btaApi";
import DonationPrompt from "./components/donation/DonationPrompt";
import AudiencePrompt from "./components/audience/AudiencePrompt";
import { useQuestionSpeech } from './lib/useQuestionSpeech';
import MicrophoneSetup from './components/MicrophoneSetup';

type DecisionResponse = {
  decision: 'PROCEED' | 'REDIRECT' | 'STOP';
  message?: string;
  execution_payload?: any;
};

export default function WhyPage() {
  const [queryCount, setQueryCount] = useState(0);
  useEffect(() => {
  if (typeof window !== "undefined") {
    const count = Number(localStorage.getItem("bta_query_count") || "0");
    setQueryCount(count);
  }
}, []);
  const router = useRouter();
  const [question, setQuestion] = useState('');
  const speech = useQuestionSpeech((text) => {
    setQuestion((previous) => previous + (previous && !/\s$/.test(previous) ? ' ' : '') + text);
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [isFinalStage, setIsFinalStage] = useState(false);
  const [dictateTooltipDismissed, setDictateTooltipDismissed] = useState(false);

  useEffect(() => {
    const dismissTooltip = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setDictateTooltipDismissed(true);
    };
    document.addEventListener('keydown', dismissTooltip);
    return () => document.removeEventListener('keydown', dismissTooltip);
  }, []);

  // 🔒 Canonical source of truth for submitted input
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();

    const trimmed = inputRef.current?.value.trim() ?? '';
    if (!trimmed) return;
    speech.cancel();

    setLoading(true);
    setLoadingMessage(
      'Searching Scripture and preparing your response...'
    );

    setTimeout(() => {
      setLoadingMessage(
        'Looking at surrounding passages and deeper context...'
      );
    }, 5000);

    setTimeout(() => {
      setLoadingMessage(
        'Building reflection and preparing insight from the passages found'
      );

      setIsFinalStage(true);
    }, 12500);

    setMessage(null);

    try {
      // --------------------------------------------------
      // HEART: /api/query
      // --------------------------------------------------
      const decisionResult: DecisionResponse = await runReflection({
        question: trimmed,
        want_commentary: true,
      });

      if (
        decisionResult.decision === 'REDIRECT' ||
        decisionResult.decision === 'STOP'
      ) {
        setMessage(
          decisionResult.message ??
            'That question may need a little more clarity. Could you share more about what you’re reflecting on?'
        );
        setLoading(false);
        return;
      }

      if (!decisionResult.execution_payload) {
        setMessage(
          'Something unexpected occurred while preparing your reflection. Please try again.'
        );
        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // HANDS: /api/results
      // --------------------------------------------------
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/results`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            execution_payload: decisionResult.execution_payload,
          }),
        }
      );

      const responseBody = await res.json();

      // --------------------------------------------------
      // Structured 422 clarification (WHY gate)
      // --------------------------------------------------
      if (res.status === 422 && typeof responseBody?.detail === 'string') {
        setMessage(responseBody.detail);
        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // True system-level failure (not structured application response)
      // --------------------------------------------------
      if (!res.ok) {
        setMessage(
          'We ran into an issue while processing your request. Please try again.'
        );
        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // Normal Success Path
      // --------------------------------------------------
      
      setLoadingMessage(
        'Preparing your response for display...'
      );

      setTimeout(() => {
        router.push(
          `/results?payload=${encodeURIComponent(
            JSON.stringify(responseBody)
          )}`
        );
      }, 250);

    } catch (err: any) {
      // Network-level failure only
      setMessage(
        'We ran into an issue while processing your request. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      className="space-y-6 sm:space-y-8"
      style={{ width: "100%" }}
    >
      <h2 className="text-2xl sm:text-3xl font-semibold text-center">
        Explore Scripture & Understanding
      </h2>

<form onSubmit={handleSubmit} className="space-y-4 w-full">
  
        <div className="relative">
        <input
          id="nql-question"
          ref={inputRef}
          type="text"
          value={question}
          onChange={(e) => {
            speech.cancel();
            setQuestion(e.target.value);
          }}
          aria-describedby="question-speech-status"
          placeholder="e.g., Genesis 1:1, hope in suffering, why faith matters"
          className="w-full rounded-md border border-neutral-400 pl-4 pr-32 py-3 text-base text-neutral-900 bg-white shadow-sm placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-neutral-300"
          disabled={loading}
        />
        <div className="absolute right-1 top-1/2 flex -translate-y-1/2 items-center">
        {question.length > 0 && (
        <button
          type="button"
          aria-label="Clear question"
          onClick={() => {
            speech.cancel();
            setQuestion('');
            inputRef.current?.focus();
          }}
          disabled={loading}
          className="flex h-11 w-11 items-center justify-center border-0 bg-transparent p-0 text-2xl text-neutral-500 hover:text-neutral-900 focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-neutral-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span aria-hidden="true">×</span>
        </button>
        )}
        <span aria-hidden="true" className="flex h-5 w-6 items-center justify-center gap-0.5">
          {speech.phase === 'listening' && (
            <span data-voice-waves className="flex h-5 items-center gap-0.5 text-red-700">
              <span className="h-2 w-1 rounded-full bg-current motion-safe:animate-[pulse_700ms_ease-in-out_infinite]" />
              <span className="h-5 w-1 rounded-full bg-current motion-safe:animate-[pulse_700ms_ease-in-out_infinite] [animation-delay:150ms]" />
              <span className="h-3 w-1 rounded-full bg-current motion-safe:animate-[pulse_700ms_ease-in-out_infinite] [animation-delay:300ms]" />
            </span>
          )}
        </span>
        <button
          type="button"
          aria-label="Dictate"
          aria-pressed={speech.phase === 'starting' || speech.phase === 'listening'}
          aria-describedby="question-speech-status"
          disabled={loading || speech.supported === null || speech.phase === 'stopping'}
          onClick={speech.toggle}
          onFocus={() => setDictateTooltipDismissed(false)}
          onMouseEnter={() => setDictateTooltipDismissed(false)}
          className={`group relative flex h-11 w-11 items-center justify-center border-0 bg-transparent p-0 focus-visible:outline-2 focus-visible:outline-neutral-500 disabled:opacity-50 ${speech.phase === 'listening' ? 'text-red-700' : 'text-neutral-500 hover:text-neutral-900'}`}
        >
          <span aria-hidden="true" className={`absolute bottom-full left-1/2 z-10 -translate-x-1/2 pb-1 ${dictateTooltipDismissed ? 'invisible' : 'invisible group-hover:visible group-focus:visible'}`}>
            <span className="block whitespace-nowrap rounded bg-neutral-900 px-2 py-1 text-[14px] font-medium leading-5 text-white">Dictate</span>
          </span>
          <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <rect x="9" y="2" width="6" height="12" rx="3" />
            <path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8" />
          </svg>
        </button>
        </div>
        </div>
        <div className="w-full text-center">
          <button
            type="submit"
            disabled={loading}
            className="bta-button"
          >
            {loading ? "Exploring Scripture..." : "Explore Scripture"}
          </button>
        </div>

        <div className={`relative text-sm text-neutral-600 ${speech.needsSetup ? 'pr-12' : ''}`}>
          {speech.needsSetup && (
            <button
              type="button"
              aria-label="Dismiss message."
              onClick={() => {
                speech.dismissError();
                inputRef.current?.focus();
              }}
              className="absolute right-0 top-0 flex h-11 w-11 items-center justify-center border-0 bg-transparent p-0 text-xl text-neutral-500 hover:text-neutral-900 focus-visible:outline-2 focus-visible:outline-neutral-500"
            >
              <span aria-hidden="true">×</span>
            </button>
          )}
          <div id="question-speech-status" role="status" aria-live="polite">
            {speech.needsSetup ? (
              <>
                <h3 className="font-medium">Microphone is unavailable</h3>
                <p>BTA cannot access your microphone right now. Select Microphone Setup for help, or type your question instead.</p>
              </>
            ) : speech.status}
          </div>
          {speech.needsSetup && (
            <div className="flex flex-wrap items-center gap-2">
              <MicrophoneSetup issue={speech.issue} />
              {speech.canRetry && (
                <button type="button" disabled={loading} onClick={speech.toggle} className="min-h-11 rounded px-2 underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-500 disabled:opacity-50">Try Again</button>
              )}
            </div>
          )}
        </div>

        <div className="text-center py-2">
          <label htmlFor="nql-question" className="block text-sm text-neutral-700">
            What would you like to explore in Scripture?
          </label>

          <p className="text-sm text-neutral-500 mt-2">
            Examples:<br />
            John 3:16 • Psalm 23 • Romans 8:28–39<br />
            "What does God say about fear?"<br />
            "I feel anxious and need peace."
          </p>
        </div>

        <div role="status" aria-live="polite" aria-atomic="true" className={message ? "space-y-1" : "sr-only"}>
        {message && (
          <>
            <p className="text-sm text-neutral-600 italic">{message}</p>
            <p className="text-xs text-neutral-500">
              You can clarify your question by adding more detail to your initial
              question, then clicking{' '}
              <span className="font-medium">Reflect →</span> again.
            </p>
          </>
        )}
        </div>

        <div role="status" aria-live="polite" aria-atomic="true" className={loading && loadingMessage ? "rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2" : "sr-only"}>
        {loading && loadingMessage && (
            <p className="text-sm text-neutral-700 italic">
              {loadingMessage}
              {isFinalStage && (
                <span aria-hidden="true" className="inline-block animate-pulse">...</span>
              )}
            </p>
        )}
        </div>


      </form>

      {/*
=============================================================================
Platform introduction relocated to the dedicated About workspace.

Reason:
The Home page is intentionally focused on helping users begin exploring
Scripture. Platform mission, purpose, and differentiators are now presented
through the dedicated About workspace accessed from the primary navigation.

Retained temporarily during About workspace validation.

Future:
Remove this commented section after About workspace has been fully validated.
=============================================================================

<div className="space-y-5 text-neutral-700">

  <p>
    BTA allows Christians, missionaries, and spiritually searching individuals
    to explore Scripture in multiple ways — whether entering a Bible verse,
    exploring an entire chapter, asking questions naturally, searching by topic
    or emotion, or seeking deeper understanding behind God’s Word.
  </p>

  <p className="text-neutral-700">
    In contrast to traditional Bible search apps or concordances, BTA helps
    people move beyond isolated verse searching into thoughtful understanding,
    connected meaning, reflection, and the deeper "why" behind Scripture while
    keeping God’s Word central to the experience.
  </p>

</div>

*/}
   
    <div className="pt-6">
      {/* 
===========================================================================
AudiencePrompt removed from Home page.

Reason:
The Stay Connected capability has been migrated to the dedicated
/stay-connected page and is now accessed through the persistent
platform navigation.

Retained temporarily for rollback during validation.

Remove permanently after Donate migration and navigation validation.
===========================================================================
<div className="pt-6">
  <AudiencePrompt />
</div>
*/}

    </div>

    </section>
  );
}


