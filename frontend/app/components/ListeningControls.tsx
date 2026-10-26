'use client';

import type { useResultsReader } from '../lib/useResultsReader';
import type { ReadingState } from '../lib/resultsReader';
import { useEffect, useId, useRef, useState, type ReactNode, type Ref } from 'react';

type AudioAction = 'Listen' | 'Restart' | 'Pause' | 'Resume' | 'Stop';
type Props = {
  reader: ReturnType<typeof useResultsReader>;
  selection: string;
  label: string;
  text: string;
};

export function listeningStatus(phase: ReadingState['phase'], selection: string | null, label: string) {
  if (!selection || phase === 'idle') return '';
  if (phase === 'paused') return 'Paused';
  if (phase === 'starting') return 'Starting audio…';
  return `Reading ${selection === 'entire' ? 'entire response' : label.replace(/ \(KJV\)$/, '')}…`;
}

function AudioIcon({ action }: { action: AudioAction }) {
  return (
    <svg data-audio-icon={action.toLowerCase()} aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" className="shrink-0">
      {action === 'Restart' ? <g fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 10a8 8 0 1 1 1 8M4 4v6h6" /></g> : action === 'Listen' ? <g fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M11 5 6 9H3v6h3l5 4V5Z" />
        <path d="M15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14" />
      </g> : action === 'Pause' ? <g fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1" /><rect x="14" y="4" width="4" height="16" rx="1" /></g>
        : action === 'Resume' ? <path fill="currentColor" d="m7 4 14 8-14 8V4Z" />
          : <rect fill="currentColor" x="5" y="5" width="14" height="14" rx="1" />}
    </svg>
  );
}

function AudioButton({ action, label, entire, onClick, children, ref }: {
  action: AudioAction;
  label: string;
  entire: boolean;
  onClick: () => void;
  children?: ReactNode;
  ref?: Ref<HTMLButtonElement>;
}) {
  const tooltipId = useId();
  const [dismissed, setDismissed] = useState(false);
  useEffect(() => {
    const dismissTooltip = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setDismissed(true);
    };
    document.addEventListener('keydown', dismissTooltip);
    return () => document.removeEventListener('keydown', dismissTooltip);
  }, []);
  return (
    <button ref={ref} type="button" aria-label={label} aria-describedby={tooltipId}
      onClick={onClick} onFocus={() => setDismissed(false)} onMouseEnter={() => setDismissed(false)}
      onKeyDown={event => { if (event.key === 'Escape') setDismissed(true); }}
      className={`group relative inline-flex min-h-11 min-w-11 items-center justify-center gap-2 rounded border-0 bg-transparent text-sm ${action === 'Stop' ? 'text-red-700' : action === 'Restart' ? 'text-neutral-600' : 'text-blue-700'} hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 ${entire ? 'px-3 py-2' : 'p-2'}`}>
      <AudioIcon action={action} />
      {children}
      <span className={`absolute bottom-full z-10 w-max max-w-48 pb-2 ${entire ? 'left-0 text-left' : 'right-0 text-right'} ${dismissed ? 'invisible' : 'invisible group-hover:visible group-focus:visible'}`}>
        <span id={tooltipId} role="tooltip" className="block rounded bg-neutral-900 px-2 py-1 text-xs font-normal text-white">{label}</span>
      </span>
    </button>
  );
}

export default function ListeningControls({ reader, selection, label, text }: Props) {
  const primary = useRef<HTMLButtonElement>(null);
  if (!text.trim() || reader.state.available !== true) return null;
  const active = reader.state.selection === selection;
  const entire = selection === 'entire';
  const action = active ? (reader.state.phase === 'paused' ? 'Resume' : 'Pause') : 'Listen';
  const actionLabel = action === 'Listen' ? `Listen to ${label}` : `${action} ${label}`;
  return (
    <div role="group" aria-label={`Listening controls: ${label}`} className={`flex flex-col gap-1 ${entire ? 'items-start' : `${active ? 'w-[8.75rem]' : 'w-11'} shrink-0 items-end`}`}>
      <div className="flex flex-wrap items-center gap-1">
        {active && <AudioButton key="restart" action="Restart" label={`Restart ${label}`} entire={entire} onClick={reader.restart} />}
        <AudioButton key="primary" ref={primary} action={action} label={actionLabel} entire={entire}
          onClick={active ? (action === 'Resume' ? reader.resume : reader.pause) : () => reader.listen(selection, text)}>
          {entire && action === 'Listen' && 'Listen to Entire Response'}
        </AudioButton>
        {active && <AudioButton key="stop" action="Stop" label={`Stop ${label}`} entire={entire} onClick={() => {
          reader.stop();
          primary.current?.focus({ preventScroll: true });
        }} />}
      </div>
      {active && <span className={`text-xs text-neutral-600 ${entire ? 'text-left' : 'text-right'}`}>{listeningStatus(reader.state.phase, selection, label)}</span>}
    </div>
  );
}
