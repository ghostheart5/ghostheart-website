#!/usr/bin/env python3
"""Owner decision 2026-11-01: the page is just "Lives". Readings (My Promise) come off the site.

Runs last in build_site.py. The My Promise text stays in .github/content/my-promise.txt
so it can come back later, but no page is published for it and nothing links to it.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

AWAKENING_NEXT = ('<section aria-labelledby="awakening-next" class="world-finish ghx-wrap"><div>'
    '<p class="ghx-kicker">Sunday Lives</p><h2 id="awakening-next">Come to a Sunday Live.</h2>'
    '<p>Every Sunday at 10:00 a.m. Central on TikTok.</p></div>'
    '<nav aria-label="Continue The Awakening"><a href="/live/">See the next Live</a>'
    '<a href="/vault/">Explore GhostHeart\'s Vault</a></nav></section>')

def clean(text):
    text = re.sub(r'<section aria-labelledby="awakening-next".*?</section>', AWAKENING_NEXT, text, flags=re.S)
    text = re.sub(r'<a\b[^>]*href="(?:https://www\.myghostheart\.com)?/live/my-promise\.html"[^>]*>.*?</a>', '', text, flags=re.S)
    text = text.replace('Readings &amp; Live details', 'Sunday Lives')
    text = text.replace('Lives &amp;amp; Readings', 'Lives')
    text = text.replace('Lives &amp; Readings', 'Lives')
    text = text.replace('Readings &amp; Live', 'Lives')
    return text

def apply():
    promise = ROOT / 'live/my-promise.html'
    if promise.exists():
        promise.unlink()
    for path in list(ROOT.rglob('*.html')) + [ROOT / 'journal/feed.xml']:
        if '.git' in path.parts or '.github' in path.parts or not path.exists():
            continue
        old = path.read_text(encoding='utf-8')
        new = clean(old)
        if new != old:
            path.write_text(new, encoding='utf-8', newline='\n')
    sitemap = ROOT / 'sitemap.xml'
    value = sitemap.read_text(encoding='utf-8')
    value = re.sub(r'\s*<url>\s*<loc>https://www\.myghostheart\.com/live/my-promise\.html</loc>.*?</url>', '', value, flags=re.S)
    sitemap.write_text(value, encoding='utf-8', newline='\n')
    print('Lives only: page named "Lives", readings removed.')

if __name__ == '__main__':
    apply()
