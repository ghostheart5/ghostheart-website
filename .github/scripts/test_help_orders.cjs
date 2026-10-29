// "I'm here to help" order form: closed until configured; song goes to Stripe with only the order id; office request; paid return.
const {chromium}=require('playwright');const assert=require('assert');(async()=>{const b=await chromium.launch();
const base='http://localhost:8765/here-to-help/';
// 1. Unconfigured: form closed, nothing sent.
let p=await b.newPage(); let sent=0; p.on('request',r=>{if(/supabase|stripe/.test(r.url()))sent++;});
await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),true);
assert.match(await p.locator('[data-order-status-title]').innerText(),/Orders open soon/i); assert.equal(sent,0); console.log('closed ok');
// 2. Configured with mocks.
p=await b.newPage(); const posts=[];
await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/test_abc123'}"}));
await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{posts.push(JSON.parse(r.request().postData()));r.fulfill({contentType:'application/json',body:'"cfcf361c-4707-43f9-a047-d37544741355"',headers:{'access-control-allow-origin':'*'}})});
let dest=null; await p.route('https://buy.stripe.com/**',r=>{dest=r.request().url();r.fulfill({body:'stripe'})});
await p.goto(base); assert.equal(await p.locator('[data-order-fields]').evaluate(e=>e.disabled),false);
await p.click('[data-order-submit]'); assert.match(await p.locator('[data-order-error]').innerText(),/email/i);
await p.fill('#sf-email','fan@example.com'); await p.click('[data-order-submit]'); assert.match(await p.locator('[data-order-error]').innerText(),/who the song is for/i);
await p.fill('#sf-for','My mom'); await p.fill('#sf-memories','Sunday mornings'); await p.check('input[name=length][value=short]');
await Promise.all([p.waitForURL(/buy\.stripe\.com/),p.click('[data-order-submit]')]);
assert.equal(posts[0].payload.kind,'song'); assert.equal(posts[0].payload.length,'short'); assert.ok(!dest.includes('example.com'));
assert.equal(dest,'https://buy.stripe.com/test_abc123?client_reference_id=cfcf361c-4707-43f9-a047-d37544741355'); console.log('song ok',dest);
// 3. Office request.
p=await b.newPage(); await p.route('**/assets/help/orders-config.js',r=>r.fulfill({contentType:'text/javascript',body:"window.GHOSTHEART_ORDERS={supabaseUrl:'https://pgqaqqliefpofsktjhjq.supabase.co',supabaseKey:'sb_publishable_test_key_123456',songPayLink:'https://buy.stripe.com/test_abc123'}"}));
const posts2=[]; await p.route('https://pgqaqqliefpofsktjhjq.supabase.co/**',r=>{posts2.push(JSON.parse(r.request().postData()));r.fulfill({contentType:'application/json',body:'"6b6c7422-b571-4c6c-9923-bbb35058b7b0"',headers:{'access-control-allow-origin':'*'}})});
await p.goto(base); await p.check('input[name=kind][value=office]'); assert.equal(await p.locator('#sf-for').isVisible(),false);
assert.match(await p.locator('[data-order-submit]').innerText(),/Send my request/i);
await p.selectOption('#sf-service','resume'); await p.fill('#sf-details','Update my resume'); await p.fill('#sf-email','a@b.co'); await p.click('[data-order-submit]');
await p.waitForFunction(()=>/Got it/i.test(document.querySelector('[data-order-status-title]').textContent));
assert.equal(posts2[0].payload.service,'resume'); console.log('office ok');
// 4. Paid return.
p=await b.newPage(); await p.goto(base+'?paid=1#order'); assert.match(await p.locator('[data-order-status-title]').innerText(),/Thank you/i); console.log('paid ok'); console.log('PASS help orders: closed by default, song to Stripe with order id only, office request, paid return');
await b.close();})().catch(e=>{console.error(e);process.exit(1)});
