const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('assets/journal/daily-quote.js','utf8');
// Fixed preservation fixture from journal/index.html at ca5dbd9ab956bd2869d6523ed66eea6fe4138495.
// Deliberately independent of Git HEAD and the generated quote implementation.
const quotes = [
  "Equality isn’t given; it’s reborn in the hearts of those who refuse to let it die.",
  "You can’t fight what you don’t face.",
  "When the promise breaks, the heart must carry it.",
  "They call it rebellion when you love who you want.",
  "You can’t close a revolving door, but you can get out.",
  "You can burn every bridge behind you, but ashes don’t rebuild paths.",
  "When the fire dies, silence becomes the loudest scream.",
  "I gave my life so yours could live—the heart that glows is the one that gave.",
  "Some bonds burn brighter... until they consume you.",
  "Everyone has something to say, but gets real quiet when it’s their turn.",
  "It doesn’t matter what they say; they couldn’t handle it anyway.",
  "I can’t draw or sing, but these are my words, and I say what I mean.",
  "Strength is quiet until it roars.",
  "Even broken steel remembers first.",
  "Love doesn’t ask permission to exist.",
  "Truth dances in silence.",
  "Reflection is rebellion."
];
assert.equal(quotes.length,17);
assert.deepEqual(JSON.parse(source.match(/const quotes = (\[.*?\]);/s)[1]), quotes);
const cases = [
 ['2026-10-19T04:59:59Z','2026-10-18'],['2026-10-19T05:00:00Z','2026-10-19'],
 ['2026-01-01T05:59:59Z','2025-12-31'],['2026-01-01T06:00:00Z','2026-01-01'],
 ['2026-03-08T07:59:59Z','2026-03-08'],['2026-03-08T08:00:00Z','2026-03-08'],
 ['2026-11-01T06:59:59Z','2026-11-01'],['2026-11-01T07:00:00Z','2026-11-01']
];
for(const tz of ['UTC','America/Los_Angeles','Asia/Tokyo','America/Chicago']) {
 process.env.TZ=tz;
 for(const [instant,date] of cases) {
  const nodes={qotd:{},qn:{},qlink:{}};
  class Clock extends Date { constructor(...args){super(...(args.length?args:[instant]));} }
  vm.runInNewContext(source,{Date:Clock,Intl,document:{querySelector:()=>nodes.qotd,getElementById:id=>nodes[id]}});
  const i=Math.floor(Date.parse(date+'T00:00:00Z')/86400000)%17;
  assert.equal(nodes.qotd.textContent,quotes[i],`${tz}: ${instant}`);
  assert.equal(nodes.qn.textContent,String(i+1).padStart(2,'0'));
  assert.equal(nodes.qlink.href,'/GhostHeart_Quotes.html#quote-'+String(i+1).padStart(2,'0'));
 }
}
const home=fs.readFileSync('index.html','utf8');
assert(!home.includes('FEATURED NOW')); // Owner 2026-11-01: no section label strips on the home page
assert(home.includes('Before the Heart Wakes'));
assert(home.includes('href="/journal/wake-the-heart-week.html"'));
for(const file of ['GhostHeart_Videos.html']) {
 const html=fs.readFileSync(file,'utf8');
 assert(html.includes('FEATURED NOW'));
 assert(html.includes("It's Not the 1950s"));
 assert(html.includes('Grandma remembers the rights people fought for—and the pain behind the victory speeches. Listen to who paid the price.'));
 assert(html.includes('https://www.youtube.com/watch?v=RtFTIssLd0s'));
 assert(html.includes('Watch the full film'));
 assert(!/watch the preview/i.test(html));
}
// Start Here retired 2026-11-01 (Dom): it only repeated Home and Enter My World. The 1950s film stays on Films.
assert(fs.readFileSync('start/index.html','utf8').includes('content="0; url=/"'));
assert(fs.readFileSync('GhostHeart_Videos.html','utf8').includes('RtFTIssLd0s'));
const films=fs.readFileSync('GhostHeart_Videos.html','utf8');
assert(films.includes('id="film-cruel"'));
assert(films.includes('data-video-id="9sbFgjM_SDE"'));
for(const file of ['journal/index.html','.github/loud-pages/journal/index.html.loud']) {
 const html=fs.readFileSync(file,'utf8');
 assert(html.includes('data-daily-quote'));
 assert(html.includes('src="/assets/journal/daily-quote.js"'));
 assert(!html.includes('getFullYear()'));
}
console.log('PASS: 32 timezone/boundary cases, unchanged 17 quotes, quote links, featured copy and preserved Cruel catalogue.');
