export type VoiceOption = { id: string; name: string; language: string };
export type ReadingState = {
  available: boolean | null;
  selection: string | null;
  phase: 'idle' | 'starting' | 'playing' | 'paused';
  message: string;
  voices: VoiceOption[];
  voiceId: string | null;
};

type SpeechEngine = Pick<SpeechSynthesis, 'speak' | 'cancel' | 'pause' | 'resume'>;
type UtteranceFactory = (text: string) => SpeechSynthesisUtterance;
export const initialReadingState: ReadingState = { available: null, selection: null, phase: 'idle', message: '', voices: [], voiceId: null };
export const readingDefaults = { rate: 0.92, pitch: 1 };
const voiceId = (voice: SpeechSynthesisVoice) => JSON.stringify([voice.voiceURI, voice.lang, voice.name]);
const english = (voice: SpeechSynthesisVoice) => /^en(?:[-_]|$)/i.test(voice.lang);
function voiceScore(voice: SpeechSynthesisVoice) {
  // Retain the previously functioning Google US English voice where exposed.
  // The API has no gender field; other female candidates use explicit/documented names.
  const female = /\bfemale\b/i.test(voice.name) || /^Microsoft (?:Zira|Jenny|Aria)\b/i.test(voice.name);
  return (/^Google US English$/i.test(voice.name) ? 2000 : 0)
    + (female ? 1000 : 0)
    + (/^en[-_]US$/i.test(voice.lang) ? 100 : 0)
    + (/natural|neural|premium|enhanced/i.test(voice.name) ? 30 : 0)
    + (voice.default ? 10 : 0);
}

