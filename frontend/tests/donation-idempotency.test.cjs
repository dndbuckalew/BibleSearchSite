const { test } = require('node:test');
const assert = require('node:assert/strict');
const { webcrypto } = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const source = fs.readFileSync(path.join(__dirname, '../app/components/donation/idempotency.ts'), 'utf8');
const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const exportsObject = {};
vm.runInNewContext(output, { exports: exportsObject, Uint8Array });
const generate = exportsObject.createDonationIdempotencyKey;
const pattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

test('uses native randomUUID when available', () => {
  let calls = 0;
  const id = webcrypto.randomUUID();
  assert.equal(generate({ randomUUID() { calls++; return id; } }), id);
  assert.equal(calls, 1);
});

test('fallback uses cryptographic bytes with correct version/variant bits', () => {
  let calls = 0;
  const id = generate({ getRandomValues(bytes) { calls++; bytes.fill(255); return bytes; } });
  assert.equal(id, 'ffffffff-ffff-4fff-bfff-ffffffffffff');
  assert.equal(calls, 1);
});

test('fallback uses real Web Crypto and generates valid varied UUID v4 values', () => {
  const api = { getRandomValues: bytes => webcrypto.getRandomValues(bytes) };
  const values = Array.from({ length: 100 }, () => generate(api));
  assert(values.every(id => pattern.test(id)));
  assert.equal(new Set(values).size, 100);
});

test('fails closed when cryptographic randomness is absent', () => {
  assert.throws(() => generate({}), /Secure donation identifier/);
  assert.throws(() => generate(null), /Secure donation identifier/);
});
