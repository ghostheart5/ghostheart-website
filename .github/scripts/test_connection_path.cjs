/* Verify the simplified homepage, single email form and next-Live route; never submits. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

module.exports = async (page, base) => {
  const evidence = process.env.GHOSTHEART_TEST_EVIDENCE_DIR;
  const results = [];
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(base + '/');
    // Owner Nov 1: the campaign leads the homepage.
    assert.equal((await page.locator('#home h1').innerText()).replace(/\s+/g, ' ').toLowerCase(), 'the man behind the heart.');
    // Site audit 2026-11-01: two hero buttons; Enter My World stays in the top bar.
    assert.deepEqual(await page.locator('#home .ghx-actions a').allTextContents(),
      ['Explore the week', '▶ Play The Awakening']);
    assert.deepEqual(await page.locator('#home .ghx-actions a').evaluateAll(nodes => nodes.map(node => node.getAttribute('href'))),
      ['/journal/wake-the-heart-week.html', '/music/#listen']);
    assert.equal(await page.locator('#home-story, .hb-arrival, .hb-scroll').count(), 0);
    assert.equal(await page.locator('#mission-board [data-live-slot-label]').count(), 1);
    assert.equal(await page.locator('section#join-the-signal').count(), 0);
    assert.equal(await page.locator('.rebellion-invite h2').textContent(), 'Get the week’s updates.');
    // One sign-up at the bottom of the page, with its existing optional-email note.
    assert.match(await page.locator('#home-join').innerText(), /Free\. Unsubscribe anytime/);
    // The Vault stays available in the footer without another signup-card invitation.
    assert.equal(await page.locator('.sitefoot a[href="/vault/"]').count(), 1);
    await page.locator('#mission-board a[href="/live/"]').focus();
    await Promise.all([page.waitForURL(base + '/live/'), page.keyboard.press('Enter')]);
    assert.equal(new URL(page.url()).pathname, '/live/');
    assert.match(await page.locator('#live-status-title').textContent(), /^Next Live: (Sunday, [A-Z][a-z]+ \d{1,2}, \d{4}, 10:00 a\.m\. Central|coming soon)\.$/);
    assert.match(await page.locator('main').innerText(), /Every Sunday at 10:00 a\.m\. Central I go live on TikTok/);
    assert.equal(await page.locator('main time, #live-replay, main iframe').count(), 0);
    assert.doesNotMatch(await page.locator('main').innerText(), /October 11|The Awakening Begins|I'm a Nobody|Watch Live|Reading|My Promise/i);
    const menu = page.locator('header.ghx-header .ghx-menu-toggle');
    await menu.click();
    assert.equal(await page.getByRole('link', { name: 'Lives', exact: true }).first().isVisible(), true);
    await page.keyboard.press('Escape');
    // Owner decision 2026-11-01: readings are off the site.
    assert.equal(await page.locator('a[href*="my-promise"]').count(), 0);
    if (evidence && [390, 1440].includes(width)) {
      await page.screenshot({ path: path.join(evidence, 'live-' + width + '.png'), fullPage: true });
      await page.goto(base + '/#latest');
      await page.screenshot({ path: path.join(evidence, 'featured-' + width + '.png') });
    }
    for (const route of ['/', '/live/', '/follow/']) {
      await page.goto(base + route);
      await page.evaluate(() => document.fonts.ready);
      const reflow = await page.evaluate(() => ({
        viewport: innerWidth, scrollWidth: document.documentElement.scrollWidth,
        offenders: [...document.querySelectorAll('main *')].map(node => {
          const box = node.getBoundingClientRect();
          const style = getComputedStyle(node);
          return { tag: node.tagName, id: node.id, className: node.className,
            text: node.textContent.trim().slice(0, 90), left: box.left, right: box.right,
            font: style.font, display: style.display };
        }).filter(node => node.display !== 'none' && (node.right > innerWidth + 1 || node.left < -1))
      }));
      assert.ok(reflow.scrollWidth <= width + 1, route + ' overflow at ' + width + ': ' + JSON.stringify(reflow));
      assert.doesNotMatch(await page.locator('body').innerText(), /Join the Signal|Follow the Signal|GhostHeart Signal/);
      results.push({ route, width, overflow: false, signalBranding: false });
    }
    assert.equal(await page.locator('#email-signup-title').textContent(), 'Join the Heart Rebellion');
    assert.equal(await page.locator('button[type=submit]').textContent(), 'Keep Me Connected');
    assert.match(await page.locator('#email-signup-title + p').innerText(), /confirmed Live announcements/);
  }
  if (evidence) fs.writeFileSync(path.join(evidence, 'connection-results.json'), JSON.stringify({
    results, signupSubmitted: false, status: 'PASS',
    limits: ['No confirmed future Live date or viewing platform', 'No native browser zoom or provider/email test']
  }, null, 2));
  console.log('PASS connection pathway: three routes, pending Lives, no readings, 16 route/viewport reflow checks; zero submissions');
};
