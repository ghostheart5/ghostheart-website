// Work with GhostHeart forms (Wake the Heart site, Dom Nov 6 2026): "Tell me what you need" (office request) and
// "A song from your story" (free preview). Closed until configured; paid return from Stripe stays honest.
const {chromium}=require('playwright');const assert=require('assert');(async()=>{const b=await chromium.launch();
const base=(process.env.GHOSTHEART_TEST_BASE_URL||'http://127.0.0.1:8765')+'/here-to-help/';
const statusTitle=p=>p.locator('[data-order-status-title]').innerText();
const honest=/Stripe emails your receipt/;
// 1. Unconfigured (no payment link): form closed, nothing sent. The real config is live now, so serve an empty one.
let p=await b.newPage(); let sent=0; p.on('request',r=>{if(/supabase|stripe/.test(r.url()))sent++;});
await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:''}"}));
await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),true);
assert.match(await p.locator('[data-order-status-title]').innerText(),/Orders open soon/i); assert.equal(sent,0); console.log('closed ok');
const CFG="window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/live_abc123'}";
// 2a. Back from Stripe in the same tab: the remembered order id is checked, and the database says paid.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:CFG})); const checks=[];
await p.addInitScript(()=>sessionStorage.setItem('ghostheart.order.pending.v1','cfcf361c-4707-43f9-a047-d37544741355'));
await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{checks.push({url:r.request().url(),body:JSON.parse(r.request().postData())});r.fulfill({contentType:'application/json',body:'true',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base+'?paid=1');
await p.waitForFunction(()=>/Payment confirmed/.test(document.querySelector('[data-order-status-title]').textContent));
assert.equal(await p.locator('[data-order-status]').isVisible(),true,'status shows outside the folded song section');
assert.match(await p.locator('[data-order-status-text]').innerText(),/write your song and email it within 7 days/);
assert.ok(checks[0].url.endsWith('/rest/v1/rpc/ghostheart_order_paid')); assert.deepEqual(checks[0].body,{order_id:'cfcf361c-4707-43f9-a047-d37544741355'});
assert.equal(await p.evaluate(()=>sessionStorage.getItem('ghostheart.order.pending.v1')),null,'forgotten once confirmed'); console.log('paid confirmed ok');
// 2b. Free preview: saved as a song story marked FREE TRY, never goes to Stripe.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:CFG}));
const postsT=[]; let stripeHit=false; await p.route('https://buy.stripe.com/**',r=>{stripeHit=true;r.fulfill({body:'stripe'})});
await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{postsT.push(JSON.parse(r.request().postData()));r.fulfill({contentType:'application/json',body:'"0d6c7422-b571-4c6c-9923-bbb35058b7b1"',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base); assert.equal(await p.locator('#story-form input[name=kind][value=try]').isChecked(),true);
assert.equal(await p.locator('#story-form input[name=kind]').count(),1,'free preview only');
await p.click('.song-opt summary');
assert.match(await p.locator('[data-order-submit]').innerText(),/free preview/i);
await p.click('[data-order-submit]'); assert.match(await p.locator('[data-order-error]').innerText(),/email/i);
await p.fill('#o-email','fan@example.com'); await p.click('[data-order-submit]'); assert.match(await p.locator('[data-order-error]').innerText(),/who the song is for/i);
await p.fill('#o-who','My dad'); await p.fill('#o-occ','Birthday'); await p.fill('#o-story','Fishing at dawn'); await p.click('[data-order-submit]');
await p.waitForFunction(()=>/title and first 2 lines/i.test(document.querySelector('[data-order-status-text]').textContent));
assert.equal(postsT[0].payload.kind,'song'); assert.match(postsT[0].payload.details,/FREE TRY/); assert.equal(postsT[0].payload.for_whom,'My dad');
assert.equal(postsT[0].payload.occasion,'Birthday'); assert.equal(postsT[0].payload.memories,'Fishing at dawn'); assert.equal(stripeHit,false); console.log('free preview ok');
// 3. "Tell me what you need": office request with the visitor's choice, name and date in the request text.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:CFG}));
const posts2=[]; await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{posts2.push(JSON.parse(r.request().postData()));r.fulfill({contentType:'application/json',body:'"6b6c7422-b571-4c6c-9923-bbb35058b7b0"',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base); assert.equal(await p.locator('#help-form [data-help-fields]').evaluate(e=>e.disabled),false);
await p.click('[data-help-submit]'); assert.match(await p.locator('[data-help-error]').innerText(),/choose a job/i);
await p.selectOption('#h-kind',{label:'Something else'}); await p.fill('#h-about','Help me write a eulogy'); await p.fill('#h-email','a@b.co');
await p.fill('#h-name','Sam'); await p.fill('#h-when','Friday'); await p.click('[data-help-submit]');
await p.waitForFunction(()=>/Got it/i.test(document.querySelector('[data-help-status-title]').textContent));
assert.equal(posts2[0].payload.kind,'office'); assert.equal(posts2[0].payload.email,'a@b.co');
assert.equal(posts2[0].payload.details,'Help with: Something else\nName: Sam\nNeeded by: Friday\n\nHelp me write a eulogy');
assert.ok(['data_entry','word','resume','powerpoint','excel','writing','proofreading'].includes(posts2[0].payload.service)); console.log('office ok');
// 3b. A Stripe TEST link never opens the live form.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/test_9B6cN551A2Ml24haFA6Ri00'}"}));
await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),true); console.log('test link refused ok');
// 4. Paid return with no remembered order (anyone can type ?paid=1): honest receipt note, nothing asked.
p=await b.newPage(); let asked=0; await p.route(/^https:\/\//,r=>{if(/supabase/.test(r.request().url()))asked++;r.fulfill({contentType:'application/json',body:'true',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base+'?paid=1'); assert.match(await statusTitle(p),/Thank you/i);
assert.match(await p.locator('[data-order-status-text]').innerText(),honest); await p.waitForTimeout(1500);
assert.equal(asked,0); assert.doesNotMatch(await statusTitle(p),/confirmed/i); console.log('paid, no order id: honest note ok');
// 4b. Remembered order, but the database never says paid: "Checking" then the honest note, never "confirmed".
p=await b.newPage(); let falseChecks=0;
await p.addInitScript(()=>{sessionStorage.setItem('ghostheart.order.pending.v1','0d6c7422-b571-4c6c-9923-bbb35058b7b1');window.__seen=[];
  document.addEventListener('DOMContentLoaded',()=>{const t=document.querySelector('[data-order-status-title]');new MutationObserver(()=>window.__seen.push(t.textContent)).observe(t,{childList:true,characterData:true,subtree:true});});});
await p.route(/^https:\/\//,r=>{if(/rpc\/ghostheart_order_paid$/.test(r.request().url()))falseChecks++;r.fulfill({contentType:'application/json',body:'false',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base+'?paid=1'); assert.match(await statusTitle(p),/Checking your payment/i);
await p.waitForFunction(()=>/Thank you for your order/.test(document.querySelector('[data-order-status-title]').textContent),null,{timeout:30000});
assert.match(await p.locator('[data-order-status-text]').innerText(),honest); assert.ok(falseChecks>=5,'asked several times: '+falseChecks);
assert.ok(!(await p.evaluate(()=>window.__seen)).some(s=>/confirmed/i.test(s)),'never showed confirmed'); console.log('paid, not confirmed: honest note ok after',falseChecks,'checks');
// 4c. Ready form shows no status/warning box until there is news.
p=await b.newPage(); await p.goto(base); assert.equal(await p.locator('[data-order-status]').isVisible(),false,'no warning box on a ready form'); console.log('no warning box ok');
// 5. The real config shipped with the site opens the form with a live link.
p=await b.newPage(); await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),false); console.log('live config opens ok'); console.log('PASS help orders: closed by default, free preview with no payment, office request with name and date, paid confirmed only when the database says so');
await b.close();})().catch(e=>{console.error(e);process.exit(1)});
