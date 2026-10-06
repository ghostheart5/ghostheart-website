const { chromium } = require('playwright');
const assert = require('node:assert/strict');

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
    '/', '/GhostHeart_Story.html', '/GhostHeart_Angel.html',
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
      assert.deepEqual(tabs.map(value => value.trim()), ['Awakening', 'Music', 'Readings', 'Projects'], path + ' tabs');
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
  assert.equal(errors.length, 0, errors.join('\n'));
  await browser.close();
  console.log('PASS browser: 9 key pages at mobile and desktop widths, navigation, Resources filters, 11 audio players');
})().catch(error => { console.error(error); process.exit(1); });
