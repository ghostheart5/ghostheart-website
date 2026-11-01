/* Regression checks for optional signup after reading; never submits an address. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const action = 'https://myghostheart.us22.list-manage.com/subscribe/post?u=a7ab330423f3b936c48b8d8ba&id=880e8056a6&f_id=00bec2e1f0';
const routes = ['/journal/', '/journal/cruel-something-needs-to-change.html',
  '/journal/this-is-ghostheart.html', '/journal/ghosthearts-oath.html',
  '/journal/youre-not-god.html', '/journal/how-we-got-here-archive.html'];

module.exports = async (page, base) => {
  const results = [];
  const evidence = process.env.GHOSTHEART_TEST_EVIDENCE_DIR;
  if (evidence) fs.mkdirSync(evidence, { recursive: true });
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of routes) {
      await page.goto(base + route);
      assert.equal(await page.locator('.journal-signup').count(), 1, route);
      const form = page.locator('.journal-signup form');
      assert.equal(await form.getAttribute('action'), action);
      assert.equal(await form.getAttribute('method'), 'post');
      assert.equal(await form.getAttribute('target'), null); // same tab (2026-10-31)
      assert.equal(await form.locator('input:not([type=hidden])').count(), 2);
      const field = form.locator('input[name=EMAIL]');
      const id = await field.getAttribute('id');
      assert.equal(await form.locator('label').getAttribute('for'), id);
      assert.equal(await field.getAttribute('type'), 'email');
      assert.equal(await form.locator('.g-honeypot input').getAttribute('name'), 'b_a7ab330423f3b936c48b8d8ba_880e8056a6');
      assert.equal(await form.locator('.g-honeypot input').getAttribute('tabindex'), '-1');
      assert.match(await form.innerText(), /tap the link in the email/);
      assert.match(await form.innerText(), /Unsubscribe anytime/);
      assert.equal(await form.locator('.g-form-status').innerText(), '');
      assert.equal(await page.locator('[data-comment-thread]').count(), route === '/journal/' ? 0 : 1, route); // comments on 2026-10-31
      assert.equal(await page.locator('footer a').filter({ hasText: /^(Stay Connected|Follow by email)$/ }).getAttribute('href'), '/follow/');
      const emailLinks = await page.locator('a').filter({ hasText: /^(Stay Connected|Follow by email)(?: ↗)?$/ }).evaluateAll(nodes => nodes.map(node => node.getAttribute('href')));
      assert.ok(emailLinks.every(href => href === '/follow/'), 'Direct email links including archive arrow label');
      assert.equal(await page.locator('.journal-signup-fallback, a.email-entry').count(), 0); // one sign-up per page (2026-11-01)
      const ids = await page.locator('[id]').evaluateAll(nodes => nodes.map(node => node.id));
      assert.equal(ids.length, new Set(ids).size, 'Duplicate IDs');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false, route + ' overflow');
      await field.focus();
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement?.tagName), 'BUTTON');
      const focus = await form.locator('button').evaluate(node => {
        const s = getComputedStyle(node);
        return { outline: s.outlineStyle, width: parseFloat(s.outlineWidth), height: node.getBoundingClientRect().height };
      });
      assert.notEqual(focus.outline, 'none');
      assert.ok(focus.width >= 2 && focus.height >= 44);
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement?.getAttribute('href')), '/GhostHeart_Privacy.html');
      if (route === '/journal/') {
        assert.equal(await page.locator('h1').textContent(), 'The GhostHeart Blog.');
        assert.equal(await page.locator('.journal-feature').evaluate(node => Boolean(node.compareDocumentPosition(document.querySelector('.journal-highlights')) & Node.DOCUMENT_POSITION_FOLLOWING)), true);
      } else {
        assert.equal(await page.locator('.journal-prose').evaluate(node => node.nextElementSibling.classList.contains('journal-signup')), true);
      }
      if (width === 390 && route.includes('cruel-')) {
        assert.equal(await field.evaluate(node => node.checkValidity()), false);
        await field.fill('not-an-email');
        assert.equal(await field.evaluate(node => node.checkValidity()), false);
        await field.fill('local-layout-check@example.invalid');
        assert.equal(await field.evaluate(node => node.checkValidity()), true);
        await field.fill('');
      }
      if (evidence && [390,1440].includes(width) && [routes[0],routes[1]].includes(route)) {
        await page.locator('.journal-signup').scrollIntoViewIfNeeded();
        await page.screenshot({ path: path.join(evidence, (route === routes[0] ? 'index' : 'cruel') + '-' + width + '.png') });
      }
      results.push({ route, width, overflow: false, providerPreserved: true, focusVisible: true });
    }
  }
  // The 320 CSS-pixel checks cover the width equivalent to 1280px at 400% zoom:
  // https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
  // CSS zoom alone does not change viewport media queries and is not browser zoom.
  if (evidence) fs.writeFileSync(path.join(evidence, 'blog-results.json'), JSON.stringify({
    results, reflow: '320 CSS pixels passed', signupSubmitted: false,
    limits: ['Equivalent reflow width; manual native browser zoom untested', 'No provider, email or subscriber-state test']
  }, null, 2));
  console.log('PASS blog subscription: 24 route/viewport checks; reading order, provider, focus, 320px reflow; zero submissions');
};
