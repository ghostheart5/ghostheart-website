// Music player seek (site audit 2026-11-01): a keyboard-operable slider with elapsed and total time.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

// Seeking needs byte-range requests, which GitHub Pages serves but `python -m http.server` (the other
// browser tests' server) does not. So this test serves the site itself, with ranges, like the real host.
const ROOT = path.resolve(__dirname, '../..');
const TYPES = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.mp3': 'audio/mpeg', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json', '.xml': 'application/xml'};
const server = http.createServer((req, res) => {
  let file = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  const size = fs.statSync(file).size;
  const type = TYPES[path.extname(file)] || 'application/octet-stream';
  const range = /bytes=(\d*)-(\d*)/.exec(req.headers.range || '');
  if (!range) { res.writeHead(200, {'Content-Type': type, 'Content-Length': size, 'Accept-Ranges': 'bytes'}); return fs.createReadStream(file).pipe(res); }
  const start = range[1] ? Number(range[1]) : size - Number(range[2]);
  const end = range[1] && range[2] ? Math.min(Number(range[2]), size - 1) : size - 1;
  res.writeHead(206, {'Content-Type': type, 'Content-Length': end - start + 1, 'Content-Range': `bytes ${start}-${end}/${size}`, 'Accept-Ranges': 'bytes'});
  fs.createReadStream(file, {start, end}).pipe(res);
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_EXECUTABLE || undefined});
  for (const width of [390, 1440]) {
    const context = await browser.newContext({reducedMotion: 'reduce', viewport: {width, height: 900}});
    await context.route('https://**/*', route => route.abort());
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(base + '/music/');
    const seek = page.locator('#seek');
    assert.equal(await seek.getAttribute('aria-label'), 'Song position');
    assert.equal(await seek.isDisabled(), true, 'disabled before a song loads');

    await page.locator('#song-cruel button[data-title]').click();
    await page.waitForFunction(() => { const a = document.getElementById('aud'); return isFinite(a.duration) && a.duration > 10; }, null, {timeout: 15000});
    await page.evaluate(() => document.getElementById('aud').pause());
    const duration = await page.evaluate(() => document.getElementById('aud').duration);
    const clock = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
    assert.equal(await seek.isDisabled(), false);
    assert.equal(Number(await seek.getAttribute('max')), Math.floor(duration));
    assert.equal(await page.locator('#t-total').innerText(), clock(duration));
    assert.equal(await seek.evaluate(e => e.getBoundingClientRect().height >= 44), true, 'touch target');

    const time = () => page.evaluate(() => document.getElementById('aud').currentTime);
    // Reach the slider the way a keyboard user does: Tab on from the Next button.
    await page.locator('#next').focus();
    await page.keyboard.press('Tab');
    assert.equal(await seek.evaluate(e => e === document.activeElement && e.matches(':focus-visible')), true, 'Tab reaches the slider with visible focus');
    await page.keyboard.press('Home');
    await page.waitForFunction(() => document.getElementById('aud').currentTime < 1);
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowRight');
    assert.ok(Math.abs(await time() - 10) < 1, 'two arrow presses move 10 seconds');
    assert.equal(await page.locator('#t-now').innerText(), '0:10');
    assert.equal(await seek.getAttribute('aria-valuetext'), '0:10 of ' + clock(duration));
    await page.keyboard.press('ArrowLeft');
    assert.ok(Math.abs(await time() - 5) < 1, 'left arrow goes back 5 seconds');
    await page.keyboard.press('End');
    await page.waitForFunction(d => document.getElementById('aud').currentTime > d - 2, duration);

    // Pointer seeking still works.
    const box = await seek.boundingBox();
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    assert.ok(Math.abs(await time() - duration / 2) < duration * 0.1, 'click in the middle seeks near halfway');

    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'no sideways scroll at ' + width);
    assert.deepEqual(errors, []);
    await context.close();
  }
  await browser.close();
  server.close();
  console.log('PASS music seek: slider label, disabled until loaded, total time, Home/arrows/End, visible focus, valuetext, pointer seek, 44px target, two widths.');
})().catch(e => { console.error(e); process.exit(1); });
