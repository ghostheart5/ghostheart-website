#!/usr/bin/env python3
"""Week 3 on the website: Too Small (Dom, Nov 16, 2026: "THE NEW WEBSITE CHANGE NEEDS TO GO UP").

Runs after apply_week2_home.py in build_site.py, before Google Analytics and the meta and sitemap steps.

Wake the Heart Week 3 is Too Small (The Heart Wakes, track 3). The song goes public Sunday, Nov 22 at 8 PM
Central. The website update goes up Sunday, Nov 22 at 7 PM Central (rules sheet: website updates the Sunday before).

- Home, Featured week: same pattern as Week 2. The page carries Weeks 1, 2 and 3. Week 2 shows until Sunday,
  Nov 22 at 7 PM Central, then Week 3 (Too Small) shows instead. So this can be merged any time before Sunday
  night and it switches by itself.
- No play button: the song file is not put on the site (it would be downloadable before the release).
- The music video is not made yet (Director's Workbook at step 2, Nov 15), so the button goes to the GhostHeart
  YouTube channel. When there is a link to send people to, put it in SONG_URL with its public time in SONG_AT
  and rebuild: the button switches by itself at that time and reads "Listen to the full song".
- Words: no lyrics are quoted. The two lines about the song are drafted from Dom's own screenplay notes for
  the video (a memory told by the little boy; how small he is next to how big his love for his mother is;
  no graphic violence) and WAIT FOR DOM'S YES before merge. Nothing implies the story is Dom's own life.
- Support line: National Domestic Violence Hotline and Childhelp, the same numbers as Find Support.
- Home title and share card name Week 3 from the merge.
- Weeks list (assets/wake-v3/site.js): Week 3 says "Out tonight at 8 PM Central" until then, and carries a note.

To take it down later, remove this script's line from build_site.py and rebuild.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
JS = ROOT / 'assets/wake-v3/site.js'
MARK = '<!-- WEEK 3: Too Small (Dom, Nov 16, 2026) -->'
SWITCH = '2026-11-22 19:00'  # Central
CHANNEL = 'https://www.youtube.com/@GhostHeart-M95RTK'
# Empty until there is a public link for Too Small. Then set both and rebuild; the button flips at SONG_AT (Central).
SONG_URL = ''
SONG_AT = '2026-11-22 20:00'

WHY = ('Too Small is a song from GhostHeart Studios, told through the eyes of a little boy in a house that '
       'does not feel safe. He is too small to stop what is happening, but his love for his mother is bigger than all of it.')

FLIP = ('' if not SONG_URL else
        '  if(now>="' + SONG_AT + '"){var v=document.querySelector("[data-week3-song]");if(v){v.href="' + SONG_URL
        + '";v.textContent="Listen to the full song \\u2197"}}\n')

WEEK3 = MARK + '''
<style>
.feat2.w03 .cover2{flex:0 0 130px;width:130px;height:130px;align-self:flex-start;object-fit:cover;border:1px solid rgba(192,197,204,.45);box-shadow:0 0 26px rgba(215,25,32,.35)}
.feat2.w03 .deck .head{align-items:flex-start}
.feat2.w03 .watch-line{color:var(--white)}
@media (max-width:520px){.feat2.w03 .cover2{flex-basis:100px;width:100px;height:100px}}
</style>
  <section class="wall2 feat2 w03 lit" data-seed="23" data-week="3" hidden><canvas class="paint" aria-hidden="true"></canvas>
    <span class="bgword r" aria-hidden="true">Too small</span>
    <div class="wrap">
      <div class="feat-head rv"><h2 class="bigtitle"><span class="steel">Featured</span> <span class="stn">week.</span></h2><span class="stamp s">Week 03 · Too Small</span></div>
      <div class="feat-grid">
        <div class="rv"><div class="poster deck">
          <div class="head"><img class="cover2" src="/assets/wake-v3/img/heart-wakes.jpg" alt="The Heart Wakes album cover: tattooed hands tearing open a shirt to show a cracked, glowing red heart" width="1000" height="1000" loading="lazy"><div><h3>Too Small</h3><p class="mono" style="margin-top:4px">The Heart Wakes · Out Sunday, Nov 22, 8 PM Central</p></div></div>
          <p class="why">''' + WHY + '''</p>
          <div class="row"><a class="btn" href="''' + CHANNEL + '''" target="_blank" rel="noopener" data-week3-song>GhostHeart on YouTube ↗</a></div>
        </div></div>
        <div class="watch rv">
          <p class="sprayline"><span class="steel">Nobody should</span><br><span class="stn">be scared at home.</span></p>
          <svg class="hb-line" viewBox="0 0 360 26" preserveAspectRatio="none" aria-hidden="true"><path d="M0 13 H150 L158 5 L166 13 L176 13 L184 1 L194 25 L202 13 H360"/></svg>
          <p class="watch-line">If home does not feel safe, you do not have to carry it alone.</p>
          <p class="note">National Domestic Violence Hotline: <a href="tel:18007997233">800-799-7233</a>, or <a href="sms:88788">text START to 88788</a>. A child or teen being hurt: Childhelp, <a href="tel:18004224453">1-800-422-4453</a>. In danger right now? <a href="tel:911">Call 911</a>. <a href="/GhostHeart_Resources.html">More support</a></p>
        </div>
      </div>
    </div>
  </section>
<script>
(function(){
  var at="''' + SWITCH + '''",now;
  try{var p={};new Intl.DateTimeFormat("en-US",{timeZone:"America/Chicago",hourCycle:"h23",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}).formatToParts(new Date()).forEach(function(x){p[x.type]=x.value});now=p.year+"-"+p.month+"-"+p.day+" "+p.hour+":"+p.minute}catch(e){now=new Date(Date.now()-6*36e5).toISOString().slice(0,16).replace("T"," ")}
  if(now<at)return;
  [].forEach.call(document.querySelectorAll('section.feat2[data-week]'),function(s){s.hidden=s.getAttribute("data-week")!=="3"});
''' + FLIP + '''})();
</script>
'''

WEEK2_END = '<!-- WEEK 2: The Parts You Hide (Dom, Nov 14, 2026) -->'
AFTER = '\n<section class="quote2 lit">'

TITLE = 'GhostHeart | Too Small · Wake the Heart Week 3'
DESC = WHY

JS_SWAPS = [
    ('{nm:"Too Small",up:"2026-11-22",a:"2026-11-23",b:"2026-11-29"}',
     '{nm:"Too Small",up:"2026-11-22",a:"2026-11-23",b:"2026-11-29",soon:["2026-11-22 20:00","Out tonight at 8 PM Central"],'
     'note:"If home does not feel safe, you do not have to carry it alone. Thanksgiving is Thursday, Nov 26."}'),
]


def main() -> None:
    s = HOME.read_text(encoding='utf-8')
    t = s
    if MARK not in t:
        assert t.count(WEEK2_END) == 1, 'week 2 section not found (apply_week2_home.py must run first)'
        i = t.index('data-week="2"')
        j = t.index(AFTER, i)
        t = t[:j] + '\n' + WEEK3 + t[j:]
    t = re.sub(r'<title>[^<]*</title>', f'<title>{TITLE}</title>', t, count=1)
    for attr, value in (('property="og:title"', TITLE), ('name="twitter:title"', TITLE), ('name="description"', DESC),
                        ('property="og:description"', DESC), ('name="twitter:description"', DESC)):
        t = re.sub(r'<meta ' + re.escape(attr) + r' content="[^"]*"', f'<meta {attr} content="{value}"', t, count=1)
    if t != s:
        HOME.write_text(t, encoding='utf-8')
    assert t.count(MARK) == 1 and t.count('data-week="3"') == 1 and f'<title>{TITLE}</title>' in t
    assert t.index('data-week="2"') < t.index('data-week="3"')
    assert t.count('<h1') == 1

    s = JS.read_text(encoding='utf-8')
    u = s
    for old, new in JS_SWAPS:
        if old in u:
            assert u.count(old) == 1, old
            u = u.replace(old, new)
    if u != s:
        JS.write_text(u, encoding='utf-8')
    assert 'soon:["2026-11-22 20:00"' in u
    print('Week 3, Too Small, takes the home page at 7 PM Central on Sunday, Nov 22.')


main()
