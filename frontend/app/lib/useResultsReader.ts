'use client';

import { useEffect, useState, useSyncExternalStore } from 'react';
import { initialReadingState, ResultsReader } from './resultsReader';

export function useResultsReader(responseKey: string | null) {
  const [reader] = useState(() => new ResultsReader());
  const state = useSyncExternalStore(reader.subscribe, reader.getSnapshot, () => initialReadingState);

  useEffect(() => {
    reader.connect(
      window.speechSynthesis ?? null,
      typeof window.SpeechSynthesisUtterance === 'function' ? text => new SpeechSynthesisUtterance(text) : null,
      document.documentElement.lang || navigator.language || 'en',
    );
    const synthesis = window.speechSynthesis;
    const refreshVoices = () => {
      try { reader.setVoices(synthesis?.getVoices?.() ?? []); }
      catch { reader.setVoices([]); }
    };
    synthesis?.addEventListener?.('voiceschanged', refreshVoices);
    refreshVoices();
    // pagehide also covers a full navigation and the back/forward cache.
    window.addEventListener('pagehide', reader.stop);
    window.addEventListener('beforeunload', reader.stop);
    const stopWhenHidden = () => {
      if (document.visibilityState === 'hidden') reader.stop();
    };
    document.addEventListener('visibilitychange', stopWhenHidden);
    return () => {
      synthesis?.removeEventListener?.('voiceschanged', refreshVoices);
      window.removeEventListener('pagehide', reader.stop);
      window.removeEventListener('beforeunload', reader.stop);
      document.removeEventListener('visibilitychange', stopWhenHidden);
      reader.stop();
    };
  }, [reader]);

  // A different response must never inherit playback from the previous response.
  useEffect(() => () => reader.stop(), [reader, responseKey]);

  return { state, chooseVoice: reader.chooseVoice, listen: reader.listen, restart: reader.restart, pause: reader.pause, resume: reader.resume, stop: reader.stop };
}
