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
    '/albums/index.html', '/vault/', '/live/index.html', '/live/my-promise.html',
    '/GhostHeart_Projects.html', '/GhostHeart_Resources.html', '/journal/index.html'
  ];
  for (const width of [390, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('http://127.0.0.1:8765/');
    assert.equal(await page.locator('.canon-hero__line').innerText(), 'GhostHeart is the fictional reflection of one man’s real life—told through music, stories, and a mission to help people feel less alone.');
    assert.equal(await page.locator('.canon-hero__note').innerText(), 'Meet the man behind GhostHeart.');
    assert.equal(await page.locator('#home h1').evaluate(element => { const range=document.createRange(); range.selectNodeContents(element); const bounds=range.getBoundingClientRect(); return bounds.x>=0 && bounds.right<=innerWidth; }), true, 'Homepage title is not clipped');
    assert.deepEqual(await page.locator('main > section').evaluateAll(sections => sections.slice(0,4).map(section => section.id)), ['home', 'latest', 'home-story', 'join-the-signal']);
    assert.equal(await page.locator('audio[autoplay], main form').count(), 0);
    const journeyLinks = page.locator('#home .ghx-actions a, #latest .ghx-actions a, #home-story .ghx-actions a, #join-the-signal a');
    for (const link of await journeyLinks.all()) {
      const box = await link.boundingBox();
      assert.ok(box.height >= 44, 'Homepage touch target ' + await link.innerText());
      await link.focus();
      assert.equal(await link.evaluate(element => element.matches(':focus-visible') && parseFloat(getComputedStyle(element).outlineWidth) >= 3), true, 'Visible keyboard focus');
    }
    await page.locator('#home a[href="#latest"]').focus();
    await page.keyboard.press('Enter');
    assert.equal(new URL(page.url()).hash, '#latest');
    await page.locator('#latest a[href="#home-story"]').focus();
    await page.keyboard.press('Enter');
    assert.equal(new URL(page.url()).hash, '#home-story');
    assert.equal(await page.locator('#latest source').getAttribute('src'), '/assets/music/preview/awakening-01-cruel.mp3');
    for (const path of paths) {
      const response = await page.goto('http://127.0.0.1:8765' + path, { waitUntil: 'load' });
      assert.equal(response.status(), 200, path);
      assert.equal(await page.locator('h1').count(), 1, path + ' heading');
      const tabs = await page.locator('header.ghx-header nav[aria-label="Main navigation"] a').allTextContents();
      assert.deepEqual(tabs.map(value => value.trim()), ['Home', 'The Awakening', 'Enter My World', 'Music'], path + ' tabs');
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
      assert.equal(overflow, false, path + ' overflow at ' + width);
      const menu = page.locator('header.ghx-header .ghx-menu-toggle');
      await menu.click();
      assert.equal(await menu.getAttribute('aria-expanded'), 'true', path + ' menu open');
      await page.keyboard.press('Escape');
      assert.equal(await menu.getAttribute('aria-expanded'), 'false', path + ' menu close');
    }
    await page.goto('http://127.0.0.1:8765/vault/');
    const videoFilter = page.locator('[data-vault-filter="videos"]');
    await videoFilter.focus();
    await page.keyboard.press('Enter');
    assert.equal(await videoFilter.getAttribute('aria-pressed'), 'true');
    assert.equal(await page.locator('.vault-item:visible').count(), 6);
    await page.locator('#vault-search').fill('cruel');
    assert.equal(await page.locator('.vault-item:visible').count(), 3);
    const cruel = page.locator('.vault-item[data-vault-kind="videos"]:visible a');
    assert.equal(await cruel.getAttribute('href'), 'https://www.youtube.com/watch?v=9sbFgjM_SDE');
    assert.equal(await cruel.innerText(), 'Watch full video');
    await page.locator('#vault-clear').click();
    assert.equal(await page.locator('.vault-item:visible').count(), 3);
    await page.locator('[data-vault-filter="songs"]').click();
    const songLinks = await page.locator('.vault-item:visible a').evaluateAll(links => links.map(link => link.getAttribute('href')));
    assert.equal(songLinks.length, 11);
    for (const href of songLinks) {
      await page.goto('http://127.0.0.1:8765' + href);
      const target = page.locator(new URL(page.url()).hash);
      assert.equal(await target.count(), 1, href);
      const bounds = await target.boundingBox();
      const headerBounds = await page.locator('header.ghx-header').boundingBox();
      assert.ok(bounds.y >= headerBounds.y + headerBounds.height - 1, href + ' visible below sticky header');
      assert.ok(bounds.y < 900, href + ' fragment in viewport');
      assert.equal(await target.locator('audio').count(), 1);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
    }
    const trailer = page.locator('#track-this-is-ghostheart a');
    assert.equal(await trailer.getAttribute('href'), 'https://www.youtube.com/watch?v=AOCRvtz92JM');
    assert.equal(await trailer.innerText(), 'Watch trailer');
    assert.equal(await trailer.getAttribute('aria-label'), 'Watch trailer: This Is GhostHeart on YouTube');
  }
  await page.goto('http://127.0.0.1:8765/GhostHeart_Resources.html');
  for (const width of [320, 390]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('http://127.0.0.1:8765/GhostHeart_Projects.html');
    assert.equal(await page.locator('h1').evaluate(element => { const range=document.createRange(); range.selectNodeContents(element); const bounds=range.getBoundingClientRect(); return bounds.x>=0 && bounds.right<=innerWidth; }), true, 'Projects title fits ' + width);
    const button = page.locator('.projects-button');
    for (const state of ['normal', 'hover', 'focus']) {
      if (state === 'hover') await button.hover();
      if (state === 'focus') { await page.mouse.move(0,0); await button.focus(); }
      const ratio = await button.evaluate(element => {
        const style=getComputedStyle(element);
        const luminance=value=>value.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
        const a=luminance(style.color),b=luminance(style.backgroundColor);
        return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
      });
      assert.ok(ratio>=4.5, 'Projects button contrast ' + state + ': ' + ratio);
    }
    assert.ok((await button.boundingBox()).height>=44);
    assert.equal(await button.evaluate(e=>e.matches(':focus-visible')&&parseFloat(getComputedStyle(e).outlineWidth)>=3),true);
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
