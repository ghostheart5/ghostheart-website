#!/usr/bin/env python3
"""Week 4 on the website: Grief Awareness Week, Why Didn't You Call (Dom, Nov 18, 2026, 6:13-6:21 PM Central).

Dom: "were changing the song i cant you why didnt you call. nov30 to the 6th will be grief awareness week",
"about a friend commiting suicide and not calling me. we can pick at the old one. we will use it in the next
campaign when we get that far", then "yes, then the wensday song will the world didnt get the chance"
(yes to plan v02: /mnt/project-files/week4-grief/FOR-DOM_WEEK4_GRIEF-AWARENESS_PLAN_v02_2026-11-19.md).

Runs after apply_week3_home.py in build_site.py, before Google Analytics and the meta and sitemap steps.

- Home, Featured week: the page carries Weeks 1 to 4. Week 3 (Too Small) shows until Sunday, Nov 29 at
  7 PM Central, then Week 4 (Why Didn't You Call) shows instead. It switches by itself.
- I Can't moves to the next campaign (not dropped). The weeks list (site.js) names Week 4 Why Didn't You Call.
- Music video on YouTube Monday, Nov 30, 4 PM Central. "Also this week": The World Didn't Get the Chance on
  YouTube Wednesday, Dec 2, 4 PM Central. Both buttons go to the channel until VIDEO_URL / WORLD_URL are set.
- Care rules (plan v02): nothing graphic (no method, no scene, no note), no blame, no lyrics quoted, no jokes.
  Plain words only ("losing a friend to suicide"), and the 988 line is on the section.
  The two lines about the song: Dom picked the softer wording, Nov 18 2026, 6:36 PM CT. Nothing says
  the song is Dom's own story. The sprayline is the plan's approved Monday card line.
- Support line: 988 Suicide & Crisis Lifeline (call or text 988, chat), 911, same as Find Support.
- Home title and share card are NOT changed by this script, so it can be merged any time before Sunday (the Week 3
  page keeps its own title and share card until then). At the switch, the browser tab title changes by itself.
  The share card (meta tags) moves to Week 4 in a small follow-up change on Sunday, Nov 29.

To take it down later, remove this script's line from build_site.py and rebuild.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
JS = ROOT / 'assets/wake-v3/site.js'
MARK = '<!-- WEEK 4: Why Didn\'t You Call, Grief Awareness Week (Dom, Nov 18, 2026) -->'
WEEK3_MARK = '<!-- WEEK 3: Too Small (Dom, Nov 16, 2026) -->'
SWITCH = '2026-11-29 19:00'  # Central
CHANNEL = 'https://www.youtube.com/@GhostHeart-M95RTK'
# Empty until the music video has a public link. Then set it and rebuild; at VIDEO_AT (Central) the button
# goes to the video and the line under the title says it is out.
VIDEO_URL = ''
VIDEO_AT = '2026-11-30 16:00'
# Also this week: The World Didn't Get the Chance on YouTube, Wed, Dec 2, 4 PM Central. False drops the line.
WORLD_LINE = False  # Dom, Nov 19 2026 7:01 AM CT: "Leave grief week to only have why didnt ypu call"
WORLD_URL = ''
WORLD_AT = '2026-12-02 16:00'
WHEN = 'Grief Awareness Week · Music video Monday, Nov 30, 4 PM Central'
WHEN_OUT = 'Grief Awareness Week · Music video out now'

WHY = ('Why Didn\u2019t You Call is a song from GhostHeart Studios about losing a friend to suicide, and the questions '
       'it leaves behind. It is for everyone still carrying them, and a reminder to reach out and to pick up.')

FLIP = ('' if not VIDEO_URL else
        '  if(now>="' + VIDEO_AT + '"){var v=document.querySelector("[data-week4-video]");if(v){v.href="' + VIDEO_URL
        + '";v.textContent="Watch the music video \\u2197"}var w=document.querySelector("[data-week4-when]");'
        'if(w)w.textContent="' + WHEN_OUT + '"}\n')
FLIP += ('' if not (WORLD_LINE and WORLD_URL) else
         '  if(now>="' + WORLD_AT + '"){var k=document.querySelector("[data-week4-world]");if(k){k.href="'
         + WORLD_URL + '";k.textContent="Watch it on YouTube \\u2197"}}\n')

WORLD = ('' if not WORLD_LINE else
         '\n          <p class="also2"><span class="mono">Also this week</span><b>The World Didn\u2019t Get the Chance</b> comes to '
         'YouTube on Wednesday, Dec 2, at 4 PM Central. <a href="' + CHANNEL + '" target="_blank" rel="noopener" '
         'data-week4-world>GhostHeart on YouTube \u2197</a></p>')

TITLE = 'GhostHeart | Why Didn\u2019t You Call · Wake the Heart Week 4'

WEEK4 = MARK + '''
<style>
.feat2.w04 .cover2{flex:0 0 130px;width:130px;height:130px;align-self:flex-start;object-fit:cover;border:1px solid rgba(192,197,204,.45);box-shadow:0 0 26px rgba(215,25,32,.35)}
.feat2.w04 .deck .head{align-items:flex-start}
.feat2.w04 .watch-line{color:var(--white)}
.feat2.w04 .also2{margin:4px 0 0;padding-top:12px;border-top:1px solid rgba(192,197,204,.25);color:var(--silver);font-size:.95rem;line-height:1.45}
.feat2.w04 .also2 .mono{display:block;margin-bottom:4px}
.feat2.w04 .also2 b{color:var(--white)}
.feat2.w04 .also2 a{color:var(--silverw,#fff)}
@media (max-width:520px){.feat2.w04 .cover2{flex-basis:100px;width:100px;height:100px}}
</style>
  <section class="wall2 feat2 w04 lit" data-seed="23" data-week="4" hidden><canvas class="paint" aria-hidden="true"></canvas>
    <span class="bgword r" aria-hidden="true">Call them</span>
    <div class="wrap">
      <div class="feat-head rv"><h2 class="bigtitle"><span class="steel">Featured</span> <span class="stn">week.</span></h2><span class="stamp s">Week 04 · Grief Awareness Week</span></div>
      <div class="feat-grid">
        <div class="rv"><div class="poster deck">
          <div class="head"><img class="cover2" src="/assets/wake-v3/img/heart-wakes.jpg" alt="The Heart Wakes album cover: tattooed hands tearing open a shirt to show a cracked, glowing red heart" width="1000" height="1000" loading="lazy"><div><h3>Why Didn\u2019t You Call</h3><p class="mono" style="margin-top:4px" data-week4-when>''' + WHEN + '''</p></div></div>
          <p class="why">''' + WHY + '''</p>
          <div class="row"><a class="btn" href="''' + CHANNEL + '''" target="_blank" rel="noopener" data-week4-video>GhostHeart on YouTube \u2197</a></div>''' + WORLD + '''
        </div></div>
        <div class="watch rv">
          <p class="sprayline"><span class="steel">If someone\u2019s on your mind,</span><br><span class="stn">call them.</span></p>
          <svg class="hb-line" viewBox="0 0 360 26" preserveAspectRatio="none" aria-hidden="true"><path d="M0 13 H150 L158 5 L166 13 L176 13 L184 1 L194 25 L202 13 H360"/></svg>
          <p class="watch-line">If you are struggling, you do not have to carry it alone.</p>
          <p class="note">988 Suicide &amp; Crisis Lifeline: <a href="tel:988">call 988</a>, <a href="sms:988">text 988</a>, or <a href="https://chat.988lifeline.org/" target="_blank" rel="noopener">chat</a>. In danger right now? <a href="tel:911">Call 911</a>. <a href="/GhostHeart_Resources.html">More support</a></p>
        </div>
      </div>
    </div>
  </section>
<script>
(function(){
  var at="''' + SWITCH + '''",now;
  try{var p={};new Intl.DateTimeFormat("en-US",{timeZone:"America/Chicago",hourCycle:"h23",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}).formatToParts(new Date()).forEach(function(x){p[x.type]=x.value});now=p.year+"-"+p.month+"-"+p.day+" "+p.hour+":"+p.minute}catch(e){now=new Date(Date.now()-6*36e5).toISOString().slice(0,16).replace("T"," ")}
  if(now<at)return;
  [].forEach.call(document.querySelectorAll('section.feat2[data-week]'),function(s){s.hidden=s.getAttribute("data-week")!=="4"});
  document.title="''' + TITLE + '''";
''' + FLIP + '''})();
</script>
'''

AFTER = '\n<section class="quote2 lit">'


JS_SWAPS = [
    ('{nm:"I Can\u2019t",up:"2026-11-29",a:"2026-11-30",b:"2026-12-06"}',
     '{nm:"Why Didn\u2019t You Call",up:"2026-11-29",a:"2026-11-30",b:"2026-12-06",soon:["' + VIDEO_AT
     + '","Music video Monday, Nov 30, 4 PM Central"],note:"For Grief Awareness Week. If someone\u2019s on your mind, call them.'
     + (' The World Didn\u2019t Get the Chance comes to YouTube on Wednesday, Dec 2, at 4 PM Central.' if WORLD_LINE else '')
     + ' If you are struggling, call or text 988."}'),
]


def main() -> None:
    s = HOME.read_text(encoding='utf-8')
    t = s
    if MARK not in t:
        assert t.count(WEEK3_MARK) == 1, 'week 3 section not found (apply_week3_home.py must run first)'
        i = t.index('data-week="3"')
        j = t.index(AFTER, i)
        t = t[:j] + '\n' + WEEK4 + t[j:]
    if t != s:
        HOME.write_text(t, encoding='utf-8')
    assert t.count(MARK) == 1 and t.count('data-week="4"') == 1 and 'Week 3</title>' in t
    assert t.index('data-week="3"') < t.index('data-week="4"')
    assert t.count('<h1') == 1
    week4 = t[t.index(MARK):t.index('</script>', t.index(MARK))]
    assert 'tel:988' in week4 and 'sms:988' in week4 and WHEN in week4
    assert ('Get the Chance' in week4) == WORLD_LINE
    assert 'I Can' not in week4

    s = JS.read_text(encoding='utf-8')
    u = s
    for old, new in JS_SWAPS:
        if old in u:
            assert u.count(old) == 1, old
            u = u.replace(old, new)
    if u != s:
        JS.write_text(u, encoding='utf-8')
    assert 'nm:"Why Didn\u2019t You Call"' in u and 'nm:"I Can' not in u
    print('Week 4, Why Didn\u2019t You Call (Grief Awareness Week), takes the home page at 7 PM Central on Sunday, Nov 29.')


main()
