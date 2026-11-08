// Wake the Heart site (prototype v3, confirmed by Dom Nov 6 2026): the new pages in a real browser, no external requests.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
const PAGES = ['/', '/music/', '/GhostHeart_Videos.html', '/live/', '/GhostHeart_Story.html', '/journal/',
  '/vault/', '/here-to-help/', '/GhostHeart_Projects.html', '/follow/', '/GhostHeart_Resources.html', '/GhostHeart_Privacy.html'];
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE || undefined});
  const context = await browser.newContext({reducedMotion: 'reduce'});
  const mailchimp = [];
  await context.route(/^https:\/\//, route => {
    const req = route.request();
    if (req.url().includes('list-manage.com/subscribe/post')) mailchimp.push(req.postData() || '');
    route.fulfill({status: 200, contentType: 'text/html', body: '<title>external</title>'});
  });
  const errors = [];
  const open = async (path, when, width = 390) => {
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(path + ': ' + e));
    await page.setViewportSize({width, height: 860});
    if (when) await page.clock.install({time: new Date(when)});
    const response = await page.goto(base + path);
    assert.equal(response.status(), 200, path);
    return page;
  };

  // Every page: loads clean, one heading, no sideways scroll on a phone or a laptop, phone menu opens.
  for (const width of [390, 1280]) {
    for (const path of PAGES) {
      const page = await open(path, null, width);
      assert.equal(await page.locator('h1').count(), 1, path);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, path + ' overflow at ' + width);
      if (width === 390) {
        await page.click('#menu-btn');
        assert.equal(await page.getAttribute('#menu-btn', 'aria-expanded'), 'true', path + ' menu');
      }
      await page.close();
    }
  }

  // Before week one goes up and after. Dom, Nov 8 2026: Week 1 premieres Monday Nov 9 at 12 PM Central
  // (apply_week1_premiere.py); later weeks open Sunday 7 PM Central. No song plays before its week opens,
  // Week 1 plays the title song The Heart Wakes and the week song To Those Who Served.
  let page = await open('/', '2026-11-07T18:00:00Z');
  assert.match(await page.locator('#featured-home').innerText(), /Premieres Monday at 12 PM Central/i);
  assert.match(await page.locator('#featured-home h3').innerText(), /To Those Who Served/i);
  assert.equal(await page.locator('#featured-home audio').count(), 0, 'nothing plays before the premiere');
  await page.close();
  // Sun Nov 8, 7 PM CST (01:00Z Nov 9) is no longer the opening for Week 1.
  page = await open('/', '2026-11-09T01:00:00Z');
  assert.match(await page.locator('#featured-home').innerText(), /Premieres Monday at 12 PM Central/i);
  assert.equal(await page.locator('#featured-home audio').count(), 0);
  await page.close();
  // Mon Nov 9, 11:59 AM CST = 17:59Z; 12:00 PM CST = 18:00Z.
  page = await open('/', '2026-11-09T17:59:00Z');
  assert.match(await page.locator('#featured-home').innerText(), /Premieres Monday/i);
  await page.close();
  page = await open('/', '2026-11-09T18:00:00Z');
  assert.match(await page.locator('#featured-home').innerText(), /Out now/i);
  assert.equal(await page.locator('#featured-home audio').count(), 2);
  assert.match(await page.locator('#featured-home .songlist').innerText(), /The Heart Wakes[\s\S]*To Those Who Served/);
  assert.ok((await page.locator('[data-daily-quote]').innerText()).length > 10, 'daily line');
  await page.close();
  page = await open('/', '2026-11-15T15:00:00Z');
  assert.match(await page.locator('#featured-home h3').innerText(), /To Those Who Served/i, 'week 2 waits until 7 PM');
  await page.close();
  page = await open('/wake-the-heart/');
  await page.waitForURL(/\/music\/$/);
  await page.close();

  // Lives: Sundays only, from the next one.
  page = await open('/live/', '2026-11-07T18:00:00Z');
  assert.equal(await page.locator('#lives li').count(), 14);
  assert.match(await page.locator('#lives li').first().innerText(), /Sun, Nov 8/i);
  assert.match(await page.locator('.nl-big .js-nl-topic').innerText(), /Lessons Learned/i);
  await page.close();
  page = await open('/live/', '2026-11-20T18:00:00Z');
  assert.match(await page.locator('#lives li').first().innerText(), /Sun, Nov 22/i);
  await page.close();

  // Notebook: filters and deep links.
  page = await open('/journal/#e-cruel');
  assert.equal(await page.locator('#e-cruel details').evaluate(d => d.open), true);
  await page.click('.nb-chips .chip[data-nb="passage"]');
  assert.equal(await page.locator('.nb-item:visible').count(), await page.locator('.nb-item[data-typ="passage"]').count());
  await page.close();

  // Heart Dial: a feeling gives one pick with a working link on this site or outside it.
  page = await open('/vault/');
  await page.click('.dial-m[data-m="strength"]');
  await page.locator('.dial-out a.btn').waitFor();
  const href = await page.locator('.dial-out a.btn').getAttribute('href');
  assert.ok(/^https:\/\//.test(href) || PAGES.includes(href.split('#')[0]), href);
  await page.close();

  // Old deep links still land on the right card.
  for (const [path, id] of [['/music/#song-cruel', 'song-cruel'], ['/GhostHeart_Videos.html#film-rebellion', 'film-rebellion'],
                            ['/GhostHeart_Story.html#behind-the-scars', 'behind-the-scars']]) {
    page = await open(path);
    assert.equal(await page.locator('#' + id).count(), 1, path);
    await page.close();
  }

  // Silver Thread: posts the email straight to Mailchimp.
  page = await open('/');
  await page.fill('#t-email', 'fan@example.com');
  await Promise.all([page.waitForURL(/list-manage\.com/), page.click('#thread form.js-thread button[type=submit]')]);
  assert.ok(mailchimp.some(body => body.includes('EMAIL=fan%40example.com')), 'Mailchimp got the email');
  await page.close();

  assert.deepEqual(errors, []);
  await browser.close();
  console.log('PASS site browser: 12 pages, no campaign page at phone and laptop width, weeks, Lives, Notebook, Heart Dial, old links, Mailchimp signup.');
})().catch(e => { console.error(e); process.exit(1); });
