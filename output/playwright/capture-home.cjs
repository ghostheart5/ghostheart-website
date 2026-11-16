const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
(async()=>{
 const browser = await chromium.launch({headless:true});
 const context = await browser.newContext({reducedMotion:'reduce'});
 await context.route('https://**/*',r=>r.abort());
 const page = await context.newPage(); const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
 const records=[];
 for(const width of [320,390,768,1440]){
  await page.setViewportSize({width,height:900});
  await page.goto('http://127.0.0.1:18774/');
  assert.equal(await page.locator('.hb-arrival,.hb-scroll,#home-story').count(),0);
  assert.equal(await page.locator('main form').count(),1);
  assert.equal(await page.locator('#latest .tracks').count(),0);
  assert.equal(await page.locator('#mission-board .ghx-kicker').textContent(),'Be Part of the Mission');
  assert.equal(await page.locator('.hb-poster span').count(),0);
  assert.equal(await page.locator('#check-back-in').isHidden(),true);
  assert.equal(await page.locator('#rebellion-title').textContent(),'Get the week’s updates.');
  await page.evaluate(async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,20));}scrollTo(0,0)});
  const record=await page.evaluate(()=>({width:innerWidth,pageHeight:document.documentElement.scrollHeight,scrollWidth:document.documentElement.scrollWidth,headings:[...document.querySelectorAll('main h1,main h2')].filter(n=>n.getBoundingClientRect().height).map(n=>n.textContent.replace(/\s+/g,' ').trim())}));
  assert.ok(record.scrollWidth<=width+1,'overflow at '+width); records.push(record);
  if(width===390)await page.screenshot({path:path.join(__dirname,'homepage-390.png'),fullPage:true});
  if(width===1440){await page.screenshot({path:path.join(__dirname,'homepage-1440.png')});await page.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));await page.screenshot({path:path.join(__dirname,'homepage-1440-bottom.png')});await page.evaluate(()=>scrollTo(0,0));}
 }
 await page.evaluate(()=>localStorage.setItem('gh-visits','25'));
 await page.reload(); assert.equal(await page.locator('[data-arrival]').count(),0,'return counter does not create a generic greeting');
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(__dirname,'homepage-layout-checks.json'),JSON.stringify({records,errors,externalRequests:'blocked',submissions:0},null,2));
 console.log(JSON.stringify({records,errors,submissions:0}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});


