'use client';

import { useRef, useState } from 'react';

function detectEnvironment() {
  const ua = navigator.userAgent;
  const ios = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  const os = ios ? 'iOS' : /Android/.test(ua) ? 'Android' : /Windows/.test(ua) ? 'Windows'
    : /Macintosh/.test(ua) ? 'macOS' : 'other';
  const browser = /Edg\/|EdgA\/|EdgiOS\//.test(ua) ? 'Edge'
    : /OPR\/|SamsungBrowser\//.test(ua) ? ''
    : /Chrome\/|CriOS\//.test(ua) ? 'Chrome'
    : /Firefox\/|FxiOS\//.test(ua) ? 'Firefox' : /Safari\//.test(ua) ? 'Safari' : '';
  return { os, browser };
}

function setupSteps(browser: string, os: string): string[] {
  if (!browser) return [];
  if (os === 'iOS' && browser !== 'Safari') return [
    `Open your iPhone or iPad Settings, choose Apps, then ${browser} (or find ${browser} directly in Settings on older versions). Turn on Microphone if shown.`,
    `Return to BTA in ${browser}. When you try the microphone again, choose Allow if asked. If no microphone setting or request appears, voice input may be unavailable in this browser.`,
  ];
  if (browser === 'Safari') return os === 'iOS' ? [
    'In Safari, open BTA and tap the page menu beside the website address (it may look like aA). Choose More if needed, then Website Settings.',
    'Choose Microphone, then Allow. If this setting is missing, open your device Settings, then Apps, Safari, and Microphone (or Settings, Safari on older versions). Choose Ask so Safari can ask for permission.',
    'Return to BTA. When you try the microphone again, choose Allow if asked.',
  ] : [
    'On a Mac, open the Safari menu, then Settings, then Websites.',
    'Choose Microphone. Find the BTA website and choose Allow.',
    'Return to BTA. If you are using another device, Safari microphone settings may be unavailable; you can type your question instead.',
  ];
  if (browser === 'Firefox') return os === 'Android' ? [
    'In Firefox, open BTA and tap the padlock beside the website address. Open Permissions if shown and clear a blocked microphone permission.',
    'In Android Settings, open Apps, Firefox, Permissions, then Microphone. Allow access while using the app.',
    'Return to BTA. If asked to use your microphone, choose Allow. Voice input may be unavailable in Firefox even when microphone access is allowed.',
  ] : [
    'In Firefox, open Settings from the three-line menu. Choose Privacy & Security.',
    'Under Permissions, find Microphone and choose Settings. Find BTA and remove its blocked entry, then save your changes. If requests are blocked, allow websites to ask for microphone access.',
    'Return to BTA. If asked to use your microphone, choose Allow. Voice input may be unavailable in Firefox even when microphone access is allowed.',
  ];
  if (os === 'Android') return [
    `In ${browser}, open the three-dot menu, then Settings. Find Site settings or Site permissions, then Microphone. Allow websites to ask for access.`,
    'If BTA is listed as blocked, select it and allow microphone access or clear the blocked permission.',
    `In Android Settings, open Apps, ${browser}, Permissions, then Microphone. Allow access while using the app, then return to BTA. Choose Allow if asked when you try again.`,
  ];
  return [
    `In ${browser}, open BTA and click the site controls or padlock beside the website address.`,
    `Open ${browser === 'Edge' ? 'Permissions for this site' : 'Site settings'}. Find Microphone and choose Allow for BTA. If you see a reset option instead, reset the blocked microphone permission so the browser can ask again.`,
    'Return to BTA. When you try the microphone again, choose Allow if asked.',
  ];
}

function deviceGuidance(os: string, browser: string) {
  if (os === 'Windows') return 'In Windows Settings, open Privacy & security (Privacy on Windows 10), then Microphone. Check microphone access and access for desktop apps, including your browser.';
  if (os === 'macOS') return 'On your Mac, open System Settings, then Privacy & Security, then Microphone. Allow your browser if listed. Check Speech Recognition too if your browser requests it.';
  if (os === 'iOS') return 'In your iPhone or iPad Settings, open Privacy & Security, then Microphone. Allow your browser if listed. Check Speech Recognition too if requested.';
  if (os === 'Android') return `In Android Settings, open Apps, ${browser || 'your browser'}, Permissions, then Microphone. Check that microphone access is allowed and your device’s microphone privacy switch is on.`;
  return 'In your device’s sound or privacy settings, check that your browser can use the microphone and that the correct microphone is selected.';
}

