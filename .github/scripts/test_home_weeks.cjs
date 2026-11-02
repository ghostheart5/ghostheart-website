// Owner 2026-11-01: "Before the Heart Wakes" runs until Nov 8; Wake the Heart Week is Nov 9-15; then the
// Blueprint's weekly themes. The home feature switches by itself; exactly one block shows on any day (Central).
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
const cases = [
  ['2026-11-02T15:00:00Z', 'Before the Heart Wakes', 'What starts Nov 9'],
  ['2026-11-09T05:59:00Z', 'Before the Heart Wakes', 'What starts Nov 9'],
  ['2026-11-09T06:00:00Z', 'Wake the Heart Week', 'About Wake the Heart Week'],
  ['2026-11-15T23:00:00Z', 'Wake the Heart Week', 'About Wake the Heart Week'],
  ['2026-11-16T15:00:00Z', 'The Parts You Hide', 'Hear You Can’t Change Us'],
  ['2026-12-08T15:00:00Z', 'Still Here', 'Hear Rebellion'],
  ['2027-01-02T15:00:00Z', 'Wrapping Before the Heart Wakes', 'See this Sunday’s Live'],
];
(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || undefined});
  const context = await browser.newContext({reducedMotion:'reduce', viewport:{width:390,height:844}});
  await context.route('https://**/*', route => route.abort());
  for (const [when, title, cta] of cases) {
    const page = await context.newPage();
    await page.clock.install({time: new Date(when)});
    await page.goto(base + '/');
    const shown = page.locator('#latest .hb-feature:visible');
    assert.equal(await shown.count(), 1, when);
    assert.equal((await shown.locator('h2').textContent()).replace(/\.$/, '').trim(), title, when);
    assert.equal((await shown.locator('.ctas a').textContent()).trim(), cta, when);
    await page.close();
  }
  await browser.close();
  console.log('Home weeks: ' + cases.length + ' dates checked.');
})().catch(e => { console.error(e); process.exit(1); });
