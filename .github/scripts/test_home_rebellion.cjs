const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.GHOSTHEART_TEST_BASE_URL || 'http://127.0.0.1:8765';
(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || undefined});
  const context = await browser.newContext({reducedMotion:'reduce'});
  await context.route('https://**/*', route => route.fulfill({status:200,body:''}));
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.clock.install({time:new Date('2026-10-20T12:00:00Z')});
  await page.addInitScript(() => {
    window.copied = null;
    Object.defineProperty(navigator, 'clipboard', {configurable:true,value:{writeText:async text => {window.copied=text;}}});
    Object.defineProperty(navigator, 'share', {configurable:true,value:undefined});
  });
  for (const width of [320,390,1440]) {
    await page.setViewportSize({width,height:900});
    await page.goto(base);
    const quote = await page.locator('#home-vault [data-daily-quote]').innerText();
    const permalink = 'https://www.myghostheart.com' + await page.locator('#qlink').getAttribute('href');
    await page.locator('[data-home-copy]').click();
    assert.equal(await page.evaluate(() => window.copied), quote+'\n'+permalink);
    await page.locator('[data-home-share]').click();
    assert.match(await page.locator('#home-share-status').innerText(), /Paste them/);
    await page.locator('#qlink').click();
    assert.equal(await page.locator(new URL(permalink).hash+' span').textContent(), quote);
    await page.goto(base);
    await page.locator('.rebellion-primary').focus();
    await Promise.all([page.waitForURL('**/follow/#email-signup-title'),page.keyboard.press('Enter')]);
    assert.equal(new URL(page.url()).pathname, '/follow/');
    assert.equal(new URL(page.url()).hash, '#email-signup-title');
    await page.goto(base);
    await page.locator('.rebellion-invite a[href="#home-vault"]').click();
    assert.equal(new URL(page.url()).hash, '#home-vault');
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1));
    await page.keyboard.press('Tab');
    for (const control of await page.locator('.rebellion-actions a,.rebellion-actions button').all()) {
      assert((await control.boundingBox()).height>=44);
      await control.focus();
      assert(await control.evaluate(e=>e.matches(':focus-visible')));
    }
    if (process.env.GHOSTHEART_SCREENSHOTS) {
      fs.mkdirSync(process.env.GHOSTHEART_SCREENSHOTS,{recursive:true});
      for (const [name,selector] of [['invitation','.rebellion-invite'],['discovery','#home-vault']]) {
        await page.locator(selector).evaluate(e => window.scrollTo({top:e.getBoundingClientRect().top+scrollY-180,behavior:'instant'}));
        await page.screenshot({path:`${process.env.GHOSTHEART_SCREENSHOTS}/${name}-${width}.png`});
      }
    }
  }
  await page.evaluate(() => Object.defineProperty(navigator,'clipboard',{value:{writeText:async()=>{throw Error('denied');}}}));
  await page.locator('[data-home-copy]').click();
  assert(await page.locator('#home-share-fallback').isVisible());
  assert(await page.locator('#home-share-text').evaluate(e=>e===document.activeElement && e.selectionEnd===e.value.length));
  await page.evaluate(() => Object.defineProperty(navigator,'share',{configurable:true,value:async data=>{window.shared=data;}}));
  await page.locator('[data-home-share]').click();
  assert.equal(await page.evaluate(()=>window.shared.url), 'https://www.myghostheart.com'+await page.locator('#qlink').getAttribute('href'));
  await page.evaluate(() => Object.defineProperty(navigator,'share',{value:async()=>{throw new DOMException('Cancelled','AbortError');}}));
  await page.locator('[data-home-share]').click();
  assert.equal(await page.locator('#home-share-status').innerText(),'Sharing cancelled.');
  assert.deepEqual(errors,[]);
  const noJS=await browser.newPage({javaScriptEnabled:false});
  await noJS.goto(base);
  assert.equal(await noJS.locator('#qlink').getAttribute('href'),'/GhostHeart_Quotes.html#quote-01');
  assert.equal(await noJS.locator('[data-home-copy]').isVisible(),false);
  assert(await noJS.locator('.rebellion-primary').isVisible());
  await browser.close();
  console.log('PASS homepage: three widths; exact quote permalink, copy, share fallback, manual fallback, native share, cancellation, keyboard, signup, Vault, no-JS; zero submissions.');
})().catch(e=>{console.error(e);process.exit(1);});
