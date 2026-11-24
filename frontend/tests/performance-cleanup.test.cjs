/* eslint-disable @typescript-eslint/no-require-imports -- Existing offline Node harness. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { execFileSync } = require('node:child_process');
const ts = require('typescript');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const app = path.join(__dirname, '../app');

function load(file, mocks, globals = {}) {
  // These watchdog tests exercise the accepted release's App Router handoff.
  // The incremental reader has a separate browser suite.
  const source = file === 'why.tsx'
    ? execFileSync('git', ['show', 'c07929136719fd2686fb27c881ed8e211fa464ea:frontend/app/why.tsx'], { cwd: app, encoding: 'utf8' })
    : fs.readFileSync(path.join(app, file), 'utf8');
  const output = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, target: ts.ScriptTarget.ES2020, esModuleInterop: true },
  }).outputText;
  const exports = {};
  vm.runInNewContext(output, { exports, require(name) {
    if (Object.hasOwn(mocks, name)) return mocks[name];
    if (name.startsWith('.')) throw new Error('Unexpected local dependency');
    return require(name);
  }, ...globals });
  return exports;
}

function hookState() {
  const slots = [];
  const effects = [], cleanups = [];
  let index = 0;
  return { slots, reset() { index = 0; }, mount() { for (const effect of effects.splice(0)) { const cleanup = effect(); if (cleanup) cleanups.push(cleanup); } }, unmount() { for (const cleanup of cleanups) cleanup(); }, react: {
    ...React,
    useState(initial) {
      const at = index++;
      if (!(at in slots)) slots[at] = typeof initial === 'function' ? initial() : initial;
      return [slots[at], value => { slots[at] = typeof value === 'function' ? value(slots[at]) : value; }];
    },
    useRef(initial) { const at = index++; return slots[at] ??= { current: initial }; },
    useEffect(effect) { effects.push(effect); }, useMemo(fn) { return fn(); },
  } };
}
function find(node, predicate) {
  if (!node || typeof node !== 'object') return undefined;
  if (predicate(node)) return node;
  for (const child of React.Children.toArray(node.props?.children)) {
    const match = find(child, predicate); if (match) return match;
  }
}
const result = {
  verses: [{ reference: 'John 3:16', text: 'Offline Scripture fixture.', testament: 'NT' }],
  summary: 'Offline Summary.', context: 'Offline Context.', reflection: 'Offline Reflection.',
};
function submission(options = {}) {
  const hooks = hookState(), calls = [], timers = [], navigations = [], cancels = [];
  const cleared = new Set();
  const decision = options.decision ?? { decision: 'PROCEED', execution_payload: { question: 'Offline question', translation: 'KJV', want_commentary: true } };
  const Page = load('why.tsx', {
    react: hooks.react,
    'next/navigation': { useRouter: () => ({ push(url) { if (options.pushError) throw new Error('Offline router failure'); navigations.push(url); } }) },
    './lib/btaApi': { async runReflection() { calls.push('query'); return options.query ? options.query() : decision; }, getQueryCount: () => 0 },
    './lib/useQuestionSpeech': { useQuestionSpeech: () => ({ cancel() { cancels.push(1); }, supported: true, phase: 'idle', issue: options.speechIssue, status: options.speechStatus, needsSetup: Boolean(options.speechIssue) }) },
    './components/audience/AudiencePrompt': () => null,
    './components/MicrophoneSetup': () => null,
  }, {
    process: { env: { NEXT_PUBLIC_API_BASE_URL: 'http://127.0.0.1:8000' } },
    setTimeout(fn, ms) { timers.push({ fn, ms }); return timers.length; },
    clearTimeout(id) { cleared.add(id); },
    document: { addEventListener() {}, removeEventListener() {} },
    async fetch(url, request) {
      assert.ok(url === 'http://127.0.0.1:8000/api/results', 'Only the fixed local fixture destination is permitted');
      calls.push('results');
      assert.ok(JSON.stringify(JSON.parse(request.body).execution_payload) === JSON.stringify(decision.execution_payload), 'Execution payload preserved');
      if (options.fetchError) throw new Error('Offline transport failure');
      return { ok: options.ok ?? true, status: options.status ?? 200, async json() {
        if (options.parseError) throw new Error('Offline invalid JSON');
        return options.body ?? result;
      } };
    },
  }).default;
  function render() { hooks.reset(); return Page(); }
  const tree = render();
  hooks.mount();
  find(tree, n => n.type === 'input').props.ref.current = { value: options.input ?? 'Offline question' };
  return { calls, timers, navigations, cancels, cleared, unmount: hooks.unmount, render, submit: find(tree, n => n.type === 'form').props.onSubmit };
}

test('recognition network failure shows its connection status rather than alleging microphone denial', () => {
  const s = submission({ speechIssue: 'network', speechStatus: 'Voice input could not connect. Try again or type your question.' });
  const html = renderToStaticMarkup(s.render());
  assert.ok(html.includes('Voice input could not connect'));
  assert.ok(html.includes('Try again or type your question.'));
  assert.ok(!html.includes('Microphone is unavailable'));
  assert.ok(!html.includes('BTA cannot access your microphone'));
  assert.equal(find(s.render(), n => n.type === 'input').props.disabled, false);
  assert.equal(s.calls.length, 0);
});

test('audio capture failure retains microphone setup and editable typing fallback', () => {
  const s = submission({ speechIssue: 'audio-capture' });
  assert.ok(renderToStaticMarkup(s.render()).includes('Microphone is unavailable'));
  assert.equal(find(s.render(), n => n.type === 'input').props.disabled, false);
});

test('Edge connection guidance does not suggest changing microphone permissions or selecting a speech provider', () => {
  const hooks = hookState();
  const Setup = load('components/MicrophoneSetup.tsx', { react: hooks.react }, { navigator: { userAgent: 'Windows Edg/157.0.0.0', maxTouchPoints: 0 } }).default;
  const render = () => { hooks.reset(); return Setup({ issue: 'network' }); };
  const initial = render();
  find(initial, n => n.type === 'button' && n.props.children === 'Microphone Setup').props.onClick();
  const tree = render();
  const html = renderToStaticMarkup(tree);
  assert.ok(html.includes('Microsoft Edge could not connect to its speech-recognition service.'));
  assert.ok(html.includes('even when microphone access is allowed'));
  assert.ok(html.includes('does not switch the browser or speech-recognition service'));
  assert.ok(!html.includes('In Windows Settings'));
  find(tree, n => n.type === 'select').props.onChange({ target: { value: 'Chrome' } });
  assert.ok(renderToStaticMarkup(render()).includes('Your browser could not connect'));
});

test('successful navigation is immediate, preserves payload and stays busy until route transition', async () => {
  const s = submission(); await s.submit({ preventDefault() {} });
  assert.deepEqual(s.calls, ['query', 'results']);
  assert.equal(s.navigations.length, 1);
  const url = new URL(s.navigations[0], 'http://127.0.0.1:3000');
  assert.equal(url.pathname, '/results');
  assert.ok(JSON.stringify(JSON.parse(url.searchParams.get('payload'))) === JSON.stringify(result), 'Result payload round-trips unchanged');
  assert.deepEqual(s.timers.map(t => t.ms), [5000, 12500, 15000]);
  assert.equal(find(s.render(), n => n.type === 'input').props.disabled, true);
  await s.submit(); assert.equal(s.calls.length, 2);
});

test('uncommitted navigation releases the form for manual retry without automatic requests', async () => {
  const s = submission(); await s.submit();
  s.timers[2].fn();
  assert.equal(find(s.render(), n => n.type === 'input').props.disabled, false);
  assert.ok(renderToStaticMarkup(s.render()).includes('The results page did not open. Please try again.'));
  assert.deepEqual(s.calls, ['query', 'results']);
  await s.submit();
  assert.deepEqual(s.calls, ['query', 'results', 'query', 'results']);
  s.timers[2].fn();
  assert.equal(find(s.render(), n => n.type === 'input').props.disabled, true);
});

test('successful route unmount disposes recovery and ignores a queued callback', async () => {
  const s = submission(); await s.submit(); s.unmount();
  assert.ok(s.cleared.has(3));
  s.timers[2].fn();
  assert.equal(find(s.render(), n => n.type === 'input').props.disabled, true);
  assert.ok(!renderToStaticMarkup(s.render()).includes('The results page did not open.'));
  assert.deepEqual(s.calls, ['query', 'results']);
});

test('synchronous navigation failure disposes its recovery callback', async () => {
  const s = submission({ pushError: true }); await s.submit();
  assert.ok(s.cleared.has(3));
  s.timers[2].fn();
  assert.ok(!renderToStaticMarkup(s.render()).includes('The results page did not open.'));
  assert.equal(find(s.render(), n => n.type === 'input').props.disabled, false);
});

test('same-tick duplicate submission cannot start a second request', async () => {
  let finish;
  const s = submission({ query: () => new Promise(resolve => { finish = resolve; }) });
  const first = s.submit(); await s.submit();
  assert.deepEqual(s.calls, ['query']);
  finish({ decision: 'PROCEED', execution_payload: { question: 'Offline question', translation: 'KJV', want_commentary: true } });
  await first; assert.equal(s.navigations.length, 1);
});

test('empty input does not start requests, timers or speech cancellation', async () => {
  const s = submission({ input: '   ' }); await s.submit();
  assert.equal(s.calls.length + s.timers.length + s.cancels.length, 0);
});

for (const [name, options] of Object.entries({
  redirect: { decision: { decision: 'REDIRECT', message: 'Offline clarification.' } },
  stop: { decision: { decision: 'STOP', message: 'Offline stop.' } },
  missing_payload: { decision: { decision: 'PROCEED' } },
  clarification: { ok: false, status: 422, body: { detail: 'Offline clarification.' } },
  server_error: { ok: false, status: 500 },
  network_error: { fetchError: true },
  invalid_json: { parseError: true },
  navigation_error: { pushError: true },
})) {
  test(`${name} does not navigate and releases loading and submission guard for retry`, async () => {
    const s = submission(options); await s.submit();
    assert.equal(s.navigations.length, 0);
    assert.equal(find(s.render(), n => n.type === 'input').props.disabled, false);
    const count = s.calls.length; await s.submit();
    assert.ok(s.calls.length > count, 'Retry is accepted after failure');
  });
}

test('results render Scripture Summary Context and Reflection with collapsed exploration and plain references', () => {
  const hooks = hookState();
  const Page = load('results/results-client.tsx', {
    react: hooks.react,
    'next/navigation': { useRouter: () => ({ push() {} }), useSearchParams: () => new URLSearchParams({ payload: JSON.stringify({ ...result, context_exploration: 'Offline hidden exploration.' }) }) },
    '../components/ExpandableSection': ({ preview }) => preview,
    '../components/ListeningControls': Object.assign(() => null, { listeningStatus: () => '' }),
    '../lib/resultsReader': { referenceForSpeech: text => text },
    '../lib/useResultsReader': { useResultsReader: () => ({ state: { available: true }, stop() {} }) },
  }).default;
  const html = renderToStaticMarkup(Page());
  for (const section of ['Offline Scripture fixture.', 'Offline Summary.', 'Offline Context.', 'Offline Reflection.']) assert.ok(html.includes(section), 'Required section rendered');
  assert.ok(!html.includes('Offline hidden exploration.'));
  assert.ok(html.includes('<strong>John 3:16</strong>'));
});
