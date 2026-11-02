// Owner 2026-11-02: the Films page "Featured Now" follows each day's Shorts Week song (Central).
// Monday's song (You Can Be GhostHeart Too) has no film, so Monday shows This Is GhostHeart.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
const cases = [
  ['2026-11-02T01:00:00Z', 'This Is GhostHeart', 'AOCRvtz92JM'],
  ['2026-11-02T15:00:00Z', 'This Is GhostHeart', 'AOCRvtz92JM'],
  ['2026-11-03T05:59:00Z', 'This Is GhostHeart', 'AOCRvtz92JM'],
  ['2026-11-03T06:00:00Z', 'I Won’t Pretend to Speak for You', 'z-FRCpG9vfw'],
  ['2026-11-04T15:00:00Z', 'Hey Preacher Man', '2SEng4dmgUc'],
  ['2026-11-05T15:00:00Z', 'Human Too', 'ARCFOZSOC_o'],
  ['2026-11-06T15:00:00Z', "It's Not the 1950s", 'RtFTIssLd0s'],
  ['2026-11-07T15:00:00Z', 'Cruel', '9sbFgjM_SDE'],
  ['2026-11-08T15:00:00Z', 'This Is GhostHeart', 'AOCRvtz92JM'],
  ['2026-12-01T15:00:00Z', 'This Is GhostHeart', 'AOCRvtz92JM'],
];
(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || undefined});
  const context = await browser.newContext({reducedMotion:'reduce', viewport:{width:390,height:844}});
  await context.route('https://**/*', route => route.abort());
  for (const [when, title, id] of cases) {
    const page = await context.newPage();
    await page.clock.install({time: new Date(when)});
    await page.goto(base + '/GhostHeart_Videos.html');
    const shown = page.locator('.fhero .feature:visible');
    assert.equal(await shown.count(), 1, when);
    assert.equal((await shown.locator('h2').textContent()).trim(), title, when);
    assert.equal(await shown.locator('.ctas a.btn.red').getAttribute('href'), 'https://www.youtube.com/watch?v=' + id, when);
    await page.close();
  }
  await browser.close();
  console.log('Films daily feature: ' + cases.length + ' dates checked.');
})().catch(e => { console.error(e); process.exit(1); });
