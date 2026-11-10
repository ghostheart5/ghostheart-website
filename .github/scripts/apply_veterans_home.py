#!/usr/bin/env python3
"""Veterans home page (Dom, Nov 9, 2026: "I ALSO WANT MY HOME PAGE OF MY WEBSITE FOR VETERANS").

Runs after apply_week1_premiere.py in build_site.py.

- Puts a "To Those Who Served" Veterans Day section at the very top of the home page,
  above The Heart Wakes. Everything else on the home page stays as it is.
- Home page title, description and share card name To Those Who Served / Veterans Day.
- The full song lives on YouTube only (one home rule), so the main button goes to the
  To Those Who Served video. Second button: the Substack, where Dom's grandfather's
  story (Army, Korean War), "He couldn't come home", is up now.
- The only lyric quoted is "You shouldn't stand alone." No veteran stories are invented.
- Veterans Crisis Line (US): dial 988 then press 1, or text 838255.

To take it down later, remove this script's line from build_site.py and rebuild.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
MARK = '<!-- VETERANS: top of home (Dom, Nov 9, 2026) -->'

SECTION = MARK + '''
<section aria-label="To Those Who Served" class="vets" id="veterans">
<style>
.vets{background:radial-gradient(120% 90% at 85% 0%,rgba(215,25,32,.22),rgba(8,9,12,0) 60%),linear-gradient(180deg,#0d0e12,var(--obsidian));border-bottom:1px solid var(--line)}
.vets .v-grid{display:grid;gap:clamp(22px,4vw,48px);grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);align-items:start}
.vets h1.giant{font-size:clamp(48px,6.4vw,92px);line-height:.86;margin:0}
.screen .hw h2.giant{font-family:var(--display);text-transform:uppercase;font-size:clamp(44px,5.6vw,80px);line-height:.82;letter-spacing:.005em;margin:0}
.screen .hw h2 .heart{font-style:italic;display:inline-block;transform:skewX(-8deg)}
.vets .v-lede{color:var(--silverw);font-size:clamp(17px,1.6vw,21px);line-height:1.5;max-width:40ch;margin:18px 0 0}
.vets blockquote{margin:22px 0 0;font-family:var(--display);text-transform:uppercase;font-size:clamp(28px,3.6vw,48px);line-height:1;color:var(--silverw)}
.vets blockquote::before{content:"\\201C";color:var(--red)}
.vets blockquote::after{content:"\\201D";color:var(--red)}
.vets .v-cite{margin:8px 0 0}
.vets .row{margin-top:24px}
.vets .v-side{display:grid;gap:14px}
.vets .v-side .panel{padding:18px 20px;border:1px solid var(--line)}
.vets .v-side p{margin:6px 0 0;color:var(--silver);line-height:1.5}
.vets .v-side b{color:var(--silverw)}
.vets .v-side a{color:var(--silverw)}
.vets .v-tags{margin:20px 0 0;color:var(--mute)}
@media (max-width:820px){.vets .v-grid{grid-template-columns:1fr}}
</style>
<div class="wrap">
<div class="v-grid">
<div>
<p class="mono" style="margin:0 0 14px"><b class="red">Veterans Day</b> · Wednesday, Nov 11</p>
<h1 class="giant"><span class="chrome">To Those</span><br/><span class="red">Who Served.</span></h1>
<p class="v-lede">Thank you. For those who served, and for everything they still carry. This song looks beyond the uniform, with gratitude, room for complicated feelings, and care that continues after the speeches end.</p>
<blockquote>You shouldn’t stand alone.</blockquote>
<p class="mono v-cite">To Those Who Served · GhostHeart</p>
<div class="row">
<a class="btn red" href="https://www.youtube.com/watch?v=U0X6SwISG_M" rel="noopener" target="_blank">Watch on YouTube ↗</a>
<a class="btn ghost" href="https://toohumantostayquiet.substack.com/p/he-couldnt-come-home" rel="noopener" target="_blank">Read on Substack ↗</a>
</div>
</div>
<div class="v-side">
<div class="panel"><p class="mono" style="margin:0">More than just today</p><p>Make the thank you last past Wednesday. <b>Check in. Listen. Share a meal.</b></p></div>
<div class="panel"><p class="mono" style="margin:0">My grandfather’s story</p><p>He served in the Army in the Korean War. His story is up now on Too Human to Stay Quiet: <a href="https://toohumantostayquiet.substack.com/p/he-couldnt-come-home" rel="noopener" target="_blank">He couldn’t come home</a>.</p></div>
<div class="panel"><p class="mono" style="margin:0">If you are carrying it alone</p><p>Veterans Crisis Line, free and 24/7: <b>dial 988, then press 1</b>, or <b>text 838255</b>. <a href="/GhostHeart_Resources.html">More support</a></p></div>
</div>
</div>
<p class="mono v-tags">#ToThoseWhoServed · #WakeTheHeart · #GhostHeartStudios</p>
</div>
</section>
'''

ANCHOR = '<div class="view" data-view="home">\n'

TITLE = 'GhostHeart | To Those Who Served · Veterans Day'
DESC = ('To Those Who Served: a Veterans Day thank you song from GhostHeart. '
        'For those who served, and for everything they still carry. Watch on YouTube.')



def main() -> None:
    s = HOME.read_text(encoding='utf-8')
    t = s
    if MARK not in t:
        assert t.count(ANCHOR) == 1, 'home view anchor not found'
        t = t.replace(ANCHOR, ANCHOR + SECTION, 1)
    t = t.replace('<title>GhostHeart | The Heart Wakes</title>', f'<title>{TITLE}</title>')
    for attr, value in (('property="og:title"', TITLE), ('name="description"', DESC), ('property="og:description"', DESC)):
        t, n = re.subn(r'<meta ' + re.escape(attr) + r' content="[^"]*"', f'<meta {attr} content="{value}"', t, count=1)
        assert n == 1, attr
    # The Heart Wakes hero is no longer the first heading, so it steps down to h2 (one h1 per page).
    t = t.replace('<h1 class="giant"><span class="chrome">The Heart</span><br/><span class="heart">Wakes.</span></h1>',
                  '<h2 class="giant"><span class="chrome">The Heart</span><br/><span class="heart">Wakes.</span></h2>')
    if t != s:
        HOME.write_text(t, encoding='utf-8')
    assert t.count('id="veterans"') == 1 and t.count('<h1') == 1 and f'<title>{TITLE}</title>' in t
    print('Home page opens with To Those Who Served for veterans.')


main()
