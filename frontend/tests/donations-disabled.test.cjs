/* eslint-disable @typescript-eslint/no-require-imports -- Node test harness matches existing tests. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
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
const flag = load('platform/capabilities.ts');
test('release capability is disabled and shared navigation retains Stay Connected', () => {
  assert.equal(flag.DONATIONS_ENABLED, false);
  const nav = load('platform/navigation/navigation_configuration.ts');
  assert.equal(nav.primaryNavigation.find(i => i.href === '/donation').display, false);
  assert.equal(nav.primaryNavigation.find(i => i.href === '/stay-connected').display, true);
});
test('donation components render no containers, controls, dialog or children', () => {
  for (const name of ['DonationPrompt', 'ResultsDonationInvitation']) {
    const Component = load(`components/donation/${name}.tsx`, { 'next/link': () => null }).default;
    assert.equal(renderToStaticMarkup(React.createElement(Component, { onDismiss() {} }, 'donation child')), '');
  }
});
test('direct donation route redirects before rendering preserved payment content', () => {
  const Page = load('donation/page.tsx', {
    'next/navigation': { redirect(url) { assert.equal(url, '/'); throw new Error('redirected'); } },
    'next/link': () => null,
    '../components/WorkspaceHome': () => null,
  }).default;
  assert.throws(() => Page(), /redirected/);
});
test('independently invoked confirmation and checkout handlers perform no work', async () => {
  const source = fs.readFileSync(path.join(app, 'components/donation/DonationPrompt.tsx'), 'utf8');
  const tree = ts.createSourceFile('DonationPrompt.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  const handlers = [];
  function visit(node) {
    if (ts.isFunctionDeclaration(node) && ['showConfirmation', 'continueToStripe'].includes(node.name?.text)) handlers.push(node);
    ts.forEachChild(node, visit);
  }
  visit(tree);
  assert.equal(handlers.length, 2);
  for (const handler of handlers) {
    const output = ts.transpileModule(handler.getText(tree), { compilerOptions: { target: ts.ScriptTarget.ES2020 } }).outputText;
    // Any state access, browser launch, identifier generation or request fails in this empty context.
    const run = vm.runInNewContext(`${output}\n${handler.name.text}`, flag);
    await run();
  }
});
