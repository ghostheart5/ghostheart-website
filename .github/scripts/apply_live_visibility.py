#!/usr/bin/env python3
"""Apply the temporary public Live pause without deleting event sources."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LIVE = json.loads((ROOT / '.github/content/live.json').read_text(encoding='utf-8'))

def apply():
    if LIVE.get('public_enabled', True):
        return
    for path in ROOT.rglob('*.html'):
        if '.git' in path.parts or '.github' in path.parts:
            continue
        old = path.read_text(encoding='utf-8')
        new = old
        if path.relative_to(ROOT).as_posix() == 'live/index.html':
            new = re.sub(r'<main\b.*?</main>', '''<main id="main-content"><div class="ghx-wrap readings-page">
<h1>Live sessions</h1><p class="ghx-lead">No Live sessions are currently scheduled.</p>
<p><a href="/GhostHeart_Story.html">Enter My World</a> or <a href="/journal/">read the Blog</a>.</p>
</div></main>''', new, count=1, flags=re.S)
            new = new.replace('<title>Readings | GhostHeart</title>', '<title>Live sessions | GhostHeart</title>')
            new = new.replace('Readings and Sunday Live updates from GhostHeart.', 'No Live sessions are currently scheduled.')
        if path.relative_to(ROOT).as_posix() == 'live/my-promise.html':
            new = re.sub(r'<a class="reading-back" href="/live/">.*?</a>', '<a class="reading-back" href="/GhostHeart_Story.html">Enter My World</a>', new)
            new = new.replace('<a href="/live/">Return to Readings &amp; Live</a>', '<a href="/GhostHeart_Story.html">Return to My World</a>')
        new = re.sub(r'<article\b[^>]*\bid="home-lives"[^>]*>.*?</article>', '', new, flags=re.S)
        new = re.sub(r'<section\b[^>]*class="journal-highlight journal-live"[^>]*>.*?</section>', '', new, flags=re.S)
        new = re.sub(r'<p\b[^>]*>\s*<strong>Next Sunday Live:</strong>.*?</p>', '', new, flags=re.S)
        new = new.replace('The next planned Sunday Live is October 11, 2026 at 10:00 a.m. Central. The viewing platform and link are pending.', '')
        new = new.replace('<p class="ghx-kicker">Readings &amp; Live</p>', '<p class="ghx-kicker">Reading</p>')
        new = new.replace(' Sunday readings will connect selected pages to the work unfolding around them; reading details will be announced when they are confirmed.', '')
        # Only the Live entry route: keep the independently approved My Promise reading.
        new = re.sub(r'<a\b[^>]*href="(?:/|\../)*live/(?:index\.html)?"[^>]*>.*?</a>', '', new, flags=re.S)
        if new != old:
            path.write_text(new, encoding='utf-8', newline='\n')
    sitemap = ROOT / 'sitemap.xml'
    value = sitemap.read_text(encoding='utf-8')
    value = re.sub(r'\s*<url>\s*<loc>https://www\.myghostheart\.com/live/</loc>.*?</url>', '', value, flags=re.S)
    sitemap.write_text(value, encoding='utf-8', newline='\n')
    feed = ROOT / 'journal/feed.xml'
    feed_text = feed.read_text(encoding='utf-8')
    feed_text = feed_text.replace(' Sunday readings will connect selected pages to the work unfolding around them; reading details will be announced when they are confirmed.', '')
    feed.write_text(feed_text, encoding='utf-8', newline='\n')
    print('Applied temporary Live visibility pause; source event details preserved.')

if __name__ == '__main__':
    apply()
