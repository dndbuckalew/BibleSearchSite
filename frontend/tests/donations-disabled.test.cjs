/* eslint-disable @typescript-eslint/no-require-imports -- Node test harness matches existing tests. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const app = path.join(__dirname, '../app');
function load(file, mocks = {}) {
  const filename = path.resolve(app, file);
  const source = fs.readFileSync(filename, 'utf8');
  const exports = {};
  const output = ts.transpileModule(source, { compilerOptions: {
    module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX,
    target: ts.ScriptTarget.ES2020, esModuleInterop: true,
  }}).outputText;
  vm.runInNewContext(output, { exports, require(name) {
    if (name in mocks) return mocks[name];
    if (name.startsWith('.')) return load(path.relative(app, path.resolve(path.dirname(filename), name)) + (fs.existsSync(path.resolve(path.dirname(filename), name) + '.ts') ? '.ts' : '.tsx'), mocks);
    return require(name);
  }});
  return exports;
}
test('shared navigation omits donations and retains Stay Connected', () => {
  const nav = load('platform/navigation/navigation_configuration.ts');
  assert.equal(nav.primaryNavigation.some(item => item.href === '/donation'), false);
  assert.equal(nav.primaryNavigation.find(item => item.href === '/stay-connected').display, true);
});
