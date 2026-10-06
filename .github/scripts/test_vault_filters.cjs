const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const rootDir = path.resolve(__dirname, '../..');
const html = fs.readFileSync(path.join(rootDir, 'vault/index.html'), 'utf8');
const cards = [...html.matchAll(/<article class="vault-item" data-vault-kind="([^"]+)" data-vault-featured="([^"]+)" data-vault-search="([^"]+)"([^>]*)>/g)]
  .map((match) => ({
    dataset: { vaultKind: match[1], vaultFeatured: match[2], vaultSearch: match[3] },
    hidden: match[4].includes(' hidden'),
  }));
assert.equal(cards.length, 38);

function element(dataset = {}) {
  return {
    dataset, handlers: {}, value: '', hidden: false, textContent: '', attrs: {},
    addEventListener(name, handler) { this.handlers[name] = handler; },
    setAttribute(name, value) { this.attrs[name] = value; },
    focus() {},
  };
}
const names = ['featured', 'songs', 'videos', 'shorts', 'quotes', 'all'];
const buttons = names.map((name) => element({ vaultFilter: name }));
const input = element();
const clear = element();
const count = element();
const empty = element();
const selectors = {
  '#vault-search': input, '#vault-clear': clear, '#vault-count': count, '#vault-empty': empty,
};
const root = {
  querySelectorAll(selector) { return selector === '[data-vault-filter]' ? buttons : cards; },
  querySelector(selector) { return selectors[selector]; },
};
const script = fs.readFileSync(path.join(rootDir, 'assets/vault/vault.js'), 'utf8');
vm.runInNewContext(script, { document: { querySelector() { return root; } } });
assert.equal(cards.filter((card) => !card.hidden).length, 3);
for (const [kind, expected] of [['songs', 11], ['videos', 5], ['shorts', 5], ['quotes', 17], ['all', 38]]) {
  buttons.find((button) => button.dataset.vaultFilter === kind).handlers.click();
  assert.equal(cards.filter((card) => !card.hidden).length, expected, kind);
  assert.equal(buttons.find((button) => button.dataset.vaultFilter === kind).attrs['aria-pressed'], 'true');
}
input.value = 'cruel';
input.handlers.input();
assert.ok(cards.filter((card) => !card.hidden).length >= 2);
input.value = 'zzzz-no-match';
input.handlers.input();
assert.equal(cards.filter((card) => !card.hidden).length, 0);
assert.equal(empty.hidden, false);
clear.handlers.click();
assert.equal(cards.filter((card) => !card.hidden).length, 3);
console.log('PASS Vault filters: 38 scoped items, category counts, search, empty state, clear');
