/* eslint-disable @typescript-eslint/no-require-imports -- Offline native-speech lifecycle harness. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

function fixture(options = {}) {
  const slots = [], effects = [], cleanups = [], instances = [], transcripts = [], timers = new Map();
  let index = 0, timerId = 0;
  const react = {
    useState(initial) { const at = index++; if (!(at in slots)) slots[at] = initial; return [slots[at], value => { slots[at] = value; }]; },
    useRef(initial) { const at = index++; return slots[at] ??= { current: initial }; },
    useEffect(effect) { const at = index++; if (!(at in slots)) { slots[at] = true; effects.push(effect); } },
  };
  class Recognition {
    constructor() { this.starts = this.stops = this.aborts = 0; instances.push(this); }
    start() { this.starts++; if (options.startThrows) throw new Error('Offline start failure'); }
    stop() { this.stops++; }
    abort() { this.aborts++; }
  }
  const source = ts.transpileModule(fs.readFileSync(path.join(__dirname, '../app/lib/useQuestionSpeech.ts'), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  const exports = {};
  vm.runInNewContext(source, {
    exports,
    require(name) { assert.equal(name, 'react'); return react; },
    window: { isSecureContext: options.secure ?? true, SpeechRecognition: options.unsupported ? undefined : Recognition },
    document: { documentElement: { lang: options.lang ?? 'en' } },
    navigator: { language: options.preferredLanguage ?? 'en-US', userAgent: options.userAgent ?? 'Windows NT 10.0 Chrome/157.0.0.0' },
    setTimeout(fn, ms) { const id = ++timerId; timers.set(id, { fn, ms }); return id; },
    clearTimeout(id) { timers.delete(id); },
  });
  function render() { index = 0; return exports.useQuestionSpeech(text => transcripts.push(text)); }
  render();
  for (const effect of effects.splice(0)) { const cleanup = effect(); if (cleanup) cleanups.push(cleanup); }
  return { render, instances, transcripts, timers, unmount() { for (const cleanup of cleanups) cleanup(); } };
}

test('speech availability never starts recognition; explicit start preserves browser language and options', () => {
  const f = fixture();
  assert.equal(f.render().supported, true);
  assert.equal(f.instances.length, 0);
  f.render().toggle(); const r = f.instances[0];
  assert.equal(r.starts, 1);
  assert.equal(r.lang, 'en');
  assert.equal(r.continuous, true);
  assert.equal(r.interimResults, false);
  r.onstart();
  assert.equal(f.render().phase, 'listening');
  assert.equal(f.timers.size, 0);
});

test('only final results append once; stop and a new manual attempt preserve editability contract', () => {
  const f = fixture(); f.render().toggle(); const r = f.instances[0]; r.onstart();
  const results = [{ isFinal: true, 0: { transcript: ' Genesis 1:1 ' } }, { isFinal: false, 0: { transcript: 'interim ignored' } }];
  r.onresult({ resultIndex: 0, results }); r.onresult({ resultIndex: 0, results });
  assert.deepEqual(f.transcripts, ['Genesis 1:1']);
  f.render().toggle(); assert.equal(r.stops, 1); assert.equal(r.onstart, null);
  r.onend(); assert.equal(f.render().phase, 'idle');
  assert.match(f.render().status, /Review your question/);
  f.render().toggle(); assert.equal(f.instances.length, 2);
});

const windowsEdge = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/157.0.0.0 Edg/157.0.0.0';
for (const [name, options, expected] of [
  ['Windows Edge bare English uses regional preference', { userAgent: windowsEdge }, 'en-US'],
  ['Windows Edge keeps a regional English preference', { userAgent: windowsEdge, preferredLanguage: 'en-GB' }, 'en-GB'],
  ['Windows Edge bare preference receives English fallback', { userAgent: windowsEdge, preferredLanguage: 'en' }, 'en-US'],
  ['Windows Edge non-English preference does not override English page', { userAgent: windowsEdge, preferredLanguage: 'fr-FR' }, 'en-US'],
  ['Windows Edge keeps explicit page region', { userAgent: windowsEdge, lang: 'en-AU' }, 'en-AU'],
  ['Windows Edge keeps non-English page language', { userAgent: windowsEdge, lang: 'de' }, 'de'],
  ['Chrome keeps bare English', {}, 'en'],
  ['iPad Safari keeps bare English', { userAgent: 'Mozilla/5.0 (iPad; CPU OS 18_7_8 like Mac OS X) Version/18.7 Mobile Safari/605.1.15' }, 'en'],
  ['iPad Edge keeps bare English', { userAgent: 'Mozilla/5.0 (iPad; CPU OS 18_7 like Mac OS X) EdgiOS/157.0 Mobile Safari/605.1.15' }, 'en'],
  ['Mac Edge stays outside Windows-only correction', { userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X) Edg/157.0' }, 'en'],
]) {
  test(name, () => {
    const f = fixture(options); f.render().toggle(); const recognition = f.instances[0];
    assert.equal(recognition.lang, expected);
    assert.equal(recognition.continuous, true);
    assert.equal(recognition.interimResults, false);
    assert.equal(recognition.starts, 1);
  });
}

for (const [error, message] of Object.entries({
  network: /could not connect/,
  'not-allowed': /blocked or was denied/,
  'service-not-allowed': /not allowed by this browser/,
  'audio-capture': /No microphone is available/,
  'no-speech': /No speech was detected/,
})) {
  test(`${error} preserves native error category, disposes recognition and permits only a manual retry`, () => {
    const f = fixture(); f.render().toggle(); const old = f.instances[0]; old.onstart();
    const staleResult = old.onresult, staleStart = old.onstart;
    old.onerror({ error });
    const state = f.render();
    assert.equal(state.issue, error); assert.equal(state.phase, 'idle'); assert.match(state.status, message);
    assert.equal(state.canRetry, true); assert.equal(old.aborts, 1); assert.equal(old.onresult, null);
    assert.equal(f.instances.length, 1); assert.equal(f.timers.size, 0);
    state.toggle(); const current = f.instances[1];
    staleResult({ resultIndex: 0, results: [{ isFinal: true, 0: { transcript: 'stale' } }] }); staleStart();
    assert.deepEqual(f.transcripts, []); assert.equal(f.render().phase, 'starting');
    current.onstart(); assert.equal(f.render().issue, null); assert.equal(f.render().phase, 'listening');
  });
}

test('unmount aborts and detaches native handlers; stale results cannot append', () => {
  const f = fixture(); f.render().toggle(); const r = f.instances[0]; const stale = r.onresult;
  f.unmount();
  assert.equal(r.aborts, 1); assert.equal(r.onstart, null); assert.equal(r.onerror, null); assert.equal(f.timers.size, 0);
  stale({ resultIndex: 0, results: [{ isFinal: true, 0: { transcript: 'stale' } }] });
  assert.deepEqual(f.transcripts, []);
});

test('cancel leaves recognition idle without automatic restart', () => {
  const f = fixture(); f.render().toggle(); const r = f.instances[0]; r.onstart(); f.render().cancel();
  assert.equal(r.aborts, 1); assert.equal(f.render().phase, 'idle'); assert.equal(f.instances.length, 1);
  assert.match(f.render().status, /You can edit your question/);
});

test('start and stop watchdogs release stalled sessions for explicit retry', () => {
  const f = fixture(); f.render().toggle();
  const startTimer = [...f.timers.values()].find(t => t.ms === 10000); startTimer.fn();
  assert.equal(f.render().phase, 'idle'); assert.equal(f.render().issue, 'start');
  f.render().toggle(); const r = f.instances[1]; r.onstart(); f.render().toggle();
  const stopTimer = [...f.timers.values()].find(t => t.ms === 4000); stopTimer.fn();
  assert.equal(f.render().phase, 'idle'); assert.equal(r.aborts, 1); assert.equal(f.instances.length, 2);
});

for (const options of [{ secure: false }, { unsupported: true }, { startThrows: true }]) {
  test(`unavailable/insecure/synchronous failure is recoverable: ${JSON.stringify(options)}`, () => {
    const f = fixture(options); f.render().toggle();
    assert.equal(f.render().phase, 'idle'); assert.equal(f.render().needsSetup, true);
    assert.equal(f.instances.length, options.startThrows ? 1 : 0);
    f.render().dismissError(); assert.equal(f.render().needsSetup, false);
  });
}
