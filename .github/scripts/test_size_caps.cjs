// Size guard (Dom, Nov 21 2026: "EVERYTIME THEY CHANGE SOMETHING THE WHOLE WEBSITE GOES BACK TO HUGE LAYOUT").
// Opens every main page in a real browser at laptop and phone size and fails if anything is over the limits:
// text size, picture height, and how many screens long Home and About are.
// The limits match /assets/shared/size-caps.css. Raise a limit only with Dom's yes, in both files.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
const ROOT = path.resolve(__dirname, '..', '..');

const PAGES = ['/', '/#story', '/#vault', '/#live', '/#merch', '/wake-the-heart/', '/music/', '/GhostHeart_Videos.html', '/live/',
  '/GhostHeart_Story.html', '/story/', '/journal/', '/vault/', '/here-to-help/', '/GhostHeart_Projects.html', '/follow/',
  '/GhostHeart_Resources.html', '/GhostHeart_Privacy.html', '/GhostHeart_Quotes.html'];
// screen size, biggest text (px), tallest picture (px), longest page in screens for Home and About
// The page-length limits sit a little above what was measured (Home 3.3 laptop, 4.0 phone on Nov 21 2026),
// because the checks machine uses different fonts and renders pages slightly longer than a Windows PC.
// hero: Home's top picture, Scars Wakes the Heart. Dom, Nov 22 2026: "can you zoom out on the scars wakes the heart?" It is shown
// whole and sized to fit the first screen (apply_new_home.py), so it has its own limit instead of the 345px picture limit.
const SIZES = [
  {name: 'laptop', width: 1366, height: 768, text: 56, moving: 64, picture: 345, hero: 570, screens: {'/': 3.5, '/#story': 3.2}},
  {name: 'phone', width: 390, height: 844, text: 34, moving: 40, picture: 330, hero: 330, screens: {'/': 4.2, '/#story': 3.4}},
];

(async () => {
  // 1. every page links the caps stylesheet, and it is the last stylesheet in the head
  const skip = new Set(['.git', '.github', 'node_modules', 'ghostheart-website']);
  const walk = dir => fs.readdirSync(dir, {withFileTypes: true}).flatMap(e => skip.has(e.name) ? [] :
    e.isDirectory() ? walk(path.join(dir, e.name)) : e.name.endsWith('.html') ? [path.join(dir, e.name)] : []);
  for (const file of walk(ROOT)) {
    const html = fs.readFileSync(file, 'utf8');
    if (!html.includes('</head>')) continue;
    const head = html.slice(0, html.indexOf('</head>'));
    const sheets = [...head.matchAll(/<link [^>]*rel="stylesheet"[^>]*>/g)].map(m => m[0]);
    assert(sheets.length && sheets.at(-1).includes('/assets/shared/size-caps.css'),
      path.relative(ROOT, file) + ': /assets/shared/size-caps.css must be the last stylesheet in the head');
  }

  // 2. nothing on screen is over the limits
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE || undefined});
  const problems = [];
  for (const size of SIZES) {
    const context = await browser.newContext({reducedMotion: 'reduce', viewport: {width: size.width, height: size.height}});
    await context.route(/^https:\/\//, route => route.fulfill({status: 200, contentType: 'text/html', body: '<title>external</title>'}));
    const page = await context.newPage();
    for (const p of PAGES) {
      const response = await page.goto(base + p.split('#')[0], {waitUntil: 'load'});
      assert(response && response.ok(), p + ' did not load');
      if (p.includes('#')) {   // a view inside Home (About, Vault, Live, Merch): open it the way a visitor's link does
        await page.goto(base + p);
        await page.reload({waitUntil: 'load'});
      }
      await page.waitForTimeout(400);
      const found = await page.evaluate(() => {
        const shown = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none'; };
        const label = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
        let text = {px: 0, what: ''}, picture = {px: 0, what: ''}, moving = {px: 0, what: ''}, hero = {px: 0, what: ''};
        for (const e of document.querySelectorAll('body *')) {
          if (!shown(e)) continue;
          if (e.closest('[aria-hidden="true"]')) {   // decorative text: sliding bands count (they are loud); faint background words do not
            if (!e.closest('.bgword,.big-no') && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) {
              const px = parseFloat(getComputedStyle(e).fontSize);
              if (px > moving.px) moving = {px, what: label(e) + ' "' + e.textContent.trim().slice(0, 30) + '"'};
            }
            continue;
          }
          if ([...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) {
            const px = parseFloat(getComputedStyle(e).fontSize);
            if (px > text.px) text = {px, what: label(e) + ' "' + e.textContent.trim().slice(0, 30) + '"'};
          }
          if (/^(IMG|VIDEO|IFRAME)$/.test(e.tagName)) {
            const px = e.getBoundingClientRect().height;
            if (e.closest('.nh-wake')) { if (px > hero.px) hero = {px, what: label(e)}; continue; }   // Home's top picture has its own limit below
            if (px > picture.px) picture = {px, what: label(e) + ' ' + (e.currentSrc || e.src || '').split('/').pop()};
          }
        }
        return {text, picture, moving, hero, screens: document.documentElement.scrollHeight / innerHeight, sideways: document.documentElement.scrollWidth > innerWidth + 1};
      });
      const where = size.name + ' ' + p + ': ';
      if (found.text.px > size.text) problems.push(where + 'text is ' + Math.round(found.text.px) + 'px, limit ' + size.text + 'px: ' + found.text.what);
      if (found.moving.px > size.moving) problems.push(where + 'sliding or decorative text is ' + Math.round(found.moving.px) + 'px, limit ' + size.moving + 'px: ' + found.moving.what);
      if (found.hero.px > size.hero) problems.push(where + 'the top picture is ' + Math.round(found.hero.px) + 'px tall, limit ' + size.hero + 'px');
      if (found.picture.px > size.picture) problems.push(where + 'picture is ' + Math.round(found.picture.px) + 'px tall, limit ' + size.picture + 'px: ' + found.picture.what);
      if (size.screens[p] && found.screens > size.screens[p]) problems.push(where + 'page is ' + found.screens.toFixed(1) + ' screens long, limit ' + size.screens[p]);
      if (found.sideways) problems.push(where + 'page scrolls sideways');
    }
    await context.close();
  }
  await browser.close();
  assert.equal(problems.length, 0, 'Size guard: the site went over its size limits.\n' + problems.join('\n'));
  console.log('Size guard passed: ' + PAGES.length + ' pages at ' + SIZES.length + ' screen sizes are inside the limits.');
})().catch(error => { console.error(error.message || error); process.exit(1); });
