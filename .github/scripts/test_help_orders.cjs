// "I'm here to help" order form: closed until configured; song goes to Stripe with only the order id; office request; paid return.
const {chromium}=require('playwright');const assert=require('assert');(async()=>{const b=await chromium.launch();
const base=(process.env.GHOSTHEART_TEST_BASE_URL||'http://127.0.0.1:8765')+'/here-to-help/';
const statusTitle=p=>p.locator('[data-order-status-title]').innerText();
const honest=/Stripe emails your receipt/;
// 1. Unconfigured (no payment link): form closed, nothing sent. The real config is live now, so serve an empty one.
let p=await b.newPage(); let sent=0; p.on('request',r=>{if(/supabase|stripe/.test(r.url()))sent++;});
await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:''}"}));
await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),true);
assert.match(await p.locator('[data-order-status-title]').innerText(),/Orders open soon/i); assert.equal(sent,0); console.log('closed ok');
// 2. Configured with mocks.
p=await b.newPage(); const posts=[];
await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/live_abc123'}"}));
await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{posts.push(JSON.parse(r.request().postData()));r.fulfill({contentType:'application/json',body:'"cfcf361c-4707-43f9-a047-d37544741355"',headers:{'access-control-allow-origin':'*'}})});
let dest=null; await p.route('https://buy.stripe.com/**',r=>{dest=r.request().url();r.fulfill({body:'stripe'})});
await p.goto(base+'?pick=song'); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),false);
assert.equal(await p.locator('input[name=kind][value=song]').isChecked(),true);
await p.click('[data-order-submit]'); assert.match(await p.locator('[data-order-error]').innerText(),/email/i);
await p.fill('#sf-email','fan@example.com'); await p.click('[data-order-submit]'); assert.match(await p.locator('[data-order-error]').innerText(),/who the song is for/i);
await p.fill('#sf-for','My mom'); await p.fill('#sf-memories','Sunday mornings'); await p.check('input[name=length][value=short]');
await Promise.all([p.waitForURL(/buy\.stripe\.com/),p.click('[data-order-submit]')]);
assert.equal(posts[0].payload.kind,'song'); assert.equal(posts[0].payload.length,'short'); assert.ok(!dest.includes('example.com'));
assert.equal(dest,'https://buy.stripe.com/live_abc123?client_reference_id=cfcf361c-4707-43f9-a047-d37544741355'); console.log('song ok',dest);
// 2a. Back from Stripe in the same tab: the remembered order id is checked, and the database says paid.
await p.unroute('https://pgqaqqliefpofsktjhjq.supabase.co/**'); const checks=[];
await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{checks.push({url:r.request().url(),body:JSON.parse(r.request().postData())});r.fulfill({contentType:'application/json',body:'true',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base+'?paid=1#order');
await p.waitForFunction(()=>/Payment confirmed/.test(document.querySelector('[data-order-status-title]').textContent));
assert.match(await p.locator('[data-order-status-text]').innerText(),/write your song and email it within 7 days/);
assert.ok(checks[0].url.endsWith('/rest/v1/rpc/ghostheart_order_paid')); assert.deepEqual(checks[0].body,{order_id:'cfcf361c-4707-43f9-a047-d37544741355'});
assert.equal(await p.evaluate(()=>sessionStorage.getItem('ghostheart.order.pending.v1')),null,'forgotten once confirmed'); console.log('paid confirmed ok');
// 2b. Free try (the default): title + 2 lines, saved as a song story marked FREE TRY, never goes to Stripe.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/live_abc123'}"}));
const postsT=[]; let stripeHit=false; await p.route('https://buy.stripe.com/**',r=>{stripeHit=true;r.fulfill({body:'stripe'})});
await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{postsT.push(JSON.parse(r.request().postData()));r.fulfill({contentType:'application/json',body:'"0d6c7422-b571-4c6c-9923-bbb35058b7b1"',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base); assert.equal(await p.locator('input[name=kind][value=try]').isChecked(),true);
assert.match(await p.locator('[data-order-submit]').innerText(),/free preview/i); assert.equal(await p.locator('#sf-length-label').isVisible(),false);
await p.fill('#sf-for','My dad'); await p.fill('#sf-memories','Fishing at dawn'); await p.fill('#sf-email','fan@example.com'); await p.click('[data-order-submit]');
await p.waitForFunction(()=>/title and first 2 lines/i.test(document.querySelector('[data-order-status-text]').textContent));
assert.equal(postsT[0].payload.kind,'song'); assert.match(postsT[0].payload.details,/FREE TRY/); assert.equal(stripeHit,false); console.log('free try ok');
// 3. Office request.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/live_abc123'}"}));
const posts2=[]; await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{posts2.push(JSON.parse(r.request().postData()));r.fulfill({contentType:'application/json',body:'"6b6c7422-b571-4c6c-9923-bbb35058b7b0"',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base); await p.check('input[name=kind][value=office]'); assert.equal(await p.locator('#sf-for').isVisible(),false);
assert.match(await p.locator('[data-order-submit]').innerText(),/Send my request/i);
await p.selectOption('#sf-service','resume'); await p.fill('#sf-details','Update my resume'); await p.fill('#sf-email','a@b.co'); await p.click('[data-order-submit]');
await p.waitForFunction(()=>/Got it/i.test(document.querySelector('[data-order-status-title]').textContent));
assert.equal(posts2[0].payload.service,'resume'); console.log('office ok');
// 3b. A Stripe TEST link never opens the live form.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/test_9B6cN551A2Ml24haFA6Ri00'}"}));
await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),true); console.log('test link refused ok');
// 4. Paid return with no remembered order (anyone can type ?paid=1): honest receipt note, nothing asked.
p=await b.newPage(); let asked=0; await p.route('https://**',r=>{if(/supabase/.test(r.request().url()))asked++;r.fulfill({contentType:'application/json',body:'true',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base+'?paid=1#order'); assert.match(await statusTitle(p),/Thank you/i);
assert.match(await p.locator('[data-order-status-text]').innerText(),honest); await p.waitForTimeout(1500);
assert.equal(asked,0); assert.doesNotMatch(await statusTitle(p),/confirmed/i); console.log('paid, no order id: honest note ok');
// 4b. Remembered order, but the database never says paid: "Checking" then the honest note, never "confirmed".
p=await b.newPage(); let falseChecks=0;
await p.addInitScript(()=>{sessionStorage.setItem('ghostheart.order.pending.v1','0d6c7422-b571-4c6c-9923-bbb35058b7b1');window.__seen=[];
  document.addEventListener('DOMContentLoaded',()=>{const t=document.querySelector('[data-order-status-title]');new MutationObserver(()=>window.__seen.push(t.textContent)).observe(t,{childList:true,characterData:true,subtree:true});});});
await p.route('https://**',r=>{if(/rpc\/ghostheart_order_paid$/.test(r.request().url()))falseChecks++;r.fulfill({contentType:'application/json',body:'false',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base+'?paid=1#order'); assert.match(await statusTitle(p),/Checking your payment/i);
await p.waitForFunction(()=>/Thank you for your order/.test(document.querySelector('[data-order-status-title]').textContent),null,{timeout:30000});
assert.match(await p.locator('[data-order-status-text]').innerText(),honest); assert.ok(falseChecks>=5,'asked several times: '+falseChecks);
assert.ok(!(await p.evaluate(()=>window.__seen)).some(s=>/confirmed/i.test(s)),'never showed confirmed'); console.log('paid, not confirmed: honest note ok after',falseChecks,'checks');
// 4c. Ready form shows no status/warning box until there is news.
p=await b.newPage(); await p.goto(base); assert.equal(await p.locator('[data-order-status]').isVisible(),false,'no warning box on a ready form'); console.log('no warning box ok');
// 5. The real config shipped with the site opens the form with a live link.
p=await b.newPage(); await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),false); console.log('live config opens ok'); console.log('PASS help orders: closed by default, free try with no payment, song to Stripe with order id only, office request, paid confirmed only when the database says so');
await b.close();})().catch(e=>{console.error(e);process.exit(1)});
