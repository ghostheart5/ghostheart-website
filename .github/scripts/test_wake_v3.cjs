// Wake the Heart site (prototype v3, confirmed by Dom Nov 6 2026): the new pages in a real browser, no external requests.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
const PAGES = ['/', '/wake-the-heart/', '/music/', '/GhostHeart_Videos.html', '/live/', '/GhostHeart_Story.html', '/journal/',
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
      if (width === 390 && path !== '/') {  // the Protected by GhostHeart home keeps its menu in one sliding row
        await page.click('#menu-btn');
        assert.equal(await page.getAttribute('#menu-btn', 'aria-expanded'), 'true', path + ' menu');
      }
      await page.close();
    }
  }

  // Home (Dom, Nov 11 2026): Protected by GhostHeart (apply_protector_home.py). Featured week is To Those Who
  // Served in steel and crimson; the full song is on YouTube only; the Vault, About, Live and Merch open on the page.
  let page = await open('/', '2026-11-11T18:00:00Z');
  assert.match(await page.locator('.feat2:visible .deck h3').innerText(), /To Those Who Served/i);
  assert.equal(await page.locator('.feat2:visible a[href="https://www.youtube.com/watch?v=U0X6SwISG_M"]').count(), 1);
  assert.ok((await page.locator('#q-text').innerText()).length > 10, 'daily line');
  assert.equal(await page.locator('#v-vault').isVisible(), false);
  await page.click('header.top a[href="#vault"]');
  await page.locator('#v-vault').waitFor();
  assert.equal(await page.locator('#albums .trk').count(), 2, 'only The Heart Wakes songs');
  await page.click('header.top a[href="#live"]');
  await page.fill('#fire-in', 'old weight');
  await page.press('#fire-in', 'Enter');
  assert.equal(await page.locator('#said').innerText(), 'old weight');
  await page.click('header.top a[href="#merch"]');
  assert.equal(await page.locator('#v-merch .m-card').count(), 5);
  assert.equal(await page.locator('header.top a[href="/here-to-help/"]').count(), 1);
  await page.close();
  // Week 2 (Dom, Nov 14 2026, apply_week2_home.py): The Parts You Hide takes over at 7 PM Central on Sunday, Nov 15.
  for (const [when, title] of [['2026-11-16T00:59:00Z', /To Those Who Served/i], ['2026-11-16T01:00:00Z', /The Parts You Hide/i],
                               ['2026-11-18T18:00:00Z', /The Parts You Hide/i]]) {
    page = await open('/', when);
    assert.equal(await page.locator('.feat2:visible').count(), 1, when);
    assert.match(await page.locator('.feat2:visible .deck h3').innerText(), title, when);
    await page.close();
  }
  page = await open('/#thread');
  assert.equal(await page.locator('#v-home').isVisible(), true, 'old /#thread links land on the home page');
  await page.close();
  // The Music page's album list follows the same opening time.
  page = await open('/music/', '2026-11-09T17:59:00Z');
  assert.equal(await page.locator('#album-songs audio').count(), 0, 'Music page waits for the premiere');
  await page.close();
  page = await open('/music/', '2026-11-09T18:00:00Z');
  assert.equal(await page.locator('#album-songs audio').count(), 2);
  await page.close();
  // Dom, Nov 8 2026: the campaign page is on again (confirmed prototype).
  page = await open('/wake-the-heart/');
  assert.match(await page.locator('h1').innerText(), /Wake the\s*Heart/i);
  assert.equal(new URL(page.url()).pathname, '/wake-the-heart/');
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

  // Blog: Dom, Nov 8 2026: older songs off everywhere; the Blog waits for The Heart Wakes notes,
  // and an old song note forwards to it.
  page = await open('/journal/');
  assert.equal(await page.locator('.nb-item').count(), 0);
  assert.match(await page.locator('.nb-empty').innerText(), /The Heart Wakes/);
  await page.close();
  page = await open('/journal/cruel-something-needs-to-change.html');
  await page.waitForURL(/\/journal\/$/);
  await page.close();

  // Heart Dial: a feeling gives one pick with a working link on this site or outside it.
  page = await open('/vault/');
  await page.click('.dial-m[data-m="strength"]');
  await page.locator('.dial-out a.btn').waitFor();
  const href = await page.locator('.dial-out a.btn').getAttribute('href');
  assert.ok(/^https:\/\//.test(href) || PAGES.includes(href.split('#')[0]), href);
  await page.close();

  // Old deep links still land on the right card.
  // Dom, Nov 8 2026: older songs left Music, so /music/#song-cruel just opens Music.
  for (const [path, id] of [['/music/#song-cruel', 'album-songs'], ['/GhostHeart_Videos.html#film-rebellion', 'film-the-heart-wakes'],
                            ['/GhostHeart_Story.html#behind-the-scars', 'behind-the-scars']]) {
    page = await open(path);
    assert.equal(await page.locator('#' + id).count(), 1, path);
    await page.close();
  }

  // Silver Thread: posts the email straight to Mailchimp.
  page = await open('/');
  await page.fill('#join-email', 'fan@example.com');
  await Promise.all([page.waitForURL(/list-manage\.com/), page.click('#thread form.js-thread button[type=submit]')]);
  assert.ok(mailchimp.some(body => body.includes('EMAIL=fan%40example.com')), 'Mailchimp got the email');
  await page.close();

  assert.deepEqual(errors, []);
  await browser.close();
  console.log('PASS site browser: 13 pages, campaign page on, at phone and laptop width, weeks, Lives, Notebook, Heart Dial, old links, Films and Blog with only The Heart Wakes, Mailchimp signup.');
})().catch(e => { console.error(e); process.exit(1); });
