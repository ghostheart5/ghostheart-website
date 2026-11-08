#!/usr/bin/env python3
"""Website without The Awakening (Dom, Nov 8, 2026).

Dom: "THE AWAKENING IS RETIRED" and "everything the awakening needs to be removed". The eight first songs stay as
music; only the Awakening name and its page go. Runs last in build_site.py, after apply_no_campaign.py.

- Music: the album block "GhostHeart's Awakening" becomes "Where it started"; the page description drops the name
- Films: the Cruel card says "Official music video" without the album name
- Heart Dial and For You picks: "From GhostHeart's Awakening." is dropped from the Cruel line
- /awakening/ (the old "Before the Heart Wakes" album page) becomes a small page that sends people to /music/,
  its menu link leaves every older page, and it leaves the sitemap
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://www.myghostheart.com'

MENU_LINK = re.compile(r'<a href="(?:/|(?:\.\./)*)awakening/">Before the Heart Wakes</a>')
TEXT = [
    ('<h3 class="chrome">GhostHeart’s Awakening</h3>', '<h3 class="chrome">Where it started</h3>'),
    ('<p class="sub">8 songs · where it started</p>', '<p class="sub">8 songs · the first GhostHeart songs</p>'),
    ('plus GhostHeart’s Awakening and You’re Not God.', 'plus the first GhostHeart songs and You’re Not God.'),
    ('GhostHeart’s Awakening · Official music video', 'Official music video'),
    # Home page campaign block (Wake the Heart is back on the site, Dom Nov 8 2026): drop the retired name only.
    ('<p class="last">The Awakening introduced the heart. Wake the Heart gives it power.</p>', ''),
    ('<a class="primary" href="/awakening/">Explore Before the Heart Wakes</a>', '<a class="primary" href="/music/">Hear The Heart Wakes</a>'),
]
JS = {
    'assets/wake-v3/site.js': [('From GhostHeart’s Awakening. Something needs to change.', 'Something needs to change.')],
    'assets/data/for-you.js': [('From GhostHeart’s Awakening. Something needs to change.', 'Something needs to change.')],
    'assets/data/ghostheart-video-catalog.js': [('"GhostHeart\'s Awakening",\n      "Official music video"', '"Official music video"')],
}

FORWARD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GhostHeart</title>
<meta name="description" content="This page has moved to Music on myghostheart.com.">
<meta name="robots" content="noindex">
<link rel="canonical" href="{site}/music/">
<meta http-equiv="refresh" content="0; url=/music/">
<style>body{{background:#000;color:#e6e6e6;font:16px/1.5 system-ui,sans-serif;margin:0;padding:40px 16px}}a{{color:#F4483C}}</style>
</head>
<body>
<h1>This page has moved.</h1>
<p><a href="/music/">Go to Music</a>.</p>
</body>
</html>
'''


def pages():
    for p in ROOT.rglob('*.html'):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(('.github/', 'node_modules/')) or '/node_modules/' in rel:
            continue
        yield p


def visible(html: str) -> str:
    html = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    return re.sub(r'<[^>]+>', ' ', html)


def main() -> None:
    changed = 0
    for p in pages():
        s = p.read_text(encoding='utf-8')
        t = MENU_LINK.sub('', s)
        for old, new in TEXT:
            t = t.replace(old, new)
        if t != s:
            p.write_text(t, encoding='utf-8')
            changed += 1
    for rel, swaps in JS.items():
        p = ROOT / rel
        if p.exists():
            s = p.read_text(encoding='utf-8')
            t = s
            for old, new in swaps:
                t = t.replace(old, new)
            if t != s:
                p.write_text(t, encoding='utf-8')
    page = ROOT / 'awakening/index.html'
    if page.exists():
        page.write_text(FORWARD.format(site=SITE), encoding='utf-8')
    sm = ROOT / 'sitemap.xml'
    if sm.exists():
        s = sm.read_text(encoding='utf-8')
        t = re.sub(r'\s*<url>\s*<loc>' + re.escape(SITE) + r'/awakening/</loc>.*?</url>', '', s, flags=re.S)
        if t != s:
            sm.write_text(t, encoding='utf-8')
    # Nothing a visitor reads still names The Awakening, and nothing links to its old page.
    for p in pages():
        rel = p.relative_to(ROOT).as_posix()
        s = p.read_text(encoding='utf-8')
        if rel != 'awakening/index.html':
            assert not re.search(r'href="(?:/|(?:\.\./)*|https://www\.myghostheart\.com/)awakening/"', s), rel
        assert 'Awakening' not in visible(s), rel
        for m in re.finditer(r'<meta [^>]*content="([^"]*)"', s):
            assert 'Awakening' not in m.group(1), rel
    for rel in JS:
        p = ROOT / rel
        if p.exists():
            s = p.read_text(encoding='utf-8')
            assert all(old not in s for old, _ in JS[rel]), rel
    print(f'Awakening name removed from {changed} pages; /awakening/ now goes to /music/.')


main()
