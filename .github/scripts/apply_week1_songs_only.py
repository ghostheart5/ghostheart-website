#!/usr/bin/env python3
"""Wake the Heart site with only Week 1's songs (Dom, Nov 8, 2026). Runs after apply_no_awakening.py.

Dom: "release the entire site and 1st weeks songs. the wake the heart is the campaign album song. to those who served
is the week song. no other song should be listed, the entire website protype was already completed"

- The campaign pieces of the confirmed prototype stay on (apply_no_campaign.py is gone): menu link, /wake-the-heart/,
  the home campaign line. The old Oct 30 "Wake the Heart Week" post was about the retired album, so it still forwards.
- Music lists only The Heart Wakes album songs as their week opens (Week 1: The Heart Wakes, To Those Who Served).
  The "Where it started" and "You're Not God" song lists leave the Music page.

Dom, Nov 8 2026 (card "Should older songs also come off the rest of the site?"): "Take older songs off everywhere".
- Films: the twelve older films leave; the page points to The Heart Wakes premiere on YouTube.
- Blog: the seven entries about older songs leave; their posts and the Passages pages forward to the Blog.
- The older songs page and the old album pages forward to Music.
- Story, The Woman Behind the Scenes and the Heart Dial picks stop naming older songs.
Source files stay in the repo, so this can be undone by removing this step.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://www.myghostheart.com'
MAIN_PAGES = {'index.html', 'wake-the-heart/index.html', 'music/index.html', 'GhostHeart_Videos.html', 'live/index.html',
              'GhostHeart_Story.html', 'journal/index.html', 'vault/index.html', 'here-to-help/index.html',
              'GhostHeart_Projects.html', 'follow/index.html', 'GhostHeart_Resources.html', 'GhostHeart_Privacy.html',
              'woman-behind-the-scenes/index.html'}

OLD_LISTS = re.compile(r'\s*<section>\s*<div class="wrap cat">.*?</section>(?=\s*</div>\s*</main>)', re.S)

FORWARD_TO = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GhostHeart</title>
<meta name="description" content="This page has moved to {label} on myghostheart.com.">
<meta name="robots" content="noindex">
<link rel="canonical" href="{site}{to}">
<meta http-equiv="refresh" content="0; url={to}">
<style>body{{background:#000;color:#e6e6e6;font:16px/1.5 system-ui,sans-serif;margin:0;padding:40px 16px}}a{{color:#F4483C}}</style>
</head>
<body>
<h1>This page has moved.</h1>
<p><a href="{to}">Go to {label}</a>.</p>
</body>
</html>
'''

FORWARD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GhostHeart</title>
<meta name="description" content="This page has moved to the Notebook on myghostheart.com.">
<meta name="robots" content="noindex">
<link rel="canonical" href="{site}/journal/">
<meta http-equiv="refresh" content="0; url=/journal/">
<style>body{{background:#000;color:#e6e6e6;font:16px/1.5 system-ui,sans-serif;margin:0;padding:40px 16px}}a{{color:#F4483C}}</style>
</head>
<body>
<h1>This page has moved.</h1>
<p><a href="/journal/">Go to the Notebook</a>.</p>
</body>
</html>
'''
SONG_LINK = re.compile(r'((?:https://www\.myghostheart\.com)?(?:\.\./)*/?)music/#song-[a-z0-9-]+')
OLD_SONGS = ['Cruel', 'I’m Not', 'Papa Didn’t Raise No Fool', 'She Got to Me', 'This Is GhostHeart',
             'GhostHeart’s Oath', 'You Can Be GhostHeart Too', 'One Heart Many Voices',
             'I Won’t Pretend to Speak for You', 'Hey Preacher Man', 'That Ain’t Holy',
             'Human Too', 'HUMAN TOO', 'The Dad I Never Had', 'The Man Beneath the Moon', 'Just Not This Morning']
YOUTUBE = 'https://www.youtube.com/@GhostHeart-M95RTK'
FILMS = re.compile(r'(<div class="films">).*?(</div>\s*</div>\s*</section>)', re.S)
FILMS_NOW = ('<article class="film panel" id="film-the-heart-wakes"><div><p class="mono k">The Heart Wakes · first film</p>'
             '<h3>The Heart Wakes</h3><p>The first film from the new album premiered Monday, November 9 on YouTube.</p><div class="row"><a class="btn red" href="' + YOUTUBE + '" rel="noopener" '
             'target="_blank">GhostHeart on YouTube ↗</a><a class="btn ghost" href="/music/">Music</a></div></div></article>\n')
BLOG_LIST = re.compile(r'<ol class="nb">.*?</ol>', re.S)
BLOG_NOW = ('<div class="panel nb-empty" style="padding:18px"><p style="margin:0">New notes arrive with each week of '
            '<b>The Heart Wakes</b>. Week 1: The Heart Wakes and To Those Who Served.</p></div>')
BLOG_CHIPS = re.compile(r'\s*<div class="chips nb-chips">.*?</div>', re.S)
BLOG_NEXT = re.compile(r'\s*<div class="nb-next panel">.*?</div>', re.S)
TO_MUSIC = ['GhostHeart_Songs.html', 'assets/platforms/index.html', 'albums/ghostheart/index.html', 'albums/youre-not-god/index.html',
            'albums/youre-not-god/lyrics.html']
TO_BLOG = ['journal/cruel-something-needs-to-change.html', 'journal/ghosthearts-oath.html', 'journal/this-is-ghostheart.html',
           'journal/youre-not-god.html', 'journal/how-we-got-here-archive.html', 'passages/index.html', 'passages/im-not.html',
           'passages/its-not-the-1950s.html', 'passages/papa-didnt-raise-no-fool.html']
TEXT = {
    'GhostHeart_Story.html': [
        ('<a class="btn red" href="/GhostHeart_Videos.html">Watch This Is GhostHeart</a><a class="btn ghost" href="/GhostHeart_Videos.html">Watch GhostHeart’s Oath</a>',
         '<a class="btn red" href="/music/">Hear The Heart Wakes</a>'),
        ('<h2>Behind the Scars — Before the Heart Wakes</h2>', '<h2>Behind the Scars</h2>'),
    ],
    'woman-behind-the-scenes/index.html': [('<a href="/music/">Listen to She Got to Me</a>', '<a href="/music/">Hear The Heart Wakes</a>')],
    'GhostHeart_Videos.html': [('<p>Music videos, lyric videos and cinematic remakes. Twelve films. Pick one.</p>',
                                '<p>Films from The Heart Wakes, one week at a time.</p>')],
    'journal/index.html': [('<p style="color:var(--silver);max-width:60ch">The songs don’t tell you everything. Here I write about the thoughts behind them and the questions they leave with me.</p>',
                            '<p style="color:var(--silver);max-width:60ch">The songs don’t tell you everything. Here I write about the thoughts behind the songs of The Heart Wakes as each week opens.</p>')],
}
JOURNAL_ITEM = re.compile(r'<li class="nb-item" data-typ="news" id="e-wth-week">.*?</li>(?=\s*(?:<li class="nb-item"|</ol>))', re.S)


def main() -> None:
    music = ROOT / 'music/index.html'
    s = music.read_text(encoding='utf-8')
    t = OLD_LISTS.sub('', s, count=1)
    if t != s:
        music.write_text(t, encoding='utf-8')
    assert 'Where it started' not in t and 'class="tplay"' not in t and 'id="album-songs"' in t

    # Old links to a song on Music now land on Music itself.
    for f in list(ROOT.rglob('*.html')) + [ROOT / 'assets/data/for-you.js']:
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(('.github/', 'node_modules/')) or '/node_modules/' in rel or not f.exists():
            continue
        s = f.read_text(encoding='utf-8')
        t = SONG_LINK.sub(r'\1music/', s)
        if t != s:
            f.write_text(t, encoding='utf-8')

    # The Oct 30 "Wake the Heart Week" post described the retired album: keep it forwarding to the Notebook.
    (ROOT / 'journal/wake-the-heart-week.html').write_text(FORWARD.format(site=SITE), encoding='utf-8')
    j = ROOT / 'journal/index.html'
    s = j.read_text(encoding='utf-8')
    t = JOURNAL_ITEM.sub('', s, count=1)
    if t != s:
        j.write_text(t, encoding='utf-8')
    feed = ROOT / 'journal/feed.xml'
    if feed.exists():
        s = feed.read_text(encoding='utf-8')
        t = re.sub(r'\s*<item>\s*<title>Wake the Heart Week</title>.*?</item>', '', s, count=1, flags=re.S)
        if t != s:
            feed.write_text(t, encoding='utf-8')
    sm = ROOT / 'sitemap.xml'
    s = sm.read_text(encoding='utf-8')
    t = re.sub(r'\s*<url>\s*<loc>' + re.escape(SITE) + r'/journal/wake-the-heart-week\.html</loc>.*?</url>', '', s, flags=re.S)
    if t != s:
        sm.write_text(t, encoding='utf-8')

    # ---- Older songs off everywhere ----
    films = ROOT / 'GhostHeart_Videos.html'
    s = films.read_text(encoding='utf-8')
    t = FILMS.sub(lambda m: m.group(1) + '\n' + FILMS_NOW + m.group(2), s, count=1)
    films.write_text(t, encoding='utf-8')
    blog = ROOT / 'journal/index.html'
    s = blog.read_text(encoding='utf-8')
    t = BLOG_LIST.sub(BLOG_NOW, s, count=1)
    t = BLOG_CHIPS.sub('', t, count=1)
    t = BLOG_NEXT.sub('', t, count=1)
    blog.write_text(t, encoding='utf-8')
    mission = ROOT / 'GhostHeart_Version_Mission.html'  # "GhostHeart's Oath is the film that carries the promise."
    if mission.exists():
        s = mission.read_text(encoding='utf-8')
        t = re.sub(r'<section class="g-section g-dark"><div class="g-wrap"><h2>The promise\.</h2>.*?</section>', '', s, count=1, flags=re.S)
        if t != s:
            mission.write_text(t, encoding='utf-8')
    for rel, swaps in TEXT.items():
        f = ROOT / rel
        s = f.read_text(encoding='utf-8')
        t = s
        for old, new in swaps:
            t = t.replace(old, new)
        if t != s:
            f.write_text(t, encoding='utf-8')
    TO_MUSIC.extend(sorted(f.relative_to(ROOT).as_posix() for f in (ROOT / 'albums').glob('*/*.html')
                           if f.relative_to(ROOT).as_posix() not in TO_MUSIC))
    songs_targets = set()
    for f in ROOT.rglob('*.html'):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(('.github/', 'node_modules/')) or '/node_modules/' in rel:
            continue
        songs_targets.update(re.findall(r'GhostHeart_Songs\.html#([A-Za-z0-9_-]+)', f.read_text(encoding='utf-8')))
    for rel in TO_MUSIC:
        if (ROOT / rel).exists():
            page = FORWARD_TO.format(site=SITE, to='/music/', label='Music')
            if rel == 'GhostHeart_Songs.html':  # old deep links (e.g. #human-too) still land before the forward
                page = page.replace('<h1>', ''.join(f'<span id="{x}"></span>' for x in sorted(songs_targets)) + '<h1>', 1)
            (ROOT / rel).write_text(page, encoding='utf-8')
    for rel in TO_BLOG:
        if (ROOT / rel).exists():
            page = FORWARD_TO.format(site=SITE, to='/journal/', label='the Blog')
            if rel == 'passages/index.html':  # build_passages.py uses this page as its template (markers + <main>), also in its tests
                page = page.replace('<h1>', '<div hidden><main><!--PASSAGES-LIST:START-->\n<!--PASSAGES-LIST:END--></main></div>\n<h1>', 1)
            (ROOT / rel).write_text(page, encoding='utf-8')
    # Links straight to forwarded pages go to where they land.
    for f in ROOT.rglob('*.html'):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(('.github/', 'node_modules/')) or '/node_modules/' in rel:
            continue
        s = f.read_text(encoding='utf-8')
        t = re.sub(r'href="(?:https://www\.myghostheart\.com)?/passages/[^"]*"', 'href="/journal/"', s)
        t = re.sub(r'href="(?:https://www\.myghostheart\.com)?/journal/#e-[a-zA-Z-]+"', 'href="/journal/"', t)
        t = re.sub(r'href="/GhostHeart_Videos\.html#film-[a-z0-9-]+"', 'href="/GhostHeart_Videos.html"', t)
        if t != s:
            f.write_text(t, encoding='utf-8')
    feed = ROOT / 'journal/feed.xml'
    if feed.exists():
        s = feed.read_text(encoding='utf-8')
        t = s
        for rel in TO_BLOG:
            if rel.startswith('journal/'):
                t = re.sub(r'\s*<item>(?:(?!</item>).)*?' + re.escape(rel) + r'.*?</item>', '', t, flags=re.S)
        t = re.sub(r'\s*<item>(?:(?!</item>).)*?/passages/.*?</item>', '', t, flags=re.S)
        if t != s:
            feed.write_text(t, encoding='utf-8')
    sm = ROOT / 'sitemap.xml'
    s = sm.read_text(encoding='utf-8')
    for rel in TO_MUSIC + TO_BLOG:
        loc = SITE + '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)
        s = re.sub(r'\s*<url>\s*<loc>' + re.escape(loc) + r'</loc>.*?</url>', '', s, flags=re.S)
    sm.write_text(s, encoding='utf-8')
    sj = ROOT / 'assets/wake-v3/site.js'
    s = sj.read_text(encoding='utf-8')
    m = re.search(r'var FY=(\{.*?\});\n', s, re.S)
    fy = json.loads(m.group(1))
    fy['picks'] = [x for x in fy['picks'] if x['kind'] not in ('Film', 'Song', 'Blog', 'Passage', 'Short')]  # Shorts are clips of older songs
    t = s[:m.start(1)] + json.dumps(fy, ensure_ascii=False) + s[m.end(1):]
    t = t.replace('var SONG={4:{t:"Rebellion",u:"https://open.spotify.com/album/7jkKCwKlYjadMvBsJokvDq"}};', 'var SONG={};')
    if t != s:
        sj.write_text(t, encoding='utf-8')

    def shown(html):
        html = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
        return re.sub(r'<[^>]+>', ' ', html)
    for f in ROOT.rglob('*.html'):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(('.github/', 'node_modules/')) or '/node_modules/' in rel:
            continue
        v = shown(f.read_text(encoding='utf-8'))
        if 'http-equiv="refresh"' in f.read_text(encoding='utf-8')[:2000]:
            continue
        if rel.startswith('apps/'):  # app pages (e.g. the Love Is Not Rebellion app) are not song listings
            continue
        v = v.replace("'", '’')
        for name in OLD_SONGS:
            assert name not in v, (rel, name)
    picks = json.loads(re.search(r'var FY=(\{.*?\});\n', (ROOT / 'assets/wake-v3/site.js').read_text(encoding='utf-8'), re.S).group(1))['picks']
    assert picks and not any(x['title'] in OLD_SONGS or x['kind'] != 'Quote' for x in picks)

    js = (ROOT / 'assets/wake-v3/site.js').read_text(encoding='utf-8')
    assert 'var AUDIO={"The Heart Wakes":' in js and '"To Those Who Served":' in js
    assert 'href="/wake-the-heart/"' in (ROOT / 'index.html').read_text(encoding='utf-8')
    print('Wake the Heart on; only The Heart Wakes songs are listed (Week 1: The Heart Wakes, To Those Who Served); older songs, films and notes are off.')


main()
