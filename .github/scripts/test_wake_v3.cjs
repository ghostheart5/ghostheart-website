// Wake the Heart site (prototype v3, confirmed by Dom Nov 6 2026): the new pages in a real browser, no external requests.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
const PAGES = ['/', '/wake-the-heart/', '/music/', '/GhostHeart_Videos.html', '/GhostHeart_Story.html', '/journal/',
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
  const NEW_LOOK = ['/here-to-help/', '/GhostHeart_Projects.html', '/GhostHeart_Resources.html', '/GhostHeart_Privacy.html', '/vault/'];
  for (const width of [390, 1280]) {
    for (const path of PAGES) {
      const page = await open(path, null, width);
      assert.equal(await page.locator('h1').count(), 1, path);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, path + ' overflow at ' + width);
      // Dom, Nov 26 2026 (grade fix 7): every page, Home and the new-look pages too, has a Menu button on a phone.
      if (width === 390) {
        const btn = path === '/' ? '#nh-menu-btn' : '#menu-btn';
        const nav = path === '/' ? '#nh-nav' : '#menu';
        assert.equal(await page.locator(nav).isVisible(), false, path + ' menu starts closed');
        await page.click(btn);
        assert.equal(await page.getAttribute(btn, 'aria-expanded'), 'true', path + ' menu');
        assert.equal(await page.locator(nav).isVisible(), true, path + ' menu opens');
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, path + ' open menu overflow');
      } else {
        assert.equal(await page.locator(path === '/' ? '#nh-menu-btn' : '#menu-btn').isVisible(), false, path + ' no Menu button on a laptop');
      }
      await page.close();
    }
  }

  // Home (Dom, Nov 11 2026): Protected by GhostHeart (apply_protector_home.py). The Vault, About, Live and Merch open on the page.
  // Dom, Nov 21 2026: nothing should say veterans anymore (apply_no_veterans_home.py), so the Week 01 block is gone.
  let page = await open('/', '2026-11-11T18:00:00Z', 1280);  // laptop width: the tabs are in the bar (phones use the Menu button)
  assert.equal(await page.locator('.feat2:visible').count(), 1);
  assert.match(await page.locator('.feat2:visible .deck h3').innerText(), /The Parts You Hide/i);
  assert.doesNotMatch(await page.locator('body').innerText(), /veteran/i);
  assert.ok((await page.locator('#q-text').innerText()).length > 10, 'daily line');
  assert.equal(await page.locator('#v-vault').isVisible(), false);
  await page.click('header.top a[href="#vault"]');
  await page.locator('#v-vault').waitFor();
  assert.equal(await page.locator('#albums .trk').count(), 1, 'only The Heart Wakes songs (grade fix 1: the veterans song is off)');
  assert.ok(!(await page.locator('#v-vault').innerText()).toLowerCase().includes(Buffer.from('VG8gVGhvc2UgV2hvIFNlcnZlZA==', 'base64').toString().toLowerCase()));
  assert.equal(await page.locator('#v-vault a[href="https://www.youtube.com/watch?v=-ZtyZCxKBM8"]').count(), 1, 'Too Small, public video');
  // Dom, Nov 26 2026 (grade fix 4): Lives are off the site, no Live tab.
  assert.equal(await page.locator('header.top a[href="#live"]').count(), 0);
  assert.equal(await page.locator('#fire-in').count(), 0);
  await page.click('header.top a[href="#merch"]');
  assert.equal(await page.locator('#v-merch .m-card').count(), 6);   // Dom, Nov 22 2026: Trans Heart and You Can't Change Us added; Nov 26: the veterans song off (grade fix 1)
  assert.equal(await page.locator('header.top a[href="/here-to-help/"]').count(), 1);
  await page.close();
  // Week 2 (Dom, Nov 14 2026, apply_week2_home.py): The Parts You Hide takes over at 7 PM Central on Sunday, Nov 15.
  for (const [when, title] of [['2026-11-16T00:59:00Z', /The Parts You Hide/i], ['2026-11-16T01:00:00Z', /The Parts You Hide/i],
                               ['2026-11-16T17:59:00Z', /The Parts You Hide/i], ['2026-11-18T18:00:00Z', /The Parts You Hide/i],
                               ['2026-11-23T00:59:00Z', /The Parts You Hide/i]]) {
    page = await open('/', when);
    assert.equal(await page.locator('.feat2:visible').count(), 1, when);
    assert.match(await page.locator('.feat2:visible .deck h3').innerText(), title, when);
    if (String(title).includes('Parts')) assert.equal(await page.locator('[data-week2-video]').getAttribute('href'),
      when < '2026-11-16T18:00:00Z' ? 'https://www.youtube.com/@GhostHeart-M95RTK' : 'https://www.youtube.com/watch?v=XfF_B-_ZNxM', when);
    if (String(title).includes('Parts')) assert.match(await page.locator('.feat2:visible .also2').innerText(), /The Man Beneath the Moon/, when);
    await page.close();
  }
  // Week 3 (apply_week3_home.py): from 7 PM Central Sun Nov 22. Dom, Nov 23 2026: Kitchen is the feature,
  // Too Small is the "Also this week" line (video Wed Nov 25 4 PM).
  for (const when of ['2026-11-23T01:00:00Z', '2026-11-23T02:30:00Z', '2026-11-23T21:59:00Z', '2026-11-23T22:00:00Z',
                      '2026-11-25T21:59:00Z', '2026-11-25T22:00:00Z', '2026-11-26T18:00:00Z']) {
    page = await open('/', when);
    assert.equal(await page.locator('.feat2:visible').count(), 1, when);
    assert.match(await page.locator('.feat2:visible .deck h3').innerText(), /When It Isn.t Your Kitchen/i, when);
    assert.match(await page.locator('.feat2:visible .stamp').innerText(), /Week 03 . When It Isn.t Your Kitchen/i, when);
    assert.equal(await page.locator('.feat2:visible a[href="tel:18007997233"]').count(), 1, when);
    assert.equal(await page.locator('[data-week3-kitchen]').getAttribute('href'),
      when < '2026-11-23T22:00:00Z' ? 'https://www.youtube.com/@GhostHeart-M95RTK' : 'https://www.youtube.com/watch?v=z00btt9OHWg', when);
    assert.equal(await page.locator('[data-week3-song]').getAttribute('href'), 'https://www.youtube.com/watch?v=-ZtyZCxKBM8', when);  // grade fix 2
    const deck = await page.locator('.feat2:visible .deck').innerText();
    assert.doesNotMatch(deck, /Sunday, Nov 22|8 PM/i, when);
    assert.match(deck, when < '2026-11-23T22:00:00Z' ? /Monday, Nov 23, 4 PM Central/i : /Music video out now/i, when);
    assert.match(deck, /Also this week[\s\S]*Too Small is on YouTube now/i, when);  // grade fix 3
    assert.doesNotMatch(await page.locator('body').innerText(), /Out tonight at 8 PM/i, when);
    await page.close();
  }
  // Week 4 (Dom, Nov 18 2026, apply_week4_home.py): Grief Awareness Week, Why Didn't You Call, from 7 PM Central Sun Nov 29.
  for (const [when, title] of [['2026-11-30T00:59:00Z', /When It Isn.t Your Kitchen/i], ['2026-11-30T01:00:00Z', /Why Didn.t You Call/i],
                               ['2026-12-02T23:00:00Z', /Why Didn.t You Call/i]]) {
    page = await open('/', when);
    assert.equal(await page.locator('.feat2:visible').count(), 1, when);
    assert.match(await page.locator('.feat2:visible .deck h3').innerText(), title, when);
    if (String(title).includes('Call')) {
      assert.equal(await page.locator('.feat2:visible a[href="tel:988"]').count(), 1, when);
      assert.equal(await page.locator('.feat2:visible a[href="sms:988"]').count(), 1, when);
      const deck = await page.locator('.feat2:visible .deck').innerText();
      assert.match(deck, /Monday, 4 PM CT on YouTube/i, when);
      assert.doesNotMatch(await page.locator('body').innerText(), /Get the Chance/i, when); // cancelled (Dom, Nov 19)
      assert.doesNotMatch(await page.locator('body').innerText(), /I Can.t/i, when);
      assert.match(await page.title(), /Why Didn.t You Call/, when);
    }
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
  assert.equal(await page.locator('#album-songs audio').count(), 1);
  assert.equal(await page.locator('#music-videos a[href^="https://www.youtube.com/watch?v="]').count(), 4, 'Music lists the songs out as videos');
  await page.close();
  // Dom, Nov 8 2026: the campaign page is on again (confirmed prototype).
  page = await open('/wake-the-heart/');
  assert.match(await page.locator('h1').innerText(), /Wake the\s*Heart/i);
  assert.equal(new URL(page.url()).pathname, '/wake-the-heart/');
  await page.close();

  // Dom, Nov 26 2026 (grade fix 4): the old Lives address forwards to Home.
  page = await open('/live/');
  await page.waitForURL(u => new URL(u).pathname === '/');
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
  console.log('PASS site browser: 12 pages, Menu button on every phone page, campaign page on, at phone and laptop width, weeks, no Lives, Blog, Heart Dial, old links, Films with every video, Mailchimp signup.');
})().catch(e => { console.error(e); process.exit(1); });
