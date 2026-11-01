// Check back in + "For how you feel" (site audit 2026-11-01, owner yes). Everything stays in the browser.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
const ROOT = path.resolve(__dirname, '../..');
const KEY = 'gh-check-back-in';

(async () => {
  // Every pick in the curated list points at a real page and anchor.
  global.window = {};
  require(path.join(ROOT, 'assets/data/for-you.js'));
  const cat = window.GHOSTHEART_FOR_YOU;
  const moods = cat.moods.map(m => m[0]);
  for (const p of cat.picks) {
    assert.ok(p.moods.length && p.moods.every(m => moods.includes(m)), p.id + ' moods');
    assert.ok(['line', 'watch', 'listen', 'read'].includes(p.how), p.id + ' how');
    if (/^https:\/\/www\.youtube\.com\/shorts\/[\w-]+$/.test(p.href)) continue;
    const [file, anchor] = p.href.split('#');
    const local = path.join(ROOT, file.endsWith('/') ? file + 'index.html' : file);
    assert.ok(fs.existsSync(local), p.id + ' page ' + file);
    if (anchor) assert.ok(fs.readFileSync(local, 'utf8').includes(`id="${anchor}"`), p.id + ' anchor #' + anchor);
  }
  for (const m of moods) assert.ok(cat.picks.some(p => p.moods.includes(m)), 'mood ' + m + ' has picks');

  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE || undefined});
  const context = await browser.newContext({reducedMotion: 'reduce', viewport: {width: 390, height: 844}});
  await context.route('https://**/*', route => route.abort());
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  const state = () => page.evaluate(k => JSON.parse(localStorage.getItem(k) || 'null'), KEY);

  // First visit: nothing to check back in to.
  await page.goto(base + '/');
  assert.equal(await page.locator('#check-back-in').isHidden(), true);

  // Vault: the picker gives one piece with its reason; honest when a format has nothing.
  await page.goto(base + '/vault/');
  assert.equal(await page.locator('#for-you').isVisible(), true);
  assert.equal(await page.locator('article.vault-item .gh-save').count(), await page.locator('article.vault-item').count());
  await page.locator('#for-you label:has-text("I feel judged")').click();
  await page.locator('#for-you label:has-text("Watch")').click();
  await page.locator('#for-you .fy-go').click();
  const first = await page.locator('#for-you .fy-title').innerText();
  assert.ok(first.length > 0);
  assert.equal(await page.locator('#for-you .fy-title').evaluate(e => e === document.activeElement), true);
  await page.locator('#for-you .fy-again').click();
  assert.notEqual(await page.locator('#for-you .fy-title').innerText(), first, 'Try another changes the pick');
  await page.locator('#for-you .fy-actions .gh-save').click();
  assert.equal(await page.locator('#for-you .fy-actions .gh-save').getAttribute('aria-pressed'), 'true');
  // "Read" + "I'm thinking about love" has one exact pick; "Listen" + "I want to feel less alone" too. Pick a gap:
  const gap = cat.moods.map(m => m[0]).flatMap(m => cat.how.map(h => [m, h[0]])).find(([m, h]) => !cat.picks.some(p => p.moods.includes(m) && p.how === h));
  if (gap) {
    await page.locator(`#for-you input[name=mood][value="${gap[0]}"]`).check({force: true});
    await page.locator(`#for-you input[name=how][value="${gap[1]}"]`).check({force: true});
    await page.locator('#for-you .fy-go').click();
    assert.match(await page.locator('#for-you .fy-honest').innerText(), /^Nothing to .+ for that yet\./);
  }

  // Music: save a song; a stored position offers to pick it up.
  await page.goto(base + '/music/');
  assert.equal(await page.locator('.tracks li[id^="song-"] .gh-save').count(), 11);
  await page.locator('#song-she-got-to-me .gh-save').click();
  assert.equal(await page.locator('#song-she-got-to-me .gh-save').getAttribute('aria-pressed'), 'true');
  await page.evaluate(k => { const d = JSON.parse(localStorage.getItem(k)); d.song = {id: 'song-cruel', title: 'Cruel', time: 72, at: Date.now()}; localStorage.setItem(k, JSON.stringify(d)); }, KEY);
  await page.goto(base + '/music/?resume=1#song-cruel');
  assert.match(await page.locator('.gh-resume').innerText(), /Pick up where you left off: Cruel at 1:12\./);
  await page.waitForFunction(() => document.activeElement && document.activeElement.matches('.gh-resume-go'), null, {timeout: 5000});

  // Reading: a stored place offers to continue.
  await page.evaluate(k => { const d = JSON.parse(localStorage.getItem(k)); d.read = {href: '/passages/im-not.html', title: 'I’m Not', pct: 0.4, at: Date.now()}; localStorage.setItem(k, JSON.stringify(d)); }, KEY);
  await page.goto(base + '/passages/im-not.html');
  assert.match(await page.locator('.gh-resume-read').innerText(), /You stopped about 40% of the way through\./);

  // Home: the panel lists the song to pick up, the reading, what's new and the saved items.
  // Last visit long ago: the home page treats this as a new visit and lists what was published since.
  await page.evaluate(k => { const d = JSON.parse(localStorage.getItem(k)); d.last = Date.parse('2026-10-02T00:00:00Z'); localStorage.setItem(k, JSON.stringify(d)); }, KEY);
  await page.goto(base + '/');
  const panel = page.locator('#check-back-in');
  await panel.locator('li:has-text("New since your last visit")').first().waitFor({timeout: 5000});
  const text = await panel.innerText();
  assert.match(text, /Pick up at 1:12\s+Cruel/i);
  assert.match(text, /Continue reading\s+I’m Not/i);
  assert.match(text, /Saved song\s+She Got to Me/i);
  assert.equal(await panel.locator('a[href="/music/?resume=1#song-cruel"]').count(), 1);
  for (const target of await panel.locator('a, button').all()) assert.ok((await target.boundingBox()).height >= 40, 'touch target');
  const before = await panel.locator('li').count();
  await panel.locator('li:has-text("She Got to Me") .gh-remove').click();
  assert.equal(await panel.locator('li').count(), before - 1);
  assert.equal((await state()).saved.some(s => s.id === 'song-she-got-to-me'), false);
  await panel.locator('[data-checkin-forget]').click();
  assert.equal(await panel.isHidden(), true);
  const cleared = await state();
  assert.deepEqual([cleared.saved.length, cleared.song, cleared.read], [0, null, null]);
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'no sideways scroll');

  // Blocked storage: pages work, the feature stays out of the way.
  const blocked = await browser.newContext({reducedMotion: 'reduce'});
  await blocked.route('https://**/*', route => route.abort());
  await blocked.addInitScript(() => { Object.defineProperty(window, 'localStorage', {get() { throw new DOMException('blocked', 'SecurityError'); }}); });
  const b = await blocked.newPage();
  b.on('pageerror', e => errors.push('blocked: ' + e));
  for (const route of ['/', '/music/', '/passages/im-not.html', '/vault/']) { await b.goto(base + route); assert.equal(await b.locator('.gh-save, .gh-resume').count(), 0, route); }
  await b.locator('#for-you .fy-go').click();
  assert.ok((await b.locator('#for-you .fy-title').innerText()).length > 0, 'picker works without storage');

  assert.deepEqual(errors, []);
  await browser.close();
  console.log(`PASS check back in: ${cat.picks.length} curated picks resolve; picker, Try another, honest gap, Save; song pick-up, reading pick-up, what's new, remove, forget; blocked storage.`);
})().catch(e => { console.error(e); process.exit(1); });
