'use client';

import { useEffect, useState, useRef } from 'react';
import { runReflection } from './lib/btaApi';
import { getQueryCount } from "./lib/btaApi";
import QueryResultView, { QueryResponse } from './components/QueryResultView';
import DonationPrompt from './components/donation/DonationPrompt';

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
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [isFinalStage, setIsFinalStage] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [donationDismissed, setDonationDismissed] = useState(false);

  // 🔒 Canonical source of truth for submitted input
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [result, message, loading, loadingMessage]);

  const resizeInput = () => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleNewQuestion = () => {
    setResult(null);
    setMessage(null);
    setQuestion('');
    setDonationDismissed(false);
    if (inputRef.current) {
      inputRef.current.value = '';
      resizeInput();
      inputRef.current.focus();
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();

    const trimmed = inputRef.current?.value.trim() ?? '';
    if (!trimmed) return;

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
      setResult(responseBody);
      setQuestion('');
      if (inputRef.current) {
        inputRef.current.value = '';
        resizeInput();
      }
    } catch (err: any) {
      // Network-level failure only
      setMessage(
        'We ran into an issue while processing your request. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const isLanding = !result && !message && !loading;

  // Rendered via a plain function call (not `<Composer />`) so it stays part of
  // the same render tree position instead of being treated as a fresh component
  // type on every keystroke — a `<Composer />` defined in-body would remount the
  // textarea (and drop focus) each time `question` state changes.
  const renderComposer = () => (
    <form onSubmit={handleSubmit} className="space-y-3">
      <label htmlFor="scripture-question" className="sr-only">
        What would you like to explore in Scripture?
      </label>

      <div className="flex items-end gap-2 rounded-3xl border border-neutral-300 bg-neutral-100 pl-4 pr-1.5 py-1.5 shadow-sm focus-within:ring-2 focus-within:ring-blue-500/60 focus-within:border-blue-500/60 dark:border-neutral-700 dark:bg-neutral-900">
        <textarea
          id="scripture-question"
          ref={inputRef}
          rows={2}
          value={question}
          onChange={(e) => {
            setQuestion(e.target.value);
            resizeInput();
          }}
          onKeyDown={handleKeyDown}
          placeholder="e.g., Genesis 1:1, hope in suffering, why faith matters"
          className="flex-1 resize-none bg-transparent py-1.5 text-base text-neutral-900 placeholder:text-neutral-500 focus:outline-none min-h-[60px] transition-[height] duration-150 ease-out dark:text-neutral-100"
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
          aria-label="Explore Scripture"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white disabled:bg-neutral-300 disabled:text-neutral-500 transition-all duration-150 hover:enabled:bg-blue-500 hover:enabled:scale-105 active:enabled:scale-95 dark:disabled:bg-neutral-700"
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
            <path d="M12 19V5" />
            <path d="M5 12l7-7 7 7" />
          </svg>
        </button>
      </div>

      <p className="px-1 text-xs text-neutral-500">
        Press Enter to send, Shift+Enter for a new line.
      </p>
    </form>
  );

  return (
    <section className="flex flex-1 min-h-0 flex-col">
      {isLanding ? (
        <div className="flex flex-1 min-h-0 flex-col items-center justify-center gap-8 text-center">
          <img
            src="/logo-lg.svg"
            alt="Bible Therapy Assistant"
            width={196}
            height={196}
            className="dark:invert"
          />

          <div className="max-w-md space-y-3 text-neutral-700 dark:text-neutral-300">
            <h4 className="text-xl font-semibold text-neutral-900 dark:text-neutral-50">
              Explore scrpture and understanding
            </h4>

              <p className="text-sm text-neutral-500">
                Enter a verse, a chapter, or ask a question in your own words.
              </p>
          </div>

          <div className="w-full max-w-2xl">{renderComposer()}</div>
        </div>
      ) : (
        <>
          {/* Full-width compact header — breaks out of main's max-w-4xl column so it spans the viewport */}
          <div className="animate-fade-slide-in relative left-1/2 right-1/2 -mx-[50vw] -mt-8 mb-4 w-screen shrink-0 border-b border-neutral-200 bg-neutral-100 px-4 py-3 sm:px-6 dark:border-neutral-800 dark:bg-neutral-800">
            <div className="flex flex-wrap items-center justify-between gap-y-2 gap-x-4">
              <div className="flex min-w-0 items-center gap-3 sm:gap-4">
                <button
                  type="button"
                  onClick={handleNewQuestion}
                  aria-label="Go to home"
                  className="h-10 w-10 shrink-0 cursor-pointer sm:h-16 sm:w-16"
                >
                  <img
                    src="/logo-sm.svg"
                    alt="Bible Therapy Assistant"
                    width={64}
                    height={64}
                    className="h-full w-full dark:invert"
                  />
                </button>

                <div className="min-w-0">
                  <div className="truncate text-base font-semibold text-neutral-900 sm:text-lg dark:text-neutral-50">
                    Bible Therapy Assistant
                  </div>
                  <div className="text-xs font-medium uppercase tracking-widest text-neutral-500 dark:text-white">
                    Go Deeper
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm sm:gap-4">
                <button
                  type="button"
                  onClick={handleNewQuestion}
                  className="flex items-center gap-1.5 rounded-full border border-blue-500/50 bg-blue-500/10 px-3 py-1.5 text-sm font-medium text-blue-600 transition-colors hover:bg-blue-500/20 dark:text-blue-400"
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
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                  New question
                </button>

                <span className="hidden cursor-pointer text-neutral-600 hover:text-neutral-900 sm:inline dark:text-neutral-400 dark:hover:text-neutral-200">
                  About
                </span>
                <span className="hidden cursor-pointer text-neutral-600 hover:text-neutral-900 sm:inline dark:text-neutral-400 dark:hover:text-neutral-200">
                  Contact
                </span>
                <span className="hidden cursor-pointer text-neutral-600 hover:text-neutral-900 sm:inline dark:text-neutral-400 dark:hover:text-neutral-200">
                  Donate
                </span>
                <span
                  aria-label="Profile"
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-neutral-300 bg-neutral-200 text-neutral-600 dark:border-neutral-600 dark:bg-neutral-700 dark:text-neutral-300"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-5 w-5"
                  >
                    <circle cx="12" cy="8" r="4" />
                    <path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
                  </svg>
                </span>
              </div>
            </div>
          </div>

          {/* Response area — takes up the rest of the page and scrolls independently */}
          <div className="min-h-0 flex-1 space-y-6 overflow-y-auto pr-2">
            {result && (
              <div className="animate-fade-slide-in space-y-6">
                <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Scripture & Reflection</h2>
                <QueryResultView data={result} />
              </div>
            )}

            {message && (
              <div className="animate-fade-slide-in space-y-1 rounded-2xl border border-neutral-200 bg-neutral-50 px-4 py-3 shadow-sm dark:border-neutral-800 dark:bg-neutral-900">
                <p className="text-sm text-neutral-700 italic dark:text-neutral-300">{message}</p>
                <p className="text-xs text-neutral-500">
                  You can clarify your question by adding more detail, then
                  sending it again.
                </p>
              </div>
            )}

            {loading && loadingMessage && (
              <div className="animate-fade-slide-in flex items-center gap-2 rounded-2xl border border-neutral-200 bg-neutral-50 px-4 py-3 shadow-sm dark:border-neutral-800 dark:bg-neutral-900">
                <p className="text-sm text-neutral-700 italic dark:text-neutral-300">{loadingMessage}</p>
                {isFinalStage && (
                  <span className="flex gap-1">
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse-dot"
                      style={{ animationDelay: '0ms' }}
                    />
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse-dot"
                      style={{ animationDelay: '160ms' }}
                    />
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse-dot"
                      style={{ animationDelay: '320ms' }}
                    />
                  </span>
                )}
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Composer — pinned to the bottom of the page */}
          <div className="sticky bottom-0 shrink-0 pt-4">{renderComposer()}</div>

          {result && !donationDismissed && (
            <div className="shrink-0 pt-3">
              <DonationPrompt onDismiss={() => setDonationDismissed(true)} />
            </div>
          )}
        </>
      )}
    </section>
  );
}

