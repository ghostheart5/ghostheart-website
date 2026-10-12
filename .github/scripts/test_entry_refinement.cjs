const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8772';
const evidence = process.env.GHOSTHEART_TEST_EVIDENCE_DIR;
const promise = 'New songs, the stories behind them, and the next GhostHeart chapter\u2014sent when they\u2019re ready.';

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROMIUM_EXECUTABLE || undefined });
  try {
    const context = await browser.newContext({ reducedMotion: 'reduce' });
    await context.route('https://**/*', route => route.abort());
    const page = await context.newPage();
    const errors = [];
    const missing = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('response', response => {
      if (response.url().startsWith(base) && response.status() >= 400) missing.push(response.url());
    });
    const measurements = [];
    for (const [width, height] of [[320,740], [390,844], [768,1024], [1440,900], [1920,1080]]) {
      await page.setViewportSize({ width, height });
      await page.goto(base + '/', { waitUntil: 'networkidle' });
      assert.equal((await page.locator('#join-the-signal h2').textContent()).trim(), 'Stay with the story.');
      assert.equal(await page.locator('#join-the-signal h2 + p').innerText(), promise);
      assert.equal(await page.locator('#home a').filter({ hasText: 'Experience Cruel' }).count(), 1);
      const layout = await page.evaluate(() => {
        const hero = document.querySelector('#home').getBoundingClientRect();
        const range = document.createRange();
        range.selectNodeContents(document.querySelector('#home h1'));
        const title = range.getBoundingClientRect();
        return { overflow: document.documentElement.scrollWidth > innerWidth + 1,
          titleFits: title.left >= 0 && title.right <= innerWidth,
          nextVisible: hero.bottom < innerHeight, heroBottom: hero.bottom,
          loadMs: performance.getEntriesByType('navigation')[0].loadEventEnd };
      });
      assert.equal(layout.overflow, false, 'Homepage overflow at ' + width);
      assert.equal(layout.titleFits, true, 'Title bounds at ' + width);
      assert.equal(layout.nextVisible, true, 'Next section visible at ' + width);
      measurements.push({ width, height, ...layout });
      if (evidence) await page.screenshot({ path: path.join(evidence, 'home-' + width + '.png'), fullPage: false });
    }
    await page.goto(base + '/follow/index.html');
    assert.equal((await page.locator('#email-signup-title').textContent()).trim(), 'Stay with the story.');
    assert.equal(await page.locator('#email-signup-title + p').innerText(), promise);
    const form = page.locator('form');
    assert.equal(await form.getAttribute('method'), 'post');
    assert.equal(await form.getAttribute('action'), 'https://myghostheart.us22.list-manage.com/subscribe/post?u=a7ab330423f3b936c48b8d8ba&id=880e8056a6&f_id=00bec2e1f0');
    assert.equal(await page.locator('label[for="follow-email"]').count(), 1);
    const email = page.locator('#follow-email');
    assert.equal(await email.evaluate(element => element.checkValidity()), false);
    await email.fill('not-an-email');
    assert.equal(await email.evaluate(element => element.checkValidity()), false);
    await email.fill('local-test@example.invalid');
    assert.equal(await email.evaluate(element => element.checkValidity()), true);
    assert.equal(await page.locator('.g-honeypot input').getAttribute('tabindex'), '-1');
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, 'Follow mobile overflow');
    if (evidence) await page.screenshot({ path: path.join(evidence, 'follow-390.png'), fullPage: true });
    // Never submit: provider delivery and unsubscribe behavior require separate approval.
    for (const slug of ['broken-man', 'the-ones-we-carry']) {
      await page.goto(base + '/albums/' + slug + '/index.html');
      const returns = page.getByRole('link', { name: 'Back to the song list', exact: true });
      assert.ok(await returns.count() > 0, slug + ' return links');
      for (const link of await returns.all()) assert.equal(await link.getAttribute('href'), '#tracks');
      await returns.first().focus();
      await page.keyboard.press('Enter');
      assert.equal(new URL(page.url()).hash, '#tracks');
      const tracks = await page.locator('#tracks').boundingBox();
      assert.ok(tracks.y >= 0 && tracks.y < 844, slug + ' target visible');
      const film = page.locator('.g-film').first();
      await film.locator('[data-video-id]').click();
      assert.equal(await film.locator('iframe').count(), 1, slug + ' player created');
      await film.locator('.g-close').click();
      assert.equal(await film.locator('iframe').count(), 0, slug + ' player closed');
      assert.equal(await film.locator('[data-video-id]').evaluate(element => element === document.activeElement), true, slug + ' focus restored');
    }
    await page.goto(base + '/');
    const media = await page.locator('#latest audio').evaluate(async audio => {
      audio.muted = true;
      audio.load();
      if (audio.readyState < 1) await new Promise((resolve, reject) => {
        audio.addEventListener('loadedmetadata', resolve, { once: true });
        audio.addEventListener('error', () => reject(new Error('Preview decode failed')), { once: true });
      });
      await audio.play();
      await new Promise(resolve => setTimeout(resolve, 300));
      audio.pause();
      return { duration: audio.duration, currentTime: audio.currentTime, controls: audio.controls };
    });
    assert.ok(media.duration > 0 && media.currentTime > 0 && media.controls, 'Local preview playback');
    assert.deepEqual(errors, [], 'Browser JavaScript errors');
    assert.deepEqual(missing, [], 'Local missing resources');
    const report = { status: 'PASS', measurements, media, signupSubmitted: false, externalRequestsBlocked: true,
      limits: ['Local timing only, not hosted performance', 'No email delivery or unsubscribe test', 'Muted preview playback, not a full listening review'] };
    if (evidence) fs.writeFileSync(path.join(evidence, 'browser-results.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
