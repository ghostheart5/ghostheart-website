#!/usr/bin/env python3
"""Wake the Heart site with only Week 1's songs (Dom, Nov 8, 2026). Runs after apply_no_awakening.py.

Dom: "release the entire site and 1st weeks songs. the wake the heart is the campaign album song. to those who served
is the week song. no other song should be listed, the entire website protype was already completed"

- The campaign pieces of the confirmed prototype stay on (apply_no_campaign.py is gone): menu link, /wake-the-heart/,
  the home campaign line. The old Oct 30 "Wake the Heart Week" post was about the retired album, so it still forwards.
- Music lists only The Heart Wakes album songs as their week opens (Week 1: The Heart Wakes, To Those Who Served).
  The "Where it started" and "You're Not God" song lists leave the Music page.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://www.myghostheart.com'

OLD_LISTS = re.compile(r'\s*<section>\s*<div class="wrap cat">.*?</section>(?=\s*</div>\s*</main>)', re.S)

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

    js = (ROOT / 'assets/wake-v3/site.js').read_text(encoding='utf-8')
    assert 'var AUDIO={"The Heart Wakes":' in js and '"To Those Who Served":' in js
    assert 'href="/wake-the-heart/"' in (ROOT / 'index.html').read_text(encoding='utf-8')
    print('Wake the Heart on; Music lists only The Heart Wakes songs as their week opens (Week 1: The Heart Wakes, To Those Who Served).')


main()
