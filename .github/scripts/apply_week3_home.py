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
- Weeks list (assets/wake-v3/site.js): Week 3 says when the Too Small music video comes out, and carries a note.

Switch (Dom, Nov 18, 2026, 22:51 UTC: "monday will be not your kitchen, wensday will be to small"):
- Monday, Nov 23, 4 PM Central on YouTube: When It Isn't Your Kitchen. Wednesday, Nov 25, 4 PM Central: Too Small.
- So the page no longer says "Out Sunday, Nov 22, 8 PM Central" or "Out tonight at 8 PM Central". It names the
  Too Small music video for Wednesday at 4 PM, and one "Also this week" line names When It Isn't Your Kitchen for
  Monday at 4 PM (same pattern as the Week 2 Moon line). No lyrics, no scenes, no description for Kitchen.
- Week 3 still opens Sunday, Nov 22 at 7 PM Central (website updates the Sunday before).
- KITCHEN_URL / KITCHEN_AT: put Kitchen's YouTube link in KITCHEN_URL and rebuild; its link flips at KITCHEN_AT.
  Set KITCHEN_LINE = False and rebuild to drop the Kitchen line.

Kitchen is the feature (Dom, Nov 23, 2026, 01:59 UTC: "you made to small the feature week ITS SUPPOSE TO BE WHEN IT
ISNT YOUR KITCHEN"):
- Featured week reads "Week 03 · When It Isn't Your Kitchen". Kitchen is the main card (title, words, button); Too Small
  moves to the "Also this week" line for Wednesday, Nov 25, 4 PM Central. Too Small's release date does not change.
- Kitchen's words come from the Instagram caption already scheduled for Monday (no lyrics on the site).
- Kitchen's button goes to the channel until KITCHEN_AT, then to KITCHEN_URL. Too Small's line link goes to the channel
  until SONG_AT, then to SONG_URL (now -ZtyZCxKBM8; the old UTvuIgq-AWI upload is private).
- The section keeps the same MARK (apply_week4_home.py looks for it). If an older Week 3 section is already on the page,
  it is replaced.

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
# Empty until there is a public link for the Too Small music video. Then set it and rebuild; at SONG_AT (Central)
# the button flips to the video and the line under the title says the video is out.
SONG_URL = 'https://www.youtube.com/watch?v=-ZtyZCxKBM8'  # Too Small v03b, scheduled public Wed, Nov 25, 4 PM Central (Nov 22; UTvuIgq-AWI and Bt00 now private)
SONG_AT = '2026-11-25 16:00'  # Too Small music video on YouTube, Wed, Nov 25, 4 PM Central (Dom, Nov 18)
# Also this week: When It Isn't Your Kitchen on YouTube, Mon, Nov 23, 4 PM Central (Dom, Nov 18).
KITCHEN_LINE = True
KITCHEN_URL = 'https://www.youtube.com/watch?v=z00btt9OHWg'  # Kitchen music video, public Mon, Nov 23, 4 PM Central (same link as the approved X post and Pinterest pin)
KITCHEN_AT = '2026-11-23 16:00'
WHEN = 'New single · Music video Monday, Nov 23, 4 PM Central'
WHEN_OUT = 'New single · Music video out now'

WHY = ('When It Isn\u2019t Your Kitchen is a new single from GhostHeart Studios. It follows a mother whose husband is '
       'admired all over town. Behind closed doors he controls the money, the car keys and the front door.')

FLIP = ('' if not KITCHEN_URL else
        '  if(now>="' + KITCHEN_AT + '"){var v=document.querySelector("[data-week3-kitchen]");if(v){v.href="' + KITCHEN_URL
        + '";v.textContent="Watch the music video \\u2197"}var w=document.querySelector("[data-week3-when]");'
        'if(w)w.textContent="' + WHEN_OUT + '"}\n')
FLIP += ('' if not (KITCHEN_LINE and SONG_URL) else
         '  if(now>="' + SONG_AT + '"){var k=document.querySelector("[data-week3-song]");if(k){k.href="'
         + SONG_URL + '";k.textContent="Watch it on YouTube \\u2197"}}\n')

KITCHEN = ('' if not KITCHEN_LINE else
           '\n          <p class="also2"><span class="mono">Also this week</span><b>Too Small</b> comes to '
           'YouTube on Wednesday, Nov 25, at 4 PM Central. <a href="' + CHANNEL + '" target="_blank" rel="noopener" '
           'data-week3-song>GhostHeart on YouTube \u2197</a></p>')

WEEK3 = MARK + '''
<style>
.feat2.w03 .cover2{flex:0 0 130px;width:130px;height:130px;align-self:flex-start;object-fit:cover;border:1px solid rgba(192,197,204,.45);box-shadow:0 0 26px rgba(215,25,32,.35)}
.feat2.w03 .deck .head{align-items:flex-start}
.feat2.w03 .watch-line{color:var(--white)}
.feat2.w03 .also2{margin:4px 0 0;padding-top:12px;border-top:1px solid rgba(192,197,204,.25);color:var(--silver);font-size:.95rem;line-height:1.45}
.feat2.w03 .also2 .mono{display:block;margin-bottom:4px}
.feat2.w03 .also2 b{color:var(--white)}
.feat2.w03 .also2 a{color:var(--silverw,#fff)}
@media (max-width:520px){.feat2.w03 .cover2{flex-basis:100px;width:100px;height:100px}}
</style>
  <section class="wall2 feat2 w03 lit" data-seed="23" data-week="3" hidden><canvas class="paint" aria-hidden="true"></canvas>
    <span class="bgword r" aria-hidden="true">Kitchen</span>
    <div class="wrap">
      <div class="feat-head rv"><h2 class="bigtitle"><span class="steel">Featured</span> <span class="stn">week.</span></h2><span class="stamp s">Week 03 · When It Isn’t Your Kitchen</span></div>
      <div class="feat-grid">
        <div class="rv"><div class="poster deck">
          <div class="head"><img class="cover2" src="/assets/wake-v3/img/kitchen-cover.jpg" alt="When It Isn’t Your Kitchen single cover: a stone house at night in the rain, two shadows behind the big front window" width="1000" height="1000" loading="lazy"><div><h3>When It Isn’t Your Kitchen</h3><p class="mono" style="margin-top:4px" data-week3-when>''' + WHEN + '''</p></div></div>
          <p class="why">''' + WHY + '''</p>
          <div class="row"><a class="btn" href="''' + CHANNEL + '''" target="_blank" rel="noopener" data-week3-kitchen>GhostHeart on YouTube ↗</a></div>''' + KITCHEN + '''
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

TITLE = 'GhostHeart | When It Isn\u2019t Your Kitchen · Wake the Heart Week 3'
DESC = WHY

WEEK3_JS = ('{nm:"When It Isn\u2019t Your Kitchen",up:"2026-11-22",a:"2026-11-23",b:"2026-11-29",soon:["' + KITCHEN_AT
            + '","Music video Monday, Nov 23, 4 PM Central"],note:"If home does not feel safe, you do not have to carry it alone.'
            + (' Too Small comes to YouTube on Wednesday, Nov 25, at 4 PM Central.' if KITCHEN_LINE else '')
            + ' Thanksgiving is Thursday, Nov 26."}')
# Any earlier Week 3 entry in the weeks list (Too Small as the feature) becomes the Kitchen entry.
WEEK3_JS_OLD = re.compile(r'\{nm:"(?:Too Small|When It Isn\u2019t Your Kitchen)",up:"2026-11-22",a:"2026-11-23",b:"2026-11-29"[^}]*\}')


def main() -> None:
    s = HOME.read_text(encoding='utf-8')
    t = s
    if MARK in t:
        # Replace an older Week 3 section (Too Small as the feature) with this one.
        a = t.index(MARK)
        b = t.index('</script>\n', a) + len('</script>\n')
        t = t[:a] + WEEK3 + t[b:]
    else:
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
    week3 = t[t.index(MARK):t.index('</script>', t.index(MARK))]
    assert 'Nov 22, 8 PM' not in week3 and WHEN in week3
    assert ('Too Small' in week3) == KITCHEN_LINE and 'Week 03 · When It Isn’t Your Kitchen' in week3

    s = JS.read_text(encoding='utf-8')
    u = s
    assert len(WEEK3_JS_OLD.findall(u)) == 1, 'week 3 entry not found in the weeks list'
    u = WEEK3_JS_OLD.sub(lambda m: WEEK3_JS, u, count=1)
    if u != s:
        JS.write_text(u, encoding='utf-8')
    assert WEEK3_JS in u and 'nm:"Too Small"' not in u
    print('Week 3, When It Isn\u2019t Your Kitchen (feature), with Too Small Wed, Nov 25, 4 PM, on the home page from 7 PM Central Sun, Nov 22.')


main()
