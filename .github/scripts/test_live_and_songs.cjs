// Site audit 2026-11-01: home song links land on their own song; home and Lives page show the same next Live.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || undefined});
  const context = await browser.newContext({reducedMotion:'reduce', viewport:{width:390,height:844}});
  await context.route('https://**/*', route => route.abort());
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));

  await page.goto(base + '/');
  const songs = await page.locator('#latest .tracks a').evaluateAll(links => links.map(a => [a.getAttribute('href'), a.textContent.replace(/\s+/g, ' ').trim()]));
  assert.equal(songs.length, 3);
  for (const [href, label] of songs) {
    assert.match(href, /^\/music\/#song-[a-z0-9-]+$/, label);
    await page.goto(base + '/');
    await Promise.all([page.waitForURL('**' + href), page.locator(`#latest .tracks a[href="${href}"]`).click()]);
    const song = page.locator(href.slice(href.indexOf('#')));
    assert.equal(await song.count(), 1, href + ' exists');
    assert.ok(label.includes(await song.locator('button').getAttribute('data-title')), label + ' matches the Music page title');
    await page.waitForFunction(id => document.activeElement === document.querySelector(id + ' button'), href.slice(href.indexOf('#')), {timeout: 5000});
    assert.ok(await song.evaluate(e => { const r = e.getBoundingClientRect(); return r.top >= 0 && r.top < innerHeight; }), href + ' in view');
  }

  // Same next Live on both pages, before, between and after the listed Lives.
  for (const time of ['2026-10-31T12:00:00Z', '2026-11-01T17:00:00Z', '2026-11-08T17:00:00Z', '2026-11-20T12:00:00Z']) {
    const timed = await context.newPage();
    await timed.clock.install({time: new Date(time)});
    await timed.goto(base + '/live/');
    const onLives = (await timed.locator('#live-status-title [data-live-slot-label]').textContent()).trim();
    await timed.goto(base + '/');
    const onHome = (await timed.locator('#mission-board [data-live-slot-label]').textContent()).trim();
    assert.equal(onHome, onLives, time);
    await timed.close();
  }
  assert.deepEqual(errors, []);
  await browser.close();
  console.log('PASS live and songs: 3 home song links land on their own song; home and Lives page agree on the next Live at 4 times.');
})().catch(e => { console.error(e); process.exit(1); });
