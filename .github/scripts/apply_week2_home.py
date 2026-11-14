#!/usr/bin/env python3
"""Week 2 on the website: The Parts You Hide (Dom, Nov 14, 2026: "GET 7PM WEBSITE SET UP AND READY TO GO").

Runs after apply_protector_home.py in build_site.py, before Google Analytics and the meta and sitemap steps.

Wake the Heart Week 2 is The Parts You Hide, for Trans Awareness Week. The song comes out Monday, Nov 16.
The website update goes up Sunday, Nov 15 at 7 PM Central (rules sheet: website updates the Sunday before).

- Home, Featured week: the page carries both weeks. Week 1 (To Those Who Served) shows until Sunday,
  Nov 15 at 7 PM Central, then Week 2 (The Parts You Hide) shows instead. So this can be merged any time
  before Sunday night and it switches by itself. Without JavaScript, Week 1 stays.
- Week 2 has no play button: the song file is not on the site yet. The button goes to the GhostHeart
  YouTube channel until the video is up. PLACEHOLDER: swap VIDEO for the video link once it is public.
- Words come only from Dom-approved copy, word for word: sentences 1 and 4 of the approved YouTube description (Nov 14), the approved Week 2
  kit line "Your story. Your timing." and the kit's three friend steps. No lyrics are quoted.
  Nothing implies Dom is a veteran. Picture: Dom's chosen title card (TitleCard_DOM_square.png).
- Also this week (Dom, Nov 14: "MAN BENEATH THE MOON NEEDS TO BE ON THE WEBSITE NEXT WEEK"): one line that the
  older song comes back as a new music video on Wednesday, Nov 18 (Dom's own words and date). No description,
  since its script still waits on Dom. PLACEHOLDER: MOON_VIDEO goes to the channel until the video is public.
  (apply_week1_songs_only.py still lists it as an older song; its check runs before this step.)
- Support line: Trans Lifeline and The Trevor Project, the same numbers as Find Support.
- Home title and share card name Week 2 (the old ones named Veterans Day, which has passed).
- Weeks list (assets/wake-v3/site.js): Week 2 says "Out Monday" until Monday, and carries a short note.

To take it down later, remove this script's line from build_site.py and rebuild.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
JS = ROOT / 'assets/wake-v3/site.js'
MARK = '<!-- WEEK 2: The Parts You Hide (Dom, Nov 14, 2026) -->'
SWITCH = '2026-11-15 19:00'  # Central
# PLACEHOLDER until The Parts You Hide video is public on YouTube: then put its watch link here and rebuild.
VIDEO = 'https://www.youtube.com/@GhostHeart-M95RTK'
# PLACEHOLDER until The Man Beneath the Moon's new video is public (Wed, Nov 18): then put its watch link here.
MOON_VIDEO = 'https://www.youtube.com/@GhostHeart-M95RTK'
VIDEO_LABEL = 'GhostHeart on YouTube ↗' if '@' in VIDEO else 'Watch the full song ↗'

WEEK2 = MARK + '''
<style>
section.feat2[hidden]{display:none!important}
.feat2.w02 .cover2{flex:0 0 130px;width:130px;height:130px;align-self:flex-start;object-fit:cover;border:1px solid rgba(192,197,204,.45);box-shadow:0 0 26px rgba(215,25,32,.35)}
.feat2.w02 .deck .head{align-items:flex-start}
.feat2.w02 .also2{margin:4px 0 0;padding-top:12px;border-top:1px solid rgba(192,197,204,.25);color:var(--silver);font-size:.95rem;line-height:1.45}
.feat2.w02 .also2 .mono{display:block;margin-bottom:4px}
.feat2.w02 .also2 b{color:var(--white)}
.feat2.w02 .also2 a{color:var(--silverw,#fff)}
.feat2.w02 .steps2{margin:0;padding-left:1.3em;color:var(--white);display:grid;gap:6px;font-size:1.02rem;line-height:1.4}
@media (max-width:520px){.feat2.w02 .cover2{flex-basis:100px;width:100px;height:100px}}
</style>
  <section class="wall2 feat2 w02 lit" data-seed="23" data-week="2" hidden><canvas class="paint" aria-hidden="true"></canvas>
    <span class="bgword r" aria-hidden="true">Your timing</span>
    <div class="wrap">
      <div class="feat-head rv"><h2 class="bigtitle"><span class="steel">Featured</span> <span class="stn">week.</span></h2><span class="stamp s">Week 02 · Trans Awareness Week</span></div>
      <div class="feat-grid">
        <div class="rv"><div class="poster deck">
          <div class="head"><img class="cover2" src="/assets/protector/parts-you-hide.jpg" alt="The Parts You Hide cover: two hooded figures in the rain, the front one in a trans-flag hoodie with a cracked heart patch" width="640" height="640" loading="lazy"><div><h3>The Parts You Hide</h3><p class="mono" style="margin-top:4px">The Heart Wakes · Out Monday, Nov 16</p></div></div>
          <p class="why">The Parts You Hide is a Country and Americana song from GhostHeart Studios, released for Trans Awareness Week. His story belongs to him, and he gets to share it when he is ready.</p>
          <div class="row"><a class="btn" href="''' + VIDEO + '''" target="_blank" rel="noopener" data-week2-video>''' + VIDEO_LABEL + '''</a></div>
          <p class="also2"><span class="mono">Also this week</span><b>The Man Beneath the Moon</b> comes back as a new music video on Wednesday, Nov 18. <a href="''' + MOON_VIDEO + '''" target="_blank" rel="noopener" data-week2-moon>GhostHeart on YouTube ↗</a></p>
        </div></div>
        <div class="watch rv">
          <p class="sprayline"><span class="steel">Your story.</span><br><span class="stn">Your timing.</span></p>
          <svg class="hb-line" viewBox="0 0 360 26" preserveAspectRatio="none" aria-hidden="true"><path d="M0 13 H150 L158 5 L166 13 L176 13 L184 1 L194 25 L202 13 H360"/></svg>
          <ol class="steps2"><li>Use the name they gave you, every time.</li><li>If you slip, fix it and keep going.</li><li>Let them choose who knows.</li></ol>
          <p class="note">Need someone to talk to? Trans Lifeline: <a href="tel:18775658860">877-565-8860</a>. LGBTQ+ and under 25: The Trevor Project, <a href="tel:18664887386">1-866-488-7386</a>, or <a href="sms:678678">text START to 678-678</a>. <a href="/GhostHeart_Resources.html">More support</a></p>
        </div>
      </div>
    </div>
  </section>
<script>
(function(){
  var at="''' + SWITCH + '''",now;
  try{var p={};new Intl.DateTimeFormat("en-US",{timeZone:"America/Chicago",hourCycle:"h23",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}).formatToParts(new Date()).forEach(function(x){p[x.type]=x.value});now=p.year+"-"+p.month+"-"+p.day+" "+p.hour+":"+p.minute}catch(e){now=new Date(Date.now()-6*36e5).toISOString().slice(0,16).replace("T"," ")}
  if(now<at)return;
  var w1=document.querySelector('section.feat2[data-week="1"]'),w2=document.querySelector('section.feat2[data-week="2"]');
  if(w1)w1.hidden=true;if(w2)w2.hidden=false;
})();
</script>
'''

WEEK1_OPEN = '<section class="wall2 feat2 lit" data-seed="23">'
WEEK1_END = '\n<section class="quote2 lit">'

TITLE = 'GhostHeart | The Parts You Hide · Wake the Heart Week 2'
DESC = ('The Parts You Hide is a Country and Americana song from GhostHeart Studios, released for Trans Awareness Week. '
        'His story belongs to him, and he gets to share it when he is ready.')

JS_SWAPS = [
    ('{nm:"The Parts You Hide",up:"2026-11-15",a:"2026-11-16",b:"2026-11-22"}',
     '{nm:"The Parts You Hide",up:"2026-11-15",a:"2026-11-16",b:"2026-11-22",soon:["2026-11-16 00:00","Out Monday, Nov 16"],'
     'songs:["The Parts You Hide","The Man Beneath the Moon"],note:"For Trans Awareness Week. Your story. Your timing. The Man Beneath the Moon comes back as a new music video on Wednesday, Nov 18."}'),
    ('(up?"Out now":', '(up?(w.soon&&NOW<w.soon[0]?w.soon[1]:"Out now"):'),
]


def main() -> None:
    s = HOME.read_text(encoding='utf-8')
    t = s
    if MARK not in t:
        assert t.count(WEEK1_OPEN) == 1, 'featured week section not found'
        t = t.replace(WEEK1_OPEN, '<section class="wall2 feat2 w01 lit" data-seed="23" data-week="1">', 1)
        i = t.index('data-week="1"')
        j = t.index(WEEK1_END, i)
        t = t[:j] + '\n' + WEEK2 + t[j:]
    t = re.sub(r'<title>[^<]*</title>', f'<title>{TITLE}</title>', t, count=1)
    for attr, value in (('property="og:title"', TITLE), ('name="twitter:title"', TITLE), ('name="description"', DESC),
                        ('property="og:description"', DESC), ('name="twitter:description"', DESC)):
        t = re.sub(r'<meta ' + re.escape(attr) + r' content="[^"]*"', f'<meta {attr} content="{value}"', t, count=1)
    if t != s:
        HOME.write_text(t, encoding='utf-8')
    assert t.count(MARK) == 1 and t.count('data-week="2"') >= 1 and f'<title>{TITLE}</title>' in t
    assert t.count('<h1') == 1

    s = JS.read_text(encoding='utf-8')
    u = s
    for old, new in JS_SWAPS:
        if old in u:
            assert u.count(old) == 1, old
            u = u.replace(old, new)
    if u != s:
        JS.write_text(u, encoding='utf-8')
    assert 'soon:["2026-11-16 00:00"' in u and 'w.soon&&NOW<w.soon[0]' in u
    print('Week 2, The Parts You Hide, takes the home page at 7 PM Central on Sunday, Nov 15.')


main()