// Keep headings with their content where possible. Preserve every word and let
// the native speech queue handle continuous playback and punctuation pauses.
export function readingChunks(text: string): string[] {
  const chunks: string[] = [];
  let remaining = text.trim();
  while (remaining.length > 600) {
    const window = remaining.slice(0, 601);
    let end = -1;
    if (typeof Intl.Segmenter === 'function') {
      for (const segment of new Intl.Segmenter('en', { granularity: 'sentence' }).segment(window)) {
        const boundary = segment.index + segment.segment.length;
        if (boundary >= 150 && boundary <= 600 && /[.!?]["')\]]?\s*$/.test(segment.segment)) end = boundary;
      }
    }
    if (end < 0) end = Math.max(window.lastIndexOf(' ', 600), window.lastIndexOf('\n', 600));
    if (end <= 0) end = 600;
    chunks.push(remaining.slice(0, end).trim());
    remaining = remaining.slice(end).trim();
  }
  if (remaining) chunks.push(remaining);
  return chunks;
}

// Read reference notation aloud; displayed references and verse wording are untouched.
export function referenceForSpeech(reference: string): string {
  const match = reference.match(/^(.+?)\s+(\d+):(\d+)(?:[-–—](\d+)(?::(\d+))?)?$/);
  if (!match) return reference;
  const [, book, chapter, verse, end, endVerse] = match;
  return `${book}, chapter ${chapter}, ${end && !endVerse ? 'verses' : 'verse'} ${verse}${end ? endVerse ? ` through chapter ${end}, verse ${endVerse}` : ` through ${end}` : ''}`;
}

export class ResultsReader {
  private engine: SpeechEngine | null = null;
  private makeUtterance: UtteranceFactory | null = null;
  private state = initialReadingState;
  private listeners = new Set<() => void>();
  private generation = 0;
  private utterances: SpeechSynthesisUtterance[] = [];
  private language = 'en';
  private availableVoices: SpeechSynthesisVoice[] = [];
  private sessionVoice: SpeechSynthesisVoice | null = null;
  private sessionLanguage = 'en';
  private sessionText = '';

  getSnapshot = () => this.state;
  subscribe = (listener: () => void) => {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  };
  private update(values: Partial<ReadingState>) {
    this.state = { ...this.state, ...values };
    this.listeners.forEach(listener => listener());
  }
  connect(engine: SpeechEngine | null, factory: UtteranceFactory | null, language: string) {
    this.engine = engine;
    this.makeUtterance = factory;
    this.language = language;
    this.update({ available: Boolean(engine && factory) });
  }
  setVoices = (voices: SpeechSynthesisVoice[]) => {
    this.availableVoices = [...new Map(voices.filter(english).map(voice => [voiceId(voice), voice])).values()]
      .sort((a, b) => voiceScore(b) - voiceScore(a) || a.name.localeCompare(b.name) || a.lang.localeCompare(b.lang));
    const selected = this.availableVoices.find(voice => voiceId(voice) === this.state.voiceId) ?? this.availableVoices[0];
    this.update({
      voices: this.availableVoices.map(voice => ({ id: voiceId(voice), name: voice.name.replace(/ - English \([^)]+\)$/, ''), language: voice.lang.replace('_', '-') })),
      voiceId: selected ? voiceId(selected) : null,
    });
  };
  chooseVoice = (id: string) => {
    if (this.state.selection || !this.availableVoices.some(voice => voiceId(voice) === id)) return;
    this.update({ voiceId: id });
  };
  stop = () => {
    this.generation++;
    this.utterances = [];
    this.sessionText = '';
    this.sessionVoice = null;
    // Cancel even if a completion event already marked the UI idle: native
    // audio/queued speech can outlive the browser's reported playback state.
    try { this.engine?.cancel(); } catch { /* The browser may already be closing. */ }
    this.update({ selection: null, phase: 'idle', message: '' });
  };
  listen = (selection: string, text: string) => {
    const voice = this.availableVoices.find(voice => voiceId(voice) === this.state.voiceId) ?? null;
    this.begin(selection, text, voice, voice?.lang || this.language);
  };
  restart = () => {
    if (!this.state.selection || !this.sessionText) return;
    this.begin(this.state.selection, this.sessionText, this.sessionVoice, this.sessionLanguage);
  };
  private begin(selection: string, text: string, voice: SpeechSynthesisVoice | null, language: string) {
    this.stop();
    if (!this.engine || !this.makeUtterance) {
      this.update({ message: 'Listening is unavailable in this browser. You can continue reading the response.' });
      return;
    }
    const chunks = readingChunks(text);
    if (!chunks.length) return;
    this.sessionVoice = voice;
    this.sessionLanguage = language;
    this.sessionText = text;
    const generation = this.generation;
    this.update({ selection, phase: 'starting', message: '' });
    try {
      this.engine.cancel();
      this.engine.resume();
      // Queue the COMPLETE selection within the reader's click. Continuation
      // must not depend on each preceding utterance delivering an end callback.
      this.utterances = chunks.map((chunk, index) => {
        const utterance = this.makeUtterance!(chunk);
        utterance.lang = language;
        if (voice) utterance.voice = voice;
        utterance.rate = readingDefaults.rate;
        utterance.pitch = readingDefaults.pitch;
        utterance.onstart = () => {
          if (generation === this.generation && this.state.phase !== 'paused') this.update({ phase: 'playing' });
        };
        utterance.onend = () => {
          if (generation !== this.generation || index !== chunks.length - 1) return;
          this.generation++;
          this.utterances = [];
          this.sessionText = '';
          this.sessionVoice = null;
          this.update({ selection: null, phase: 'idle', message: '' });
        };
        utterance.onerror = () => { if (generation === this.generation) this.fail(); };
        return utterance;
      });
      for (const utterance of this.utterances) {
        if (generation !== this.generation) break;
        this.engine.speak(utterance);
      }
    } catch { this.fail(); }
  }
  private fail() {
    this.stop();
    this.update({ message: 'Audio could not play. You can try Listen again or continue reading the response.' });
  }
  pause = () => {
    if (!this.state.selection || this.state.phase === 'paused') return;
    try {
      this.engine?.pause();
      this.update({ phase: 'paused' });
    } catch { this.fail(); }
  };
  resume = () => {
    if (this.state.phase !== 'paused') return;
    try {
      this.engine?.resume();
      this.update({ phase: 'playing' });
    } catch { this.fail(); }
  };
}
