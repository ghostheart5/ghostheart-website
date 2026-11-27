#!/usr/bin/env python3
"""Site grade fixes (Dom, Nov 26, 2026: myghostheart.com graded 75, C, rejected; seven fixes).

Runs after apply_social_links.py in build_site.py, before the size caps, Google Analytics, meta and
sitemap steps. The content that lives in a source part was changed there instead:
.github/new-home/work.part, projects.part and vault-videos.part.

1. The veterans song comes off the site: the week list, Music, the Vault songs and lyrics, the
   merch view, Work with GhostHeart and Projects. When It Isn't Your Kitchen is the finished-work
   example instead. (The Veterans filter and the Veterans Crisis Line on Find Support stay: those
   are help lines, not the song. Dom decides.)
2. Too Small in the Vault links to the public video (-ZtyZCxKBM8), the same one Home uses.
3. The campaign is the final plan: 24 weeks, Nov 9 to Apr 19 (plan doc, Nov 24, 2026). Week 1 is
   The Heart Wakes. Too Small "is on YouTube now", not "comes Nov 25".
4. Lives come off the site: the Live tab, the Sunday Live blocks, and /live/ forwards to Home.
5. Sign-up boxes keep collecting emails (Dom, Nov 26: "STILL COLLECT EMAILS") but no longer
   promise emails, since email is off the plan. Enter My World's "Get email updates" goes to the
   sign-up box on Home.
6. Films lists the real videos with direct links; Music lists them too; the empty Blog leaves the
   menus (the page stays for old links).
7. Phones get a Menu button on every page (CSS in .github/new-home/home.css and
   assets/new-look/pages.css; the Home button is added here).

Idempotent: every change checks before it applies. To undo, remove this script's line from
build_site.py, revert the three parts and the two stylesheets, and rebuild.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARK = '<!-- GRADE FIXES (Dom, Nov 26, 2026) -->'
SKIP = ('.git/', '.github/', 'ghostheart-website/', 'node_modules/')

KITCHEN = 'https://www.youtube.com/watch?v=z00btt9OHWg'
TOO_SMALL = 'https://www.youtube.com/watch?v=-ZtyZCxKBM8'
VIDEOS = [  # every line here is already on the site (Home, the Vault)
    ('When It Isn’t Your Kitchen', KITCHEN, 'It follows a mother whose husband is admired all over town.'),
    ('Too Small', TOO_SMALL, 'Told through the eyes of a little boy in a house that does not feel safe.'),
    ('The Parts You Hide', 'https://www.youtube.com/watch?v=XfF_B-_ZNxM', 'A Country and Americana song, released for Trans Awareness Week.'),
    ('The Man Beneath the Moon', 'https://www.youtube.com/watch?v=l_ftyUginiA', 'Back as a new music video.'),
]
SIGNUP_NOTE = 'Add your email to join the Silver Thread. You get one welcome note to confirm it, nothing else is planned. Leave anytime.'


# The song's name is never written in this repo (Dom: off "everywhere"); the older build steps call it
# "The Tribute Song" and this step removes that too. The guard below reads the real name from base64.
import base64
REAL = base64.b64decode('VG8gVGhvc2UgV2hvIFNlcnZlZA==').decode().lower()


def named(text):
    low = text.lower()
    return REAL in low or REAL.replace(' ', '-') in low or 'tribute song' in low or 'tribute-song' in low


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')


def sub(text, old, new, what, count=1):
    if old not in text and new in text:
        return text
    assert text.count(old) == count, f'{what}: expected {count}, found {text.count(old)}'
    return text.replace(old, new)


def pages():
    for p in sorted(ROOT.rglob('*.html')):
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(SKIP):
            yield rel


# ---------- 4 and 6: Lives and Blog leave every menu and footer ----------
LINK_RE = re.compile(r'<a (?:aria-current="page" )?href="(?:(?:\.\./)+|/)?(?:live/|#live|journal/)"(?: data-nav="live")?>(?:Lives?|Blog)</a>\n?')
for rel in pages():
    t = read(rel)
    n = LINK_RE.sub('', t)
    if n != t:
        write(rel, n)

# ---------- 4: /live/ forwards to Home ----------
write('live/index.html', '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>GhostHeart</title>
<meta name="description" content="This page has moved to the GhostHeart home page."/>
<meta name="robots" content="noindex"/>
<link rel="canonical" href="https://www.myghostheart.com/">
<meta http-equiv="refresh" content="0; url=/"/>
<style>body{background:#000;color:#e6e6e6;font:16px/1.5 system-ui,sans-serif;margin:0;padding:40px 16px}a{color:#F4483C}</style>
</head>
<body>
<h1>This page has moved.</h1>
<p><a href="/">Go to the home page</a>.</p>
</body>
</html>
''')

# ---------- the shared script: weeks, songs, lyrics ----------
JS = 'assets/wake-v3/site.js'
js = read(JS)
WEEKS = [  # final plan (doc "Wake the Heart: lighter plan, one song a week", Nov 24, 2026)
    ('The Heart Wakes', '2026-11-08', ',at:"2026-11-09 12:00",songs:["The Heart Wakes"],cover:"/assets/wake-v3/img/heart-wakes.jpg",color:"var(--song-heartwakes)"'),
    ('The Parts You Hide', '2026-11-15', ',soon:["2026-11-16 00:00","Out Monday, Nov 16"],note:"For Trans Awareness Week. Your story. Your timing. The Man Beneath the Moon is back as a new music video."'),
    ('When It Isn’t Your Kitchen', '2026-11-22', ',soon:["2026-11-23 16:00","Music video Monday, Nov 23, 4 PM Central"],note:"If home does not feel safe, you do not have to carry it alone. Too Small is on YouTube now."'),
    ('Why Didn’t You Call', '2026-11-29', ',soon:["2026-11-30 16:00","Music video Monday, Nov 30, 4 PM Central"],note:"For Grief Awareness Week. If someone’s on your mind, call them. If you are struggling, call or text 988."'),
    ('Freedom Belongs to Everyone', '2026-12-06', ''),
    ('Heart Before Law', '2026-12-13', ''),
    ('The Lights Don’t Reach Every House', '2026-12-20', ',songs:["The Lights Don’t Reach Every House","Still"],color:"var(--song-still)"'),
    ('Still Me', '2026-12-27', ''),
    ('Letters to My Younger Self', '2027-01-03', ''),
    ('What Did You Take From Her?', '2027-01-10', ''),
    ('Stand Up for Somebody', '2027-01-17', ''),
    ('Every Life Has a Name', '2027-01-24', ''),
    ('Against the World', '2027-01-31', ''),
    ('Love Makes Me Braver', '2027-02-07', ''),
    ('A Kinder Tomorrow', '2027-02-14', ''),
    ('One Side of the Story', '2027-02-21', ''),
    ('Still Here', '2027-02-28', ''),
    ('Watch Me Anyway', '2027-03-07', ''),
    ('The Heart That Fought for Me', '2027-03-14', ''),
    ('What Saved You', '2027-03-21', ''),
    ('Invisible Crown', '2027-03-28', ''),
    ('Listen to the Kids', '2027-04-04', ''),
    ('Home Got There First', '2027-04-11', ''),
    ('Carry the Light', '2027-04-18', ''),
]


def week_line(name, up, extra):
    from datetime import date, timedelta
    d = date.fromisoformat(up)
    return f'    {{nm:"{name}",up:"{up}",a:"{d + timedelta(days=1)}",b:"{d + timedelta(days=7)}"{extra}}}'


weeks_js = 'var WEEKS=[\n' + ',\n'.join(week_line(*w) for w in WEEKS) + '\n  ];'
js = re.sub(r'var WEEKS=\[.*?\n  \];', lambda m: weeks_js, js, count=1, flags=re.S)
js = sub(js, '"The Tribute Song":"/assets/wake-v3/audio/the-tribute-song.mp3"', '', 'audio map')
js = js.replace('"/assets/wake-v3/audio/the-heart-wakes.mp3",}', '"/assets/wake-v3/audio/the-heart-wakes.mp3"}').replace('the-heart-wakes.mp3",};', 'the-heart-wakes.mp3"};')
js = js.replace(', "The Tribute Song": ""', '')
js = js.replace(',\n    "The Tribute Song":"A tribute song."', '')
js = sub(js, "' of 14 · '", "' of '+WEEKS.length+' · '", 'week of N')
js = sub(js, 'var left=13-feat;', 'var left=WEEKS.length-1-feat;', 'weeks left')
js = sub(js, '"All 14 weeks are open"', '"All "+WEEKS.length+" weeks are open"', 'all weeks open')
js = sub(js, '// Journey tracker: 14 slots;', '// Journey tracker: one slot per week;', 'tracker comment')
js = sub(js, "They open one Sunday night at a time. Add your thread to hear about the next one first.", "They open one Sunday night at a time.", 'locked weeks')
js = sub(js, 's.textContent="Opening Mailchimp to finish joining."', 's.textContent="Opening Mailchimp to finish adding your thread."', 'signup status')
assert not named(js), 'site.js still names the song'
assert js.count('{nm:') == 24
write(JS, js)

# ---------- Wake the Heart page ----------
W = 'wake-the-heart/index.html'
t = read(W)
t = t.replace('fourteen weeks of songs about the things we carry, opening one Sunday night at a time, Nov 9 to Feb 8',
              'twenty-four weeks of songs about the things we carry, opening one Sunday night at a time, Nov 9 to Apr 19')
t = sub(t, '<span class="stamp">14 weeks · Nov 9 to Feb 8</span>', '<span class="stamp">24 weeks · Nov 9 to Apr 19</span>', 'wake stamp')
t = sub(t, 'Across fourteen weeks, I’m sharing', 'Across twenty-four weeks, I’m sharing', 'wake lead')
t = sub(t, 'aria-label="The fourteen weeks"', 'aria-label="The weeks"', 'wake track label')
t = re.sub(r'<!-- NEXT LIVE -->\n<section class="nextlive">.*?</section>\n', '', t, count=1, flags=re.S)
t = sub(t, 'Join by email and you’ll get a note every Sunday night when the next week opens, with its songs, plus a reminder before each Sunday Live.', SIGNUP_NOTE, 'wake signup words')
t = sub(t, '>Join by email</button>', '>Add my thread</button>', 'wake signup button')
t = sub(t, 'Email only. Free. Unsubscribe anytime. Mailchimp handles signup.', 'Free. Mailchimp keeps the list.', 'wake signup fine print')
assert 'nextlive' not in t and 'Sunday Live' not in t and '14 weeks' not in t
write(W, t)

# ---------- Music: the album, then the songs out as videos ----------
M = 'music/index.html'
t = read(M)
if 'id="music-videos"' not in t:
    items = ''.join(f'<li><b>{n}</b><p class="why-song">{why}</p><a class="btn ghost" href="{u}" rel="noopener" target="_blank">Watch on YouTube ↗</a></li>'
                    for n, u, why in VIDEOS)
    block = ('<section id="music-videos">\n<div class="wrap">\n<p class="mono" style="margin:0 0 12px">More songs</p>\n'
             '<h2 class="giant"><span class="chrome">Out as</span> <span class="red">videos.</span></h2>\n'
             f'<ul class="songlist">{items}</ul>\n</div>\n</section>\n')
    t = sub(t, '</section>\n</div>\n</main>', '</section>\n' + block + '</div>\n</main>', 'music end')
write(M, t)

# ---------- Films: every video, each with its own link ----------
F = 'GhostHeart_Videos.html'
t = read(F)
if 'id="film-kitchen"' not in t:
    ids = ['film-kitchen', 'film-too-small', 'film-the-parts-you-hide', 'film-the-man-beneath-the-moon']
    cards = ''.join(f'<article class="film panel" id="{i}"><div><p class="mono k">Music video</p><h3>{n}</h3><p>{why}</p>'
                    f'<div class="row"><a class="btn red" href="{u}" rel="noopener" target="_blank">Watch on YouTube ↗</a></div></div></article>'
                    for i, (n, u, why) in zip(ids, VIDEOS))
    t = sub(t, '<div class="films">\n', '<div class="films">\n' + cards, 'films list')
    t = sub(t, '<p>Films from The Heart Wakes, one week at a time.</p>', '<p>Every GhostHeart music video, with a link straight to it.</p>', 'films lead')
write(F, t)

# ---------- Enter My World: the email link goes to the sign-up box ----------
S = 'GhostHeart_Story.html'
t = read(S)
t = sub(t, '<a class="btn ghost" href="/follow/">Get email updates</a>', '<a class="btn ghost" href="/#thread">Add your thread</a>', 'story email link')
write(S, t)

# ---------- Stay Connected ----------
FO = 'follow/index.html'
t = read(FO)
t = sub(t, '<span>First moments, and the Sunday Lives.</span>', '<span>First moments from every song.</span>', 'follow tiktok line')
write(FO, t)

# ---------- Work with GhostHeart: the custom song example ----------
H = 'here-to-help/index.html'
t = read(H)
t = re.sub(r'Hear one I made: <a [^>]*href="https://www\.youtube\.com/watch\?v=U0X6SwISG_M"[^>]*>The Tribute Song ↗</a>\. I wrote it, produced it and made its music video\.',
           f'Hear one of my songs: <a href="{KITCHEN}" rel="noopener" target="_blank">When It Isn’t Your Kitchen ↗</a>.', t, count=1)
write(H, t)

# ---------- Home ----------
HOME = 'index.html'
t = read(HOME)
if MARK not in t:
    # 3. the campaign line
    t = sub(t, '<b>Wake the Heart</b> · 14 weeks · Nov 9 to Feb 8</p>', '<b>Wake the Heart</b> · 24 weeks · Nov 9 to Apr 19</p>', 'home campaign line')
    t = sub(t, '>The 14 weeks</a>', '>The 24 weeks</a>', 'home weeks button')
    # 2 and 3. Too Small is out, with its working link
    t = re.sub(r'<b>Too Small</b> comes to YouTube on Wednesday, Nov 25, at 4 PM Central\. <a href="[^"]*"([^>]*) data-week3-song>[^<]*</a>',
               f'<b>Too Small</b> is on YouTube now. <a href="{TOO_SMALL}"\\1 data-week3-song>Watch it on YouTube ↗</a>', t, count=1)
    # 4. the Sunday Live block; the Live view can no longer be opened
    t = re.sub(r'<section class="fire2">.*?</section>\s*<div class="hazard red" aria-hidden="true"></div>\s*', '', t, count=1, flags=re.S)
    t = sub(t, 'var VIEWS=["home","vault","story","live","merch"];', 'var VIEWS=["home","vault","story","merch"];', 'home views')
    # 5. the sign-up words
    t = t.replace('Every person who takes a seat adds a silver thread to the heart. Email only. New songs, new work from the studio, and every Sunday Live. Leave anytime.',
                  'Every person who takes a seat adds a silver thread to the heart. You get one welcome note to confirm it, nothing else is planned. Leave anytime.')
    # 1. the Vault songs, lyrics and the merch card
    t = re.sub(r',\n  \{f:"the-tribute-song"[^\n]*\}\]\}\];', ']}];', t, count=1)
    t = t.replace(', "The Tribute Song": ""', '')
    t = sub(t, '/^(the-heart-wakes|the-tribute-song)$/', '/^(the-heart-wakes)$/', 'vault audio path')
    t = sub(t, 'var MOODS=[["","Everything"],["love","I’m thinking about love"],["protect","I want to look out for someone"]];',
            'var MOODS=[["","Everything"],["love","I’m thinking about love"]];', 'vault moods')
    t = re.sub(r'<article class="m-card"><div class="m-art"><img src="/assets/protector/merch-tribute\.jpg".*?</article>\s*', '', t, count=1, flags=re.S)
    t = sub(t, 'Seven designs, twenty-four pieces.', 'Six designs, nineteen pieces.', 'merch count')
    # 7. the phone Menu button
    t = sub(t, '<nav class="nav" aria-label="Main">',
            '<button class="menu-btn" id="nh-menu-btn" type="button" aria-controls="nh-nav" aria-expanded="false">Menu</button>\n'
            '  <nav class="nav" id="nh-nav" aria-label="Main">', 'home menu')
    t = sub(t, '</body>', MARK + '''
<script>
(function(){var b=document.getElementById("nh-menu-btn"),n=document.getElementById("nh-nav");if(!b||!n)return;
  function set(o){n.classList.toggle("open",o);b.setAttribute("aria-expanded",o?"true":"false")}
  b.addEventListener("click",function(){set(!n.classList.contains("open"))});
  n.addEventListener("click",function(e){if(e.target.closest("a"))set(false)});})();
</script>
</body>''', 'home end')
    write(HOME, t)

# ---------- checks on every page a visitor can reach from the menu ----------
TAGS = re.compile(r'<[^>]+>')
for rel in pages():
    t = read(rel)
    if 'http-equiv="refresh"' in t:
        continue
    words = ' '.join(TAGS.sub(' ', re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S)).split())
    assert not named(t), f'{rel}: still names the tribute song'
    assert 'U0X6SwISG_M' not in t and 'UTvuIgq-AWI' not in t, f'{rel}: old video link'
    assert not re.search(r'Sunday Lives?\b', words), f'{rel}: still mentions the Sunday Live'
    assert '14 weeks' not in words and 'Nov 9 to Feb 8' not in words, f'{rel}: old campaign dates'
    assert 'Too Small comes' not in t, rel
    assert not LINK_RE.search(t), f'{rel}: Live or Blog link left'
print('Grade fixes: veterans song off, Too Small link, 24 weeks to Apr 19, Lives off, sign-up words, Films and Music filled, Blog out of menus, phone Menu.')
