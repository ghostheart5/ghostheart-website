const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROMIUM_EXECUTABLE || undefined
  });
  const context = await browser.newContext({ reducedMotion: 'reduce' });
  await context.route('https://**/*', route => route.fulfill({
    status: 200, contentType: 'text/plain', body: 'External request intercepted during local QA.'
  }));
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  const paths = [
    '/', '/GhostHeart_Story.html', '/woman-behind-the-scenes/',
    '/albums/index.html', '/live/index.html', '/live/my-promise.html',
    '/GhostHeart_Projects.html', '/GhostHeart_Resources.html', '/journal/index.html'
  ];
  for (const width of [390, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const path of paths) {
      const response = await page.goto('http://127.0.0.1:8765' + path, { waitUntil: 'domcontentloaded' });
      assert.equal(response.status(), 200, path);
      assert.equal(await page.locator('h1').count(), 1, path + ' heading');
      const tabs = await page.locator('header.ghx-header nav[aria-label="Main navigation"] a').allTextContents();
      assert.deepEqual(tabs.map(value => value.trim()), ['Home', 'The Awakening', 'Enter My World', 'Music'], path + ' tabs');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, path + ' overflow at ' + width);
      const menu = page.locator('header.ghx-header .ghx-menu-toggle');
      await menu.click();
      assert.equal(await menu.getAttribute('aria-expanded'), 'true', path + ' menu open');
      await page.keyboard.press('Escape');
      assert.equal(await menu.getAttribute('aria-expanded'), 'false', path + ' menu close');
    }
  }
  await page.goto('http://127.0.0.1:8765/GhostHeart_Resources.html');
  assert.equal(await page.locator('.resource:visible').count(), 16);
  await page.locator('[data-filter="start"]').click();
  assert.ok((await page.locator('.resource:visible').count()) < 16);
  await page.locator('[data-filter="all"]').click();
  assert.equal(await page.locator('.resource:visible').count(), 16);
  await page.goto('http://127.0.0.1:8765/albums/index.html');
  assert.equal(await page.locator('audio').count(), 11);
  await page.goto('http://127.0.0.1:8765/GhostHeart_Privacy.html');
  const privacyMenu = page.locator('header.ghx-header .ghx-menu-toggle');
  for (const expected of ['true', 'false', 'true']) {
    await privacyMenu.click();
    assert.equal(await privacyMenu.getAttribute('aria-expanded'), expected, 'Privacy Explore repeated clicks');
  }
  await page.keyboard.press('Escape');
  assert.equal(await privacyMenu.getAttribute('aria-expanded'), 'false');

  // Python's simple server does not use custom 404.html, so serve that exact
  // document at a nested missing URL to exercise browser URL resolution.
  await context.route('http://127.0.0.1:8765/nested/missing/page', route => route.fulfill({
    status: 404, contentType: 'text/html', body: fs.readFileSync('404.html', 'utf8')
  }));
  const missing = await page.goto('http://127.0.0.1:8765/nested/missing/page', { waitUntil: 'load' });
  assert.equal(missing.status(), 404);
  assert.equal(await page.locator('link[href="/assets/shared/ghostheart-world.css"]').count(), 1);
  const missingMenu = page.locator('header.ghx-header .ghx-menu-toggle');
  await missingMenu.click();
  assert.equal(await missingMenu.getAttribute('aria-expanded'), 'true', 'Nested 404 Explore opens');
  await page.locator('a.hero-link').click();
  assert.equal(new URL(page.url()).pathname, '/index.html', 'Nested 404 returns to root Home');
  assert.equal(errors.length, 0, errors.join('\n'));
  await browser.close();
  console.log('PASS browser: key pages, repeated Privacy Explore clicks, nested 404 recovery, Resources filters, 11 audio players');
})().catch(error => { console.error(error); process.exit(1); });