export default function MicrophoneSetup({ issue }: { issue: string | null }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const [environment, setEnvironment] = useState({ os: 'other', browser: '' });
  const control = 'min-h-11 rounded px-2 underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-500';
  const heading = 'mt-5 font-semibold';
  const steps = setupSteps(environment.browser, environment.os);

  return (
    <>
      <button ref={trigger} type="button" className={control} onClick={() => {
        setEnvironment(detectEnvironment());
        dialog.current?.showModal();
      }}>Microphone Setup</button>
      <dialog
        ref={dialog}
        aria-labelledby="microphone-setup-title"
        aria-describedby="microphone-setup-description"
        onClose={() => trigger.current?.focus({ preventScroll: true })}
        className="m-auto max-h-[80dvh] w-[calc(100%_-_2rem)] max-w-lg overflow-y-auto rounded-lg border border-neutral-300 bg-white p-5 text-base text-neutral-800 shadow-xl backdrop:bg-black/40"
      >
        <div className="flex items-center justify-between gap-2">
          <h2 id="microphone-setup-title" className="text-xl font-semibold">Microphone Setup</h2>
          <button type="button" autoFocus aria-label="Close Microphone Setup" className={`${control} shrink-0 text-xl no-underline`} onClick={() => dialog.current?.close()}><span aria-hidden="true">×</span></button>
        </div>
        <p id="microphone-setup-description" className="mt-3">To use your microphone, you may need to allow BTA to access it. If you prefer not to use your microphone, you can simply type your question.</p>
        <h3 className={heading}><label htmlFor="microphone-browser">Select Your Browser</label></h3>
        <select id="microphone-browser" value={environment.browser} onChange={(event) => setEnvironment({ ...environment, browser: event.target.value })} className="mt-2 min-h-11 w-full rounded border border-neutral-400 bg-white px-2 focus-visible:outline-2 focus-visible:outline-neutral-500">
          <option value="" disabled>Select your browser</option>
          <option value="Chrome">Google Chrome</option>
          <option value="Safari">Apple Safari</option>
          <option value="Edge">Microsoft Edge</option>
          <option value="Firefox">Mozilla Firefox</option>
        </select>
        <h3 className={heading}>Microphone Setup Instructions</h3>
        <div aria-live="polite" aria-atomic="true">
          {steps.length ? <ol className="mt-2 list-decimal space-y-2 pl-5">{steps.map(step => <li key={step}>{step}</li>)}</ol> : <p className="mt-2">Choose your browser above to see its instructions.</p>}
        </div>
        <p className="mt-2">Menu names may vary with your browser or device version.</p>
        <h3 className={heading}>Still Having Trouble?</h3>
        {issue === 'insecure' ? <div className="mt-2 space-y-2">
          <p>Your browser may be blocking your microphone because of the website address you&apos;re using.</p>
          <p>Try opening BTA at <a className="underline focus-visible:outline-2" href="https://www.bibleta.com/" target="_blank" rel="noopener noreferrer">www.bibleta.com</a> and using the microphone again.</p>
        </div> : <div className="mt-2 space-y-2">
          <p>{issue === 'unsupported' ? 'Voice input is unavailable in this browser. You can try BTA in another browser, or type your question instead.'
            : issue === 'network' ? 'Voice input could not connect. Check your internet connection and try again. You can type your question instead.'
            : issue === 'audio-capture' ? 'Your browser could not access a microphone. Check that it is connected and selected in your device’s sound settings. Close other apps that may be using it.'
            : issue === 'no-speech' ? 'No speech was detected. Check that your microphone is not muted and try speaking again.'
            : issue === 'service-not-allowed' ? 'Your browser reported that voice input is not allowed. Check browser and device permissions. Voice input may still be unavailable in this browser.'
            : 'Check microphone access in your browser and device settings. Voice input may still be unavailable even when access is allowed.'}</p>
          <p>{deviceGuidance(environment.os, environment.browser)}</p>
        </div>}
        <h3 className={heading}>Check Your Microphone</h3>
        <div className="mt-2 space-y-2">
          <p>Make sure your microphone is connected and turned on.</p>
          <p>If your microphone has a mute button, make sure it is not muted.</p>
          <p>If you&apos;re using a computer provided by your church, workplace, or school, you may need help from the person who manages it.</p>
        </div>
        <h3 className={heading}>Try Your Microphone Again</h3>
        <div className="mt-2 space-y-2">
          <p>Once you&apos;ve updated your microphone settings, click the X in the upper-right corner to close this window.</p>
          <p>Then click the microphone icon in BTA to try speaking again.</p>
        </div>
        <h3 className={heading}>Still not working?</h3>
        <p className="mt-2">You can continue using BTA by typing your question instead of speaking. All Bible study features remain available without a microphone.</p>
      </dialog>
    </>
  );
}
