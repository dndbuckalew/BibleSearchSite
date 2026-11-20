// Normalize Scripture input before submitting a lookup.
const book = '(?:[1-3]\\s*)?\\p{L}[\\p{L}\\p{M}]*(?:[ .]+\\p{L}[\\p{L}\\p{M}]*)*';
const spokenReference = new RegExp(
  '^(' + book + ')[\\s,.:;]+chapter[\\s,.:;]+(\\d+|[a-z -]+?)[\\s,.:;]+verse[\\s,.:;]+(\\d+|[a-z -]+?)[\\s.!?,;]*$',
  'iu',
);
const compactReference = /^(?:[1-3]\s*)?\p{L}[\p{L}\p{M}]*\s+(\d{3,})[.!?,;]*$/u;
const smallNumbers = ' one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split(' ');
const tens = '  twenty thirty forty fifty sixty seventy eighty ninety'.split(' ');

function spokenNumber(value: string): string | undefined {
  if (/^\d+$/.test(value)) return value;
  let words = value.toLowerCase().trim().split(/[\s-]+/);
  let hundreds = 0;
  const first = smallNumbers.indexOf(words[0]);
  if (first > 0 && first < 10 && words[1] === 'hundred') {
    hundreds = first * 100;
    words = words.slice(2);
    if (!words.length) return String(hundreds);
    if (words[0] === 'and') words = words.slice(1);
  }
  if (words.length === 1) {
    const small = smallNumbers.indexOf(words[0]);
    if (small > 0) return String(hundreds + small);
  }
  const ten = tens.indexOf(words[0]);
  if (ten < 2) return undefined;
  if (words.length === 1) return String(hundreds + ten * 10);
  const unit = smallNumbers.indexOf(words[1]);
  if (words.length === 2 && unit > 0 && unit < 10) return String(hundreds + ten * 10 + unit);
}

export function prepareScriptureQuestion(original: string) {
  const question = original.trim();
  const spoken = spokenReference.exec(question);
  if (spoken) {
    const [, name, chapterWords, verseWords] = spoken;
    const chapter = spokenNumber(chapterWords);
    const verse = spokenNumber(verseWords);
    if (chapter && verse) return { lookup: name + ' ' + chapter + ':' + verse };
  }
  const compact = compactReference.exec(question);
  // No chapter in the approved catalog exceeds Psalm 150.
  if (compact && Number(compact[1]) > 150) return { needsChapterAndVerse: true } as const;
  return { lookup: original };
}
