'use client';

import { useId } from 'react';
import type { useResultsReader } from '../lib/useResultsReader';

export default function ResultsVoiceChoice({ reader }: { reader: ReturnType<typeof useResultsReader> }) {
  const id = useId();
  if (reader.state.available !== true || !reader.state.voices.length) return null;
  const englishName = (language: string) => language.toLowerCase() === 'en-us' ? 'English (US)' : language.toLowerCase() === 'en-gb' ? 'English (UK)' : `English (${language})`;
  const voices = reader.state.voices;
  if (voices.length === 1) return <p className="py-2 text-sm text-neutral-600">Voice: {voices[0].name}</p>;
  return (
    <div className="w-full min-w-0 space-y-1 sm:w-auto sm:max-w-xs">
      <label htmlFor={id} className="block text-sm text-neutral-700">Listening voice</label>
      <select id={id} value={reader.state.voiceId ?? ''} onChange={event => reader.chooseVoice(event.target.value)}
        disabled={reader.state.selection !== null} aria-describedby={reader.state.selection ? `${id}-help` : undefined}
        className="min-h-11 w-full rounded border border-neutral-300 bg-white px-2 text-sm text-neutral-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 disabled:bg-neutral-50 disabled:text-neutral-600">
        {voices.map(voice => <option key={voice.id} value={voice.id}>{voice.name} — {englishName(voice.language)}</option>)}
      </select>
      {reader.state.selection && <p id={`${id}-help`} className="text-xs text-neutral-600">Stop listening to change the voice.</p>}
    </div>
  );
}
