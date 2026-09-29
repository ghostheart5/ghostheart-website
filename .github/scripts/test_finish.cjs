const { chromium }=require('playwright');
const fs=require('fs');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const context=await browser.newContext({reducedMotion:'reduce'});
 const errors=[],posts=[],external=[];
 await context.addInitScript(()=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async v=>{window.__copied=v;}}});});
 await context.route('https://**/*',async route=>{
  const r=route.request();external.push(r.url());
  if(r.url().includes('list-manage.com/subscribe/post'))posts.push({url:r.url(),method:r.method(),body:r.postData()});
  return route.fulfill({status:200,contentType:'text/html',body:'<h1>Intercepted test response; no remote request sent.</h1>'});
 });
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 const order=['broken-man','ghostheart','ghosthearts-angel','fatherhood','human-after-all','love-is-love','the-ones-we-carry','uplifting','youre-not-god'];
 const paths=['/','/GhostHeart_Story.html','/GhostHeart_Angel.html','/start/index.html','/music/index.html','/live/index.html','/follow/index.html','/journal/index.html','/journal/how-we-got-here.html','/GhostHeart_Projects.html','/GhostHeart_Resources.html','/GhostHeart_Privacy.html','/GhostHeart_Quotes.html','/GhostHeart_Videos.html','/GhostHeart_Songs.html','/GhostHeart_Versions.html','/GhostHeart_Version_Mission.html','/signup/check-your-inbox.html','/signup/confirmed.html','/albums/index.html',...order.map(x=>'/albums/'+x+'/index.html')];
 const layouts=[];
 for(const width of [360,390,768,1440]){
  await page.setViewportSize({width,height:900});
  for(const path of paths){
   const response=await page.goto('http://127.0.0.1:8765'+path,{waitUntil:'domcontentloaded'});assert.equal(response.status(),200,path);
   await page.waitForTimeout(90);
   assert.equal(await page.locator('h1').count(),1,path+' one main heading');
   assert.equal(await page.locator('header.gateway-header a[href*="GhostHeart_Versions.html"]').count(),0,'Retired taxonomy not in menu');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,path+' overflow '+width);
   const menu=page.locator('.ghx-menu-toggle');await menu.click();assert.equal(await menu.getAttribute('aria-expanded'),'true',path+' open');await page.keyboard.press('Escape');assert.equal(await menu.getAttribute('aria-expanded'),'false',path+' Escape');
   layouts.push({path,width,passed:true});
  }
 }
 await page.setViewportSize({width:1440,height:1000});
 await page.goto('http://127.0.0.1:8765/albums/index.html');
 const actualOrder=await page.locator('.l-collection-card h2 a').evaluateAll(a=>a.map(n=>n.getAttribute('href').split('/')[2]));assert.deepEqual(actualOrder,order);
 await page.goto('http://127.0.0.1:8765/albums/fatherhood/index.html');assert.equal(await page.locator('#the-dad h3').innerText(),'The Dad');assert.equal(await page.locator('[data-video-id="cBNxq4y1ahU"]').count(),1);
 await page.goto('http://127.0.0.1:8765/albums/love-is-love/index.html');assert.equal(await page.locator('[data-video-id="FaT_Ibrs9Y0"]').count(),1);
 await page.goto('http://127.0.0.1:8765/albums/human-after-all/index.html');assert.equal(await page.locator('[data-video-id="ARCFOZSOC_o"]').count(),1);
 await page.goto('http://127.0.0.1:8765/GhostHeart_Videos.html');assert.equal(await page.locator('iframe').count(),0);
 await page.locator('#library-search').fill('Rebellion');assert.equal(await page.locator('[data-library-item]:visible').count(),1);
 await page.locator('[data-video-id="FaT_Ibrs9Y0"]').click();assert.match(await page.locator('.g-player iframe').getAttribute('src'),/youtube-nocookie.com\/embed\/FaT_Ibrs9Y0/);
 await page.locator('#library-search').fill('zzzz-no-such-film');assert.equal(await page.locator('iframe').count(),0,'Filtering removes a playing iframe');assert.equal(await page.locator('[data-library-empty]').isVisible(),true);
 await page.evaluate(()=>location.hash='film-this-is-ghostheart');await page.waitForTimeout(120);assert.equal(await page.locator('#film-this-is-ghostheart').isVisible(),true);assert.equal(await page.locator('#library-search').inputValue(),'');
 await page.locator('[data-video-id="AOCRvtz92JM"]').click();await page.locator('[data-video-id="mBAsUNX3vHQ"]').click();assert.equal(await page.locator('.g-player iframe').count(),1);await page.locator('.g-close:visible').click();assert.equal(await page.locator('iframe').count(),0);
 const data=JSON.parse(fs.readFileSync('.github/content/site-library.json','utf8'));
 await page.goto('http://127.0.0.1:8765/GhostHeart_Quotes.html');
 assert.deepEqual(await page.locator('.q-text').allTextContents(),data.quotes,'Exact quote preservation');assert.equal(await page.locator('[data-quote]:visible').count(),9);
 await page.locator('#show-more').click();assert.equal(await page.locator('[data-quote]:visible').count(),17);assert.equal(await page.evaluate(()=>document.activeElement.id),'quote-10','Focus moves to revealed quote');
 await page.locator('#quote-01 [data-copy-quote]').click();assert.equal(await page.evaluate(()=>window.__copied),data.quotes[0]);
 await page.locator('#quote-01 [data-copy-link]').click();assert.equal(await page.evaluate(()=>window.__copied),'http://127.0.0.1:8765/GhostHeart_Quotes.html#quote-01');
 await page.locator('#quote-search').fill('zzzz-no-match');assert.equal(await page.locator('[data-quote]:visible').count(),0);
 await page.evaluate(()=>location.hash='quote-17');await page.waitForTimeout(120);assert.equal(await page.locator('#quote-17').isVisible(),true);
 await page.goto('http://127.0.0.1:8765/GhostHeart_Songs.html');assert.equal(await page.locator('.record-card').count(),data.recordings.length);
 const originalLinks=data.recordings.flatMap(r=>[...r.html.matchAll(/href="([^"]+)"/g)].map(m=>m[1].replace(/&amp;/g,'&')));
 const currentLinks=await page.locator('.record-card a[href]').evaluateAll(a=>a.map(n=>n.getAttribute('href')));for(const href of originalLinks)assert.ok(currentLinks.includes(href),'Preserved recording link '+href);
 await page.locator('#library-search').fill('zzzzz');await page.evaluate(()=>location.hash='song-the-dad');await page.waitForTimeout(120);assert.equal(await page.locator('#song-the-dad').isVisible(),true);
 await page.goto('http://127.0.0.1:8765/journal/how-we-got-here.html');assert.equal(await page.evaluate(()=>localStorage.getItem('ghostheart.reading.place.v1')),null);
 await page.locator('[data-save-reading]').click();await page.evaluate(()=>scrollTo(0,850));await page.waitForTimeout(250);assert.ok((await page.evaluate(()=>JSON.parse(localStorage.getItem('ghostheart.reading.place.v1')))).y>500);
 await page.goto('http://127.0.0.1:8765/');assert.equal(await page.locator('.g-resume').isVisible(),true);await page.locator('[data-forget-reading]').click();assert.equal(await page.evaluate(()=>localStorage.getItem('ghostheart.reading.place.v1')),null);
 await page.goto('http://127.0.0.1:8765/follow/index.html');await page.locator('button[name=subscribe]').click();assert.equal(posts.length,0,'Empty signup not sent');
 await page.locator('input[name=EMAIL]').fill('website-test@example.invalid');const wait=context.waitForEvent('page');await page.locator('button[name=subscribe]').click();const popup=await wait;await popup.waitForLoadState();await popup.close();assert.equal(posts.length,1);assert.equal(posts[0].method,'POST');assert.match(posts[0].url,/id=880e8056a6/);assert.match(posts[0].body,/EMAIL=website-test%40example.invalid/);
 assert.match(await page.locator('.g-form-status').innerText(),/does not confirm/);
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const plain=await nojs.newPage();
 await plain.goto('http://127.0.0.1:8765/GhostHeart_Quotes.html');assert.equal(await plain.locator('[data-quote]:visible').count(),17);assert.equal(await plain.locator('.l-nojs-nav').isVisible(),true);
 await plain.goto('http://127.0.0.1:8765/GhostHeart_Videos.html');assert.ok(await plain.locator('.g-film:visible').count()>=20);
 await plain.goto('http://127.0.0.1:8765/journal/how-we-got-here.html');assert.ok((await plain.locator('.journal-prose').innerText()).length>1500);
 fs.mkdirSync('.github/evidence/site-finish',{recursive:true});
 for(const [path,name] of [['/albums/index.html','collections'],['/GhostHeart_Quotes.html','quotes'],['/GhostHeart_Videos.html','films']]){
  await page.goto('http://127.0.0.1:8765'+path);await page.setViewportSize({width:1440,height:960});await page.screenshot({path:'.github/evidence/site-finish/'+name+'-desktop.png'});await page.setViewportSize({width:390,height:844});await page.screenshot({path:'.github/evidence/site-finish/'+name+'-mobile.png'});
 }
 assert.deepEqual(errors,[]);
 const receipt={status:'passed',layoutChecks:layouts.length,layouts,exactQuotesPreserved:17,originalRecordingLinksPreserved:true,angelBeforeFatherhood:true,rebellionAndHumanTooConnected:true,fatherhoodHasTheDad:true,searchAndDeepLinks:true,quoteCopyAndFocus:true,readingBookmarkOptInAndRemoval:true,noJavaScriptContent:true,emptyEmailRejected:true,signupRequestIntercepted:true,actualSignupSent:false,emailDeliveryVerified:false,newsletterActivated:false,fullExternalVideoPlaybackTested:false,browserErrors:errors};
 fs.writeFileSync('.github/evidence/site-finish/tests.json',JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
