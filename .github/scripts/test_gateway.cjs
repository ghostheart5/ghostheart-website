const { chromium } = require('playwright');
const fs = require('fs');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({headless:true});
  const context = await browser.newContext({reducedMotion:'reduce'});
  const errors=[]; const postReceipts=[];
  await context.route('https://**/*', async route => {
    const req=route.request();
    if(req.url().includes('list-manage.com/subscribe/post')) {
      postReceipts.push({url:req.url(), method:req.method(), body:req.postData()});
      return route.fulfill({status:200,contentType:'text/html',body:'<h1>Intercepted test only</h1>'});
    }
    // No analytics, real email requests or live video playback during tests.
    return route.fulfill({status:200,contentType:'text/html',body:''});
  });
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  const paths=['/','/GhostHeart_Story.html','/GhostHeart_Angel.html','/start/index.html','/music/index.html','/live/index.html','/follow/index.html','/journal/index.html','/journal/how-we-got-here.html','/GhostHeart_Projects.html'];
  const checks=[];
  for (const width of [360,390,768,1440]) {
    await page.setViewportSize({width,height:900});
    for(const path of paths) {
      const response=await page.goto('http://127.0.0.1:8765'+path,{waitUntil:'networkidle'});
      assert.equal(response.status(),200,path);
      assert.equal(await page.locator('h1').count(),1,path+' h1');
      assert.equal(await page.locator('header a[href*="Versions"]').count(),0,'No Versions-led navigation');
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
      assert.equal(overflow,false,path+' horizontal overflow at '+width);
      const imgs=await page.locator('main img').evaluateAll(images=>images.filter(i=>!i.loading || i.loading!=='lazy').map(i=>({src:i.getAttribute('src'),valid:i.complete && i.naturalWidth>0})));
      assert.ok(imgs.every(i=>i.valid),path+' initial images '+JSON.stringify(imgs));
      const menu=page.locator('.ghx-menu-toggle');await menu.click();
      assert.equal(await menu.getAttribute('aria-expanded'),'true',path+' menu opens');
      await page.keyboard.press('Escape');
      assert.equal(await menu.getAttribute('aria-expanded'),'false',path+' Escape closes menu');
      checks.push({path,width,passed:true});
    }
  }
  await page.setViewportSize({width:1440,height:1000});
  await page.goto('http://127.0.0.1:8765/');
  assert.equal(await page.locator('iframe').count(),0,'No automatic video contact');
  await page.locator('[data-video-id="AOCRvtz92JM"]').click();
  assert.match(await page.locator('.g-player iframe').getAttribute('src'),/youtube-nocookie.com\/embed\/AOCRvtz92JM/);
  await page.locator('[data-video-id="mBAsUNX3vHQ"]').click();
  assert.equal(await page.locator('.g-player iframe').count(),1,'One player at a time');
  await page.locator('.g-close:visible').click();
  assert.equal(await page.locator('.g-player iframe').count(),0,'Player removed');
  await page.goto('http://127.0.0.1:8765/journal/how-we-got-here.html');
  assert.equal(await page.evaluate(()=>localStorage.getItem('ghostheart.reading.place.v1')),null,'Bookmark opt-in only');
  await page.locator('[data-save-reading]').click();
  assert.ok(await page.evaluate(()=>localStorage.getItem('ghostheart.reading.place.v1')));
  await page.goto('http://127.0.0.1:8765/');
  assert.equal(await page.locator('.g-resume').isVisible(),true,'Resume exists after explicit save');
  await page.locator('[data-forget-reading]').click();
  assert.equal(await page.evaluate(()=>localStorage.getItem('ghostheart.reading.place.v1')),null);
  await page.goto('http://127.0.0.1:8765/follow/index.html');
  await page.locator('button[name=subscribe]').click();
  assert.equal(postReceipts.length,0,'Empty email rejected');
  await page.locator('input[name=EMAIL]').fill('gateway-test@example.com');
  const popupPromise=context.waitForEvent('page');
  await page.locator('button[name=subscribe]').click();
  const popup=await popupPromise;await popup.waitForLoadState();
  assert.equal(postReceipts.length,1,'Exactly one intercepted signup request');
  assert.equal(postReceipts[0].method,'POST');
  assert.match(postReceipts[0].url,/id=880e8056a6/);
  assert.match(postReceipts[0].body,/EMAIL=gateway-test%40example.com/);
  assert.match(await page.locator('.g-form-status').innerText(),/does not confirm/);
  await popup.close();
  fs.mkdirSync('.github/evidence/gateway-v2',{recursive:true});
  await page.goto('http://127.0.0.1:8765/');await page.screenshot({path:'.github/evidence/gateway-v2/desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:'.github/evidence/gateway-v2/mobile.png',fullPage:true});
  assert.deepEqual(errors,[],'No browser JavaScript exceptions');
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const plain=await nojs.newPage();await plain.goto('http://127.0.0.1:8765/journal/how-we-got-here.html');
  assert.ok((await plain.locator('.journal-prose').innerText()).length>1500,'Story remains readable without JavaScript');
  const receipt={status:'passed',layoutChecks:checks,playerInsertionAndClose:true,bookmarkOptInAndRemoval:true,nativeEmailValidation:true,signupRequestIntercepted:true,actualSignupSent:false,emailDeliveryVerified:false,mailchimpAutomationActivated:false,noJavaScriptReading:true,browserErrors:errors};
  fs.writeFileSync('.github/evidence/gateway-v2/results.json',JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify(receipt));await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
