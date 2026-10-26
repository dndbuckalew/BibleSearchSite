'use client';

import { useEffect, useRef, useState } from 'react';

type SpeechResult = { isFinal: boolean; 0: { transcript: string } };
type Recognition = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: (() => void) | null;
  onend: (() => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onresult: ((event: { resultIndex: number; results: ArrayLike<SpeechResult> }) => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
};
type SpeechWindow = Window & {
  SpeechRecognition?: new () => Recognition;
  webkitSpeechRecognition?: new () => Recognition;
};

export function useQuestionSpeech(appendText: (text: string) => void) {
  const [supported, setSupported] = useState<boolean | null>(null);
  const [phase, setPhase] = useState<'idle' | 'starting' | 'listening' | 'stopping'>('idle');
  const [status, setStatus] = useState('');
  const [issue, setIssue] = useState<string | null>(null);
  const [errorDismissed, setErrorDismissed] = useState(false);
  const current = useRef<Recognition | null>(null);
  const stopRequested = useRef(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const append = useRef(appendText);
  append.current = appendText;

  function release() {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    const recognition = current.current;
    current.current = null;
    if (recognition) {
      recognition.onstart = recognition.onend = null;
      recognition.onerror = recognition.onresult = null;
      try { recognition.abort(); } catch { /* Already disconnected. */ }
    }
  }

  useEffect(() => {
    const browser = window as SpeechWindow;
    const available = Boolean(browser.SpeechRecognition || browser.webkitSpeechRecognition);
    setSupported(available && window.isSecureContext);
    if (!window.isSecureContext) {
      setIssue('insecure');
      setStatus('Voice input may be blocked on this insecure HTTP connection. Use BTA over HTTPS, or localhost on this device. You can still type your question.');
    } else if (!available) {
      setIssue('unsupported');
      setStatus('Voice input is unavailable in this browser. You can still type your question.');
    }
    return () => release();
  }, []);

  function cancel() {
    if (!current.current) return;
    release();
    setPhase('idle');
    setStatus('Voice input stopped. You can edit your question.');
  }

  function toggle() {
    if (current.current) {
      const recognition = current.current;
      stopRequested.current = true;
      if (timer.current) clearTimeout(timer.current);
      timer.current = null;
      // A delayed start event must not restore the listening indicator after Stop.
      recognition.onstart = null;
      setPhase('stopping');
      setStatus('Stopping voice input…');
      try {
        recognition.stop();
        if (current.current === recognition) {
          timer.current = setTimeout(() => {
            release();
            setPhase('idle');
            setStatus('Voice input stopped. Review your question before submitting.');
          }, 4000);
        }
      } catch { cancel(); }
      return;
    }
    const browser = window as SpeechWindow;
    const Constructor = browser.SpeechRecognition || browser.webkitSpeechRecognition;
    // Dismissal hides one message; every explicit attempt checks availability again.
    setErrorDismissed(false);
    setSupported(Boolean(Constructor) && window.isSecureContext);
    if (!window.isSecureContext) {
      setIssue('insecure');
      setStatus('Voice input requires a secure connection. Open Microphone Setup for help.');
      return;
    }
    if (!Constructor) {
      setIssue('unsupported');
      setStatus('Voice input is unavailable in this browser. Please type your question.');
      return;
    }
    const handled = new Set<number>();
    let started = false;
    stopRequested.current = false;
    try {
      const recognition = new Constructor();
      current.current = recognition;
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.lang = document.documentElement.lang || navigator.language || 'en-US';
      recognition.onstart = () => {
        if (current.current !== recognition) return;
        started = true;
        setIssue(null);
        setErrorDismissed(false);
        if (timer.current) clearTimeout(timer.current);
        timer.current = null;
        setPhase('listening');
        setStatus('Listening… Speak to append to your question. Select the microphone again to stop.');
      };
      recognition.onresult = (event) => {
        if (current.current !== recognition) return;
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (!result.isFinal || handled.has(i)) continue;
          handled.add(i);
          const text = result[0].transcript.trim();
          if (text) append.current(text);
        }
      };
      recognition.onerror = ({ error }) => {
        if (current.current !== recognition) return;
        release();
        setPhase('idle');
        setIssue(error);
        const errors: Record<string, string> = {
          'not-allowed': 'Microphone access is blocked or was denied. Allow access in browser and device settings before selecting Try Again. You can still type your question.',
          'service-not-allowed': 'Voice input is not allowed by this browser. Please type your question.',
          'audio-capture': 'No microphone is available. Check your microphone or type your question.',
          'no-speech': 'No speech was detected. Try the microphone again or type your question.',
          network: 'Voice input could not connect. Try again or type your question.',
          aborted: 'Voice input stopped. You can try again or type your question.',
        };
        setStatus(errors[error] || 'Voice input encountered an error. Try again or type your question.');
      };
      recognition.onend = () => {
        if (current.current !== recognition) return;
        release();
        setPhase('idle');
        if (!started && !stopRequested.current) {
          setIssue('start');
          setStatus('Voice input could not start. Open Microphone Setup for help.');
          return;
        }
        setStatus('Voice input ended. Review your question or select the microphone to speak again.');
      };
      setPhase('starting');
      setStatus('Starting voice input… Allow microphone access if prompted.');
      timer.current = setTimeout(() => {
        if (current.current !== recognition) return;
        release();
        setPhase('idle');
        setIssue('start');
        setStatus('Voice input did not start. Open Microphone Setup for help.');
      }, 10000);
      recognition.start();
    } catch {
      release();
      setPhase('idle');
      setIssue('start');
      setStatus('Voice input could not start. Check microphone permissions or type your question.');
    }
  }

  function dismissError() {
    setErrorDismissed(true);
    setStatus('');
  }

  return { supported, phase, status, issue, toggle, cancel, dismissError, needsSetup: issue !== null && !errorDismissed,
    canRetry: supported === true && issue !== null };
}
