#!/usr/bin/env python3
"""Website without the Wake the Heart campaign (Dom, Nov 8, 2026).

Dom: "the website should not have anything to do with the Wake the Heart campaign." He picked: keep the new site
look and the album The Heart Wakes as music; take out only the campaign pieces. Runs last in build_site.py.

- the "Wake the Heart" link in every page's menu and footer (the footer group "Campaign" becomes "More")
- /wake-the-heart/ and the "Wake the Heart Week" journal post become small pages that send people on
  (to /music/ and /journal/), so old links and posts never land on a dead page
- the home page's campaign line, "14 weeks" button and stamp, and the old "The Awakening ... Wake the Heart" line
- campaign words in page descriptions and the Lives signup line
The album's own weekly song release (home "Featured week", Music page) stays: that is the music, not the campaign.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://www.myghostheart.com'

LINK = re.compile(r'\s*<a(?: aria-current="page")? href="/wake-the-heart/">Wake the Heart</a>')

HOME_CUTS = [
    re.compile(r'<p class="mono" style="margin:0 0 14px"><b class="red">Wake the Heart</b> · the campaign · 14 weeks, Nov 9 to Feb 8</p>\s*'),
    re.compile(r'\s*<a class="btn" href="/wake-the-heart/">14 weeks</a>'),
    re.compile(r'\s*<span class="stamp"[^>]*>14 weeks</span>'),
    re.compile(r'\s*<p class="last">The Awakening introduced the heart\. Wake the Heart gives it power\.</p>'),
]
HOME_DESC = ('GhostHeart: Wake the Heart, fourteen weeks of new songs from the album The Heart Wakes, Nov 9 to Feb 8. '
             'Music, films, Sunday Lives and stories.')
HOME_DESC_NEW = 'GhostHeart: The Heart Wakes, the new album, opening one week at a time. Music, films, Sunday Lives and stories.'

JOURNAL_ITEM = re.compile(r'<li class="nb-item" data-typ="news" id="e-wth-week">.*?</li>(?=\s*(?:<li class="nb-item"|</ol>))', re.S)

FORWARD = '''<!doctype html>
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


def pages():
    for p in ROOT.rglob('*.html'):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(('.github/', 'node_modules/')) or '/node_modules/' in rel:
            continue
        yield p


def forward(rel: str, to: str, label: str) -> None:
    p = ROOT / rel
    if p.exists():
        p.write_text(FORWARD.format(site=SITE, to=to, label=label), encoding='utf-8')


def main() -> None:
    changed = 0
    for p in pages():
        s = p.read_text(encoding='utf-8')
        t = LINK.sub('', s)
        t = t.replace('<p class="foot-h">Campaign</p>', '<p class="foot-h">More</p>')
        t = t.replace('plus each new week of Wake the Heart.', 'plus each new week of The Heart Wakes.')
        if p == ROOT / 'index.html':
            for cut in HOME_CUTS:
                t = cut.sub('', t, count=1)
            t = t.replace(HOME_DESC, HOME_DESC_NEW)
        if p == ROOT / 'journal/index.html':
            t = JOURNAL_ITEM.sub('', t, count=1)
        if t != s:
            p.write_text(t, encoding='utf-8')
            changed += 1
    forward('wake-the-heart/index.html', '/music/', 'Music')
    forward('journal/wake-the-heart-week.html', '/journal/', 'the Notebook')
    feed = ROOT / 'journal/feed.xml'
    if feed.exists():
        s = feed.read_text(encoding='utf-8')
        t = re.sub(r'\s*<item>\s*<title>Wake the Heart Week</title>.*?</item>', '', s, count=1, flags=re.S)
        if t != s:
            feed.write_text(t, encoding='utf-8')
    sm = ROOT / 'sitemap.xml'
    if sm.exists():
        s = sm.read_text(encoding='utf-8')
        t = re.sub(r'\s*<url>\s*<loc>' + re.escape(SITE) + r'/(?:wake-the-heart/|journal/wake-the-heart-week\.html)</loc>.*?</url>', '', s, flags=re.S)
        if t != s:
            sm.write_text(t, encoding='utf-8')
    # Nothing left that sends people to the campaign.
    for p in pages():
        rel = p.relative_to(ROOT).as_posix()
        if rel in ('wake-the-heart/index.html', 'journal/wake-the-heart-week.html'):
            continue
        s = p.read_text(encoding='utf-8')
        assert 'href="/wake-the-heart/' not in s and 'wake-the-heart-week' not in s, rel
    if feed.exists():
        assert 'wake-the-heart-week' not in feed.read_text(encoding='utf-8'), 'journal/feed.xml'
    print(f'Campaign pieces removed from {changed} pages; /wake-the-heart/ now goes to /music/.')


main()
