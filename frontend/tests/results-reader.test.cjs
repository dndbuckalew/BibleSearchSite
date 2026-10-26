const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const source = fs.readFileSync(path.join(__dirname, '../app/lib/resultsReader.ts'), 'utf8');
const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const exported = {};
vm.runInNewContext(output, { exports: exported });
const { ResultsReader, readingChunks, referenceForSpeech } = exported;
const normalize = text => text.replace(/\s+/g, ' ').trim();
const voice = (name, lang = 'en-US', isDefault = false) => ({ name, lang, voiceURI: name, default: isDefault, localService: true });
function setup() {
  const calls = [], utterances = [];
  const engine = {
    speak(u) { calls.push('speak'); utterances.push(u); },
    cancel() { calls.push('cancel'); }, pause() { calls.push('pause'); }, resume() { calls.push('resume'); },
  };
  const reader = new ResultsReader();
  reader.connect(engine, text => ({ text }), 'en');
  return { reader, engine, calls, utterances };
}

test('connection and asynchronous voice discovery never start audio', () => {
  const { reader, calls } = setup();
  reader.setVoices([voice('Google US English')]);
  assert.equal(reader.getSnapshot().available, true);
  assert.equal(reader.getSnapshot().phase, 'idle');assert.equal(calls.length, 0);
});
test('short Scripture keeps heading, reference and full verse in one utterance', () => {
  const { reader, utterances } = setup();
  const text = 'Old Testament\n\nPsalm, chapter 23, verse 1. The LORD is my shepherd; I shall not want.';
  reader.listen('scripture', text);
  assert.equal(utterances.length, 1);assert.equal(utterances[0].text, text);
  utterances[0].onstart();assert.equal(reader.getSnapshot().phase, 'playing');
  utterances[0].onend();assert.equal(reader.getSnapshot().phase, 'idle');
});
test('complete long response is queued before any end event, preserving every word and order', () => {
  const { reader, utterances } = setup();
  const text = 'Scriptures.\n' + Array.from({ length: 200 }, (_, i) => `Passage ${i}. All these original words must be narrated.`).join('\n\n') + '\n\n\nReflection. The final reflection sentence must also be read.';
  reader.listen('entire', text);
  assert(utterances.length > 10);assert(utterances.every(u => u.text.length <= 600));
  assert.equal(normalize(utterances.map(u => u.text).join(' ')), normalize(text));
  assert.match(utterances.at(-1).text, /final reflection sentence must also be read/);
  // Simulate a lost early end callback: the browser already has every subsequent utterance.
  utterances.at(-1).onstart();utterances.at(-1).onend();assert.equal(reader.getSnapshot().phase, 'idle');
});
test('long unpunctuated content is bounded without dropping words', () => {
  const text = Array.from({ length: 1200 }, (_, i) => `word${i}`).join(' ');
  const chunks = Array.from(readingChunks(text));assert.equal(chunks.join(' '), text);
  assert(chunks.every(chunk => chunk.length <= 600));assert.equal(Array.from(readingChunks('   ')).length, 0);
});
test('Pause and Resume retain the queued utterances and browser position indefinitely', () => {
  const { reader, calls, utterances } = setup();
  reader.listen('reflection', 'Original reflection. '.repeat(100));utterances[0].onstart();
  const queued = utterances.slice(), count = calls.filter(c => c === 'speak').length;
  utterances[0].charIndex = 17;reader.pause();assert.equal(reader.getSnapshot().phase, 'paused');
  utterances[1].onstart();assert.equal(reader.getSnapshot().phase, 'paused');
  reader.resume();assert.equal(reader.getSnapshot().phase, 'playing');
  assert.equal(calls.filter(c => c === 'speak').length, count);assert.deepEqual(utterances, queued);assert.equal(utterances[0].charIndex, 17);
  assert.deepEqual(calls.slice(-2), ['pause', 'resume']);
});
test('Restart requeues exactly the current complete selection from the beginning, including while paused', () => {
  const { reader, utterances } = setup();const text = 'Full reflection. '.repeat(120);
  reader.listen('reflection', text);const original = utterances.map(u => u.text);const old = utterances[0];
  reader.pause();reader.restart();assert.equal(reader.getSnapshot().selection, 'reflection');
  assert.deepEqual(utterances.slice(original.length).map(u => u.text), original);
  assert.notEqual(utterances[original.length], old);
  old.onend();old.onerror();assert.equal(reader.getSnapshot().selection, 'reflection');
  reader.stop();reader.restart();assert.equal(utterances.length, original.length * 2);
});
test('switching or stopping cancels the entire prior queue and ignores all stale callbacks', () => {
  const { reader, calls, utterances } = setup();
  reader.listen('entire', 'Original response. '.repeat(100));const old = utterances.slice();reader.pause();
  reader.listen('reflection', 'Reflection only.');assert.equal(calls.at(-3), 'cancel');
  const state = reader.getSnapshot();old.forEach(u => { u.onstart();u.onend();u.onerror(); });assert.equal(reader.getSnapshot(), state);
  reader.stop();assert.equal(calls.at(-1), 'cancel');assert.equal(reader.getSnapshot().selection, null);
});
test('female English preference retains Google US English and does not force male voices', () => {
  const { reader, utterances } = setup();
  reader.setVoices([voice('Microsoft David - English (United States)', 'en-US', true), voice('Google US English'), voice('Microsoft Zira - English (United States)')]);
  assert.equal(reader.getSnapshot().voices[0].name, 'Google US English');
  reader.listen('reflection', 'Original words.');assert.equal(utterances[0].voice.name, 'Google US English');reader.stop();
  reader.setVoices([voice('Microsoft David - English (United States)', 'en-US', true), voice('Microsoft Zira - English (United States)')]);assert.equal(reader.getSnapshot().voices[0].name, 'Microsoft Zira');
  reader.setVoices([voice('Google UK English Male', 'en-GB'), voice('Google UK English Female', 'en-GB')]);assert.equal(reader.getSnapshot().voices[0].name, 'Google UK English Female');
});
test('voice, language, rate and pitch remain consistent through all chunks and Restart', () => {
  const { reader, utterances } = setup();const selected = voice('Google US English');
  reader.setVoices([selected]);reader.listen('entire', 'Original response. '.repeat(100));
  reader.setVoices([voice('Microsoft Zira - English (United States)')]);reader.restart();
  assert(utterances.every(u => u.voice === selected && u.lang === 'en-US' && u.rate === 0.92 && u.pitch === 1));
});
test('unavailable/empty synthesis and synchronous or asynchronous errors fail gracefully without auto retry', () => {
  const { reader, engine, utterances } = setup();reader.listen('empty', ' ');assert.equal(utterances.length, 0);
  reader.connect(null, null, 'en');reader.listen('entire', 'Text');assert.match(reader.getSnapshot().message, /unavailable/);
  reader.connect(engine, text => ({ text }), 'en');reader.listen('entire', 'Text');utterances[0].onerror();assert.match(reader.getSnapshot().message, /could not play/);
  engine.speak = () => { throw Error('blocked'); };reader.listen('entire', 'Text');assert.equal(reader.getSnapshot().phase, 'idle');assert.match(reader.getSnapshot().message, /could not play/);
});
test('missing preferred voices fall back to available English or browser language without playback on discovery', () => {
  const { reader, utterances, calls } = setup();reader.setVoices([voice('UK English', 'en-GB')]);assert.equal(calls.length, 0);
  reader.listen('reflection', 'Text');assert.equal(utterances[0].lang, 'en-GB');reader.stop();reader.setVoices([]);
  reader.listen('reflection', 'Text');assert.equal(utterances.at(-1).voice, undefined);assert.equal(utterances.at(-1).lang, 'en');
});
test('reference pronunciation preserves recognized notation meaning and leaves complex references intact', () => {
  assert.equal(referenceForSpeech('John 3:16'), 'John, chapter 3, verse 16');
  assert.equal(referenceForSpeech('Psalm 23:1–3'), 'Psalm, chapter 23, verses 1 through 3');
  assert.equal(referenceForSpeech('1 John 3:16-4:2'), '1 John, chapter 3, verse 16 through chapter 4, verse 2');
  assert.equal(referenceForSpeech('John 3:16, 18'), 'John 3:16, 18');
});

test('late callbacks after natural completion cannot revive controls or report a new failure', () => {
  const { reader, utterances } = setup();reader.listen('reflection', 'Complete reflection.');
  const u = utterances[0];u.onstart();u.onend();const completed = reader.getSnapshot();
  u.onstart();u.onerror();u.onend();assert.equal(reader.getSnapshot(), completed);assert.equal(completed.phase, 'idle');
});

test('Stop and teardown cancel native speech even after the UI reports completion', () => {
  const { reader, calls, utterances } = setup();reader.listen('reflection', 'A completed reflection.');
  utterances[0].onstart();utterances[0].onend();assert.equal(reader.getSnapshot().phase, 'idle');
  const count = calls.filter(c => c === 'cancel').length;reader.stop();
  assert.equal(calls.filter(c => c === 'cancel').length, count + 1);
  assert.equal(reader.getSnapshot().selection, null);reader.stop();assert.equal(calls.at(-1), 'cancel');
});
