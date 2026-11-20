const assert = require('node:assert/strict');
const {test} = require('node:test');
const {prepareScriptureQuestion: prepare} = require('../app/lib/prepareScriptureQuestion.ts');

test('spoken Scripture formatting preserves explicit boundaries', () => {
  for (const [input, expected] of [
    ['John, chapter 3, verse 16.', 'John 3:16'],
    ['John chapter three verse sixteen', 'John 3:16'],
    ['JOHN CHAPTER THREE, VERSE THIRTY-SIX!', 'JOHN 3:36'],
    ['1 John chapter four verse seven', '1 John 4:7'],
    ['Psalm chapter one hundred and nineteen verse one hundred seventy-six', 'Psalm 119:176'],
  ]) assert.deepEqual(prepare(input), {lookup: expected});
});

test('compact numbers require clarification while existing input passes through', () => {
  assert.deepEqual(prepare('John 316'), {needsChapterAndVerse: true});
  for (const input of ['John 3:16','1 John 4:7','Psalm 150','What does John say about love?','What happened in 2020?']) {
    assert.deepEqual(prepare(input), {lookup: input});
  }
});
