'use client';

import { useEffect, useState, useRef } from 'react';
import { resultEvents, runReflection, scriptureOptions } from './lib/btaApi';
import type { Execution, ScriptureOption } from './lib/btaApi';
import IncrementalReader, { sectionNames } from './components/IncrementalReader';
import type { ActiveResult } from './components/IncrementalReader';
import { getQueryCount } from "./lib/btaApi";
import DonationPrompt from "./components/donation/DonationPrompt";
import AudiencePrompt from "./components/audience/AudiencePrompt";
import { prepareScriptureQuestion } from './lib/prepareScriptureQuestion';
import { useQuestionSpeech } from './lib/useQuestionSpeech';
import MicrophoneSetup from './components/MicrophoneSetup';

type DecisionResponse = {
  decision: 'PROCEED' | 'REDIRECT' | 'STOP';
  message?: string;
  execution_payload?: Execution;
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
  const speech = useQuestionSpeech((text) => {
    setQuestion((previous) => previous + (previous && !/\s$/.test(previous) ? ' ' : '') + text);
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [dictateTooltipDismissed, setDictateTooltipDismissed] = useState(false);

  useEffect(() => {
    const dismissTooltip = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setDictateTooltipDismissed(true);
    };
    document.addEventListener('keydown', dismissTooltip);
    return () => document.removeEventListener('keydown', dismissTooltip);
  }, []);

  const inputRef = useRef<HTMLTextAreaElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const selectionButton = useRef<HTMLButtonElement>(null);
  const [catalog, setCatalog] = useState<{ default: string; options: ScriptureOption[] }>();
  const options = catalog?.options ?? [];
  const [selection, setSelection] = useState<string>();
  const [draft, setDraft] = useState<string>();
  const visibleSelection = draft ?? selection ?? catalog?.default;
  const [result, setResult] = useState<ActiveResult>();
  const [original, setOriginal] = useState<{ result: ActiveResult; execution: Execution; reference: number }>();
  const [restoreFocus, setRestoreFocus] = useState<number>();
  const execution = useRef<Execution | undefined>(undefined);
  const active = useRef<AbortController | undefined>(undefined);
  const nextId = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    scriptureOptions(controller.signal).then(data => {
      setCatalog(data);
    }).catch(() => {});
    const abandon = () => {
      active.current?.abort();
      active.current = undefined;
    };
    window.addEventListener('pagehide', abandon);
    return () => {
      controller.abort();
      abandon();
      window.removeEventListener('pagehide', abandon);
    };
  }, []);

  useEffect(() => {
    const field = inputRef.current;
    if (field) {
      field.style.height = 'auto';
      field.style.height = field.scrollHeight + 2 + 'px';
    }
  }, [question, result]);

  const abandon = () => {
    active.current?.abort();
    active.current = undefined;
    setLoading(false);
  };

  const edit = () => {
    abandon();
    setOriginal(undefined);
    setResult(undefined);
    setRestoreFocus(undefined);
    requestAnimationFrame(() => inputRef.current?.focus());
  };

  const start = async (text: string, parent?: Execution, retry?: Execution) => {
    if (active.current || !text.trim()) return;
    const controller = new AbortController();
    active.current = controller;
    const { signal } = controller;
    const id = ++nextId.current;
    setLoading(true);
    setMessage(null);
    setRestoreFocus(undefined);
    if (!retry) execution.current = undefined;
    speech.cancel();
    const current = () => active.current === controller && !signal.aborted;
    let view: ActiveResult = {
      id, question: text, status: 'pending', data: {}, ready: [], failed: [],
      announcement: 'Preparing your response…',
    };
    const publish = (changes: Partial<ActiveResult>) => {
      view = { ...view, ...changes };
      if (current()) setResult(view);
    };
    try {
      let accepted = retry;
      if (!accepted) {
        const prepared = prepareScriptureQuestion(text);
        if (prepared.needsChapterAndVerse) {
          publish({ status: 'failed', failed: ['scripture'], announcement:
            'Enter the chapter and verse with a colon, for example John 3:16.' });
          return;
        }
        const decision: DecisionResponse = await runReflection({
          question: prepared.lookup, scripture_option: parent ? undefined : selection,
          parent_execution: parent, want_commentary: true, signal,
        });
        if (!current()) return;
        if (decision.decision !== 'PROCEED' || !decision.execution_payload) {
          const notice = decision.message ?? 'Could you share a little more about what you’re seeking?';
          if (parent) publish({ status: 'failed', announcement: notice });
          else setMessage(notice);
          return;
        }
        accepted = decision.execution_payload;
      }
      execution.current = accepted;
      publish({});
      for await (const event of resultEvents(accepted, signal)) {
        if (!current()) return;
        if (event.event === 'section') {
          if (!sectionNames.includes(event.section) || view.ready.includes(event.section) || view.failed.includes(event.section)) continue;
          const label = event.section.charAt(0).toUpperCase() + event.section.slice(1);
          publish({
            data: { ...view.data, ...event.data },
            ready: event.success ? [...view.ready, event.section] : view.ready,
            failed: event.success ? view.failed : [...view.failed, event.section],
            announcement: event.success ? label + ' is ready.' : label + ' couldn’t be fully prepared.',
          });
        } else if (event.event === 'failure') {
          const notice = event.code === 'missing_passage'
            ? 'This passage was not found in the selected Scripture edition. Edit your question to try another reference.'
            : event.code === 'source_unavailable' || event.code === 'edition_unverified'
              ? accepted.resolved_scripture.source_label + ' is temporarily unavailable. Try again.'
              : 'The response could not be completed. Sections already available are still readable.';
          publish({ status: view.ready.length ? 'partial' : 'failed', code: event.code,
            failed: [...view.failed, event.section], announcement: notice });
          break;
        } else if (event.event === 'complete') {
          const complete = event.success && sectionNames.every(section => view.ready.includes(section));
          publish({ status: complete ? 'complete' : 'partial', escalation: event.escalation,
            announcement: event.escalation ? 'Support information is available.'
              : complete ? 'Response complete. Scripture references are ready to explore.'
              : 'The response is incomplete. Sections already available are still readable.' });
          break;
        }
      }
      if (view.status === 'pending') publish({
        status: 'interrupted', announcement: 'Response interrupted. Sections already available are still readable.',
      });
    } catch {
      if (current()) {
        const notice = 'Response interrupted. Sections already available are still readable.';
        if (execution.current || parent) publish({ status: 'interrupted', announcement: notice });
        else setMessage('We ran into an issue while processing your request. Please try again.');
      }
    } finally {
      if (current()) {
        active.current = undefined;
        setLoading(false);
      }
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    void start(question);
  };

  if (result) return <IncrementalReader result={result} restoreFocus={restoreFocus} onEdit={edit}
    onStop={() => {
      abandon();
      setResult({ ...result, status: 'interrupted',
        announcement: 'Response interrupted. Sections already available are still readable.' });
    }}
    onRetry={() => { if (execution.current) void start(result.question, undefined, execution.current); }}
    onExplore={(reference, index) => {
      if (!execution.current || active.current) return;
      const parent = execution.current;
      if (!original) setOriginal({ result, execution: parent, reference: index });
      void start(reference, parent);
    }}
    onReturn={original ? () => {
      abandon();
      execution.current = original.execution;
      setRestoreFocus(original.reference);
      setResult(original.result);
      setOriginal(undefined);
    } : undefined}
  />;

  const versionActions = (
    <>
      <button type="button" className="bta-button" onClick={() => dialog.current?.close()}>Cancel</button>
      <button type="button" className="bta-button" disabled={!visibleSelection}
        onClick={() => { setSelection(visibleSelection); dialog.current?.close(); }}>Apply</button>
    </>
  );

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
        <textarea
          id="nql-question"
          ref={inputRef}
          rows={1}
          dir="auto"
          aria-label="Your question"
          value={question}
          onChange={(e) => {
            speech.cancel();
            setQuestion(e.target.value);
          }}
          aria-describedby="question-speech-status"
          placeholder="e.g., Genesis 1:1, hope in suffering, why faith matters"
          className="block w-full resize-none rounded-md border border-neutral-400 pl-4 pr-32 py-3 text-base text-neutral-900 bg-white shadow-sm placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-neutral-300"
          disabled={loading}
        />
        <div className="absolute right-1 top-1 flex items-center">
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
        <div className="grid grid-cols-2 items-center gap-2">
          <button type="submit" disabled={loading || !question.trim()} className="bta-button justify-self-end">
            {loading ? "Exploring Scripture…" : "Explore Scripture"}
          </button>
          <button type="button" aria-haspopup="dialog" ref={selectionButton}
            className="bta-button justify-self-end"
            onClick={() => { setDraft(selection); dialog.current?.showModal(); }}>
            Versions
          </button>
        </div>
        <dialog ref={dialog} aria-labelledby="translation-title"
          onClose={() => selectionButton.current?.focus()}
          className="m-auto w-[min(92vw,32rem)] rounded-lg bg-white p-6 text-neutral-900 shadow-xl backdrop:bg-black/40">
          <h3 id="translation-title" className="mb-4 text-xl font-semibold">Versions</h3>
          <div className="mb-4 flex flex-wrap gap-2">{versionActions}</div>
          {options.length ? options.map(option => (
            <label key={option.option_id} className="mb-3 flex items-center gap-2">
              <input type="radio" name="scripture-option" checked={visibleSelection === option.option_id}
                onChange={() => setDraft(option.option_id)} />
              {option.edition_label}{option.option_id === catalog?.default ? " (default)" : ""}
            </label>
          )) : <p>Translation options are unavailable. The default is local KJV.</p>}
          <div className="mt-4 flex flex-wrap gap-2">{versionActions}</div>
        </dialog>

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
                <h3 className="font-medium">{speech.issue === 'network' ? 'Voice input could not connect' : 'Microphone is unavailable'}</h3>
                <p>{speech.issue === 'network'
                  ? speech.status
                  : 'BTA cannot access your microphone right now. Select Microphone Setup for help, or type your question instead.'}</p>
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
              <span className="font-medium">Explore Scripture</span> again.
            </p>
          </>
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


