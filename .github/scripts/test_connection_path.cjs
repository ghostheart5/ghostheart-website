/* Verify the new invitation and visible pending Live route; never submits. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

module.exports = async (page, base) => {
  const evidence = process.env.GHOSTHEART_TEST_EVIDENCE_DIR;
  const results = [];
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(base + '/');
    // Owner decision 2026-10-14 (LOUD redesign): homepage headline is "Too Human to Stay Quiet."
    assert.equal((await page.locator('#home h1').innerText()).toLowerCase(), 'too human\nto stay quiet.');
    assert.deepEqual(await page.locator('#home .ghx-actions a').allTextContents(),
      ['▶ Play The Awakening', 'Get Your Song Written', 'Enter My World']);
    assert.deepEqual(await page.locator('#home .ghx-actions a').evaluateAll(nodes => nodes.map(node => node.getAttribute('href'))),
      ['/music/#listen', '/here-to-help/#order', '/GhostHeart_Story.html']);
    assert.equal(await page.locator('#mission-board form').count(), 0);
    assert.match(await page.locator('#mission-board').innerText(), /No payment or personal story is required/);
    assert.match(await page.locator('#mission-board').innerText(), /The Awakening campaign continues through January 3, 2027\. The Start campaign kicks off January 4, 2027\./);
    assert.equal(await page.locator('section#join-the-signal').count(), 0);
    assert.equal(await page.locator('.rebellion-invite h2').textContent(), 'Join the Heart Rebellion.');
    assert.match(await page.locator('.rebellion-invite').innerText(), /Free and optional/);
    for (const fragment of ['#home-vault']) {
      await page.locator('.rebellion-invite a[href="' + fragment + '"]').focus();
      await page.keyboard.press('Enter');
      // The same-page jump reaches Playwright's URL a moment after the key press; wait for it instead of racing it.
      await page.waitForURL(url => url.hash === fragment, { waitUntil: 'commit', timeout: 5000 }).catch(() => {});
      assert.equal(new URL(page.url()).hash, fragment);
      const box = await page.locator(fragment).boundingBox();
      const header = await page.locator('header.ghx-header').boundingBox();
      assert.ok(box.y >= header.y + header.height - 1 && box.y < 900, fragment + ' visible below header');
    }
    await page.locator('#mission-board a[href="/live/"]').focus();
    await Promise.all([page.waitForURL(base + '/live/'), page.keyboard.press('Enter')]);
    assert.equal(new URL(page.url()).pathname, '/live/');
    assert.match(await page.locator('#live-status-title').textContent(), /^Next Live: (Sunday, [A-Z][a-z]+ \d{1,2}, \d{4}, 10:00 a\.m\. Central|coming soon)\.$/);
    assert.match(await page.locator('main').innerText(), /GhostHeart Lives are on TikTok/);
    assert.equal(await page.locator('main time, #live-replay, main iframe').count(), 0);
    assert.doesNotMatch(await page.locator('main').innerText(), /October 11|The Awakening Begins|I'm a Nobody|Watch Live|weekly|every Sunday/i);
    const menu = page.locator('header.ghx-header .ghx-menu-toggle');
    await menu.click();
    assert.equal(await page.getByRole('link', { name: 'Lives & Readings', exact: true }).first().isVisible(), true);
    await page.keyboard.press('Escape');
    await page.getByRole('link', { name: 'Read My Promise', exact: true }).focus();
    assert.ok(await page.evaluate(() => parseFloat(getComputedStyle(document.activeElement).outlineWidth) >= 3));
    await Promise.all([page.waitForURL(base + '/live/my-promise.html'), page.keyboard.press('Enter')]);
    assert.equal(new URL(page.url()).pathname, '/live/my-promise.html');
    assert.equal(await page.locator('.reading-text p').count(), 15);
    await page.locator('.reading-return a').click();
    assert.equal(new URL(page.url()).pathname, '/live/');
    if (evidence && [390, 1440].includes(width)) {
      await page.screenshot({ path: path.join(evidence, 'live-' + width + '.png'), fullPage: true });
      await page.goto(base + '/#mission-board');
      await page.screenshot({ path: path.join(evidence, 'mission-' + width + '.png') });
    }
    for (const route of ['/', '/live/', '/live/my-promise.html', '/follow/']) {
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
  console.log('PASS connection pathway: three routes, pending Lives, exact reading, 16 route/viewport reflow checks; zero submissions');
};
