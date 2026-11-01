const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
module.exports = async (page, base) => {
  const records = [];
  for (const width of [320, 390, 1440]) {
    await page.setViewportSize({width, height:900});
    for (const route of ['/GhostHeart_Story.html', '/passages/', '/passages/im-not.html']) {
      await page.goto(base + route);
      const link = page.getByRole('link', {name:'Get email updates', exact:true}).first();
      assert.equal(await link.getAttribute('href'), '/follow/#email-signup-title');
      const position = await link.evaluate(e=>e.getBoundingClientRect().top + scrollY);
      assert.ok(position < 1200, route + ' entry link buried: ' + position);
      await link.focus();
      assert.equal(await link.evaluate(e=>document.activeElement===e), true);
      await page.keyboard.press('Enter');
      await page.waitForURL('**/follow/#email-signup-title');
      await page.locator('#email-signup-title').waitFor();
      const heading = await page.locator('#email-signup-title').boundingBox();
      assert.ok(heading.y >= 0 && heading.y < 900, 'signup fragment visible');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      records.push({route,width,entryTop:position});
    }
    // Home page has the email box itself (2026-10-31), right under the hero buttons.
    await page.goto(base + '/');
    const homeForm = page.locator('form#home-join');
    assert.equal(await homeForm.getAttribute('method'), 'post');
    assert.equal(await homeForm.getAttribute('target'), null);
    assert.match(await homeForm.getAttribute('action'), /^https:\/\/myghostheart\.us22\.list-manage\.com\/subscribe\/post\?/);
    const homeTop = await page.locator('#home-join-email').evaluate(e=>e.getBoundingClientRect().top+scrollY);
    // Dom 2026-11-01: not at the top of home; it lives in the Join the Heart Rebellion card.
    assert.equal(await page.locator('.rebellion-invite form#home-join').count(), 1);
    assert.equal(await page.locator('#home form').count(), 0);
    assert.ok((await page.locator('#home-join button[type=submit]').boundingBox()).height >= 44);
    await page.goto(base + '/follow/');
    const field=page.locator('input[name=EMAIL]');
    const form=page.locator('form.signal-signup-form');
    assert.equal(await form.count(),1);
    assert.equal(await form.getAttribute('target'),null); // same tab (2026-10-31)
    assert.equal(await form.getAttribute('method'),'post');
    assert.match(await form.getAttribute('action'),/^https:\/\/myghostheart\.us22\.list-manage\.com\/subscribe\/post\?/);
    assert.equal(await field.getAttribute('required'),'');
    assert.equal(await field.getAttribute('type'),'email');
    assert.ok(await field.evaluate(e=>e.getBoundingClientRect().top+scrollY)<900,'email field in opening viewport');
    assert.ok(await page.locator('button[type=submit]').evaluate(e=>e.getBoundingClientRect().top+scrollY)<1000,'submit near entry');
    assert.equal(await page.evaluate(()=>document.querySelector('form').compareDocumentPosition(document.querySelector('.socials')) & Node.DOCUMENT_POSITION_FOLLOWING),4);
    await field.focus();await page.keyboard.press('Tab');
    assert.equal(await page.locator('button[type=submit]').evaluate(e=>e===document.activeElement),true);
    assert.equal(await page.locator('button[type=submit]').evaluate(e=>{const r=e.getBoundingClientRect();const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return hit===e||e.contains(hit)}),true);
    const dir=process.env.GHOSTHEART_TEST_EVIDENCE_DIR;
    if(dir){fs.mkdirSync(dir,{recursive:true});await page.screenshot({path:path.join(dir,`visible-email-follow-${width}.png`)});}
    await page.goto(base + '/GhostHeart_Story.html');
    assert.equal(await page.locator('link[href="/assets/story/story-bottom-compact.css"]').count(),1);
    const sizes=await page.locator('.her h2,.pace h2').evaluateAll(es=>es.map(e=>parseFloat(getComputedStyle(e).fontSize)));
    assert.ok(sizes.every(v=>v<=44));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  }
  console.log('PASS visible email: '+records.length+' entry routes/widths, direct signup fragments, keyboard, unblocked controls, preserved provider, compact typography; zero submissions');
};
