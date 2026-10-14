#!/usr/bin/env python3
"""Keep the Live pathway visible independently of an announced event."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LIVE = json.loads((ROOT / '.github/content/live.json').read_text(encoding='utf-8'))
PATH_VISIBLE = LIVE.get('public_path_enabled', False)

def apply():
    if LIVE.get('public_enabled', True):
        return
    for path in ROOT.rglob('*.html'):
        if '.git' in path.parts or '.github' in path.parts:
            continue
        old = path.read_text(encoding='utf-8')
        new = old
        if path.relative_to(ROOT).as_posix() == 'live/index.html':
            pending = '''<main id="main-content"><div class="ghx-wrap readings-page">
<p class="ghx-kicker">GhostHeart / Lives &amp; Readings</p><h1>Lives &amp; Readings.</h1>
<section class="readings-event" aria-labelledby="live-status-title"><h2 id="live-status-title">Next Live: announcement pending.</h2>
<p>No upcoming Live date or viewing link is confirmed yet.</p><p><a href="/follow/">Be Part of GhostHeart</a> for the announcement when details are ready.</p></section>
<section class="readings-event" aria-labelledby="promise-title"><p class="ghx-kicker">Read now</p><h2 id="promise-title">My Promise</h2><p>A promise to keep learning, listening, and choosing care.</p><a href="/live/my-promise.html">Read My Promise</a></section>
<p><a href="/GhostHeart_Story.html">Enter My World</a> or <a href="/journal/">read the Blog</a>.</p>
</div></main>'''
            hidden = '''<main id="main-content"><div class="ghx-wrap readings-page">
<h1>Live sessions</h1><p class="ghx-lead">No Live sessions are currently scheduled.</p>
<p><a href="/GhostHeart_Story.html">Enter My World</a> or <a href="/journal/">read the Blog</a>.</p>
</div></main>'''
            new = re.sub(r'<main\b.*?</main>', pending if PATH_VISIBLE else hidden, new, count=1, flags=re.S)
            title = 'Lives &amp; Readings' if PATH_VISIBLE else 'Live sessions'
            description = 'GhostHeart readings and Live announcements. The next Live date and viewing link are pending.' if PATH_VISIBLE else 'No Live sessions are currently scheduled.'
            new = new.replace('<title>Readings | GhostHeart</title>', f'<title>{title} | GhostHeart</title>')
            new = new.replace('Readings and Sunday Live updates from GhostHeart.', description)
        if not PATH_VISIBLE and path.relative_to(ROOT).as_posix() == 'live/my-promise.html':
            new = re.sub(r'<a class="reading-back" href="/live/">.*?</a>', '<a class="reading-back" href="/GhostHeart_Story.html">Enter My World</a>', new)
            new = new.replace('<a href="/live/">Return to Readings &amp; Live</a>', '<a href="/GhostHeart_Story.html">Return to My World</a>')
        new = re.sub(r'<article\b[^>]*\bid="home-lives"[^>]*>.*?</article>', '', new, flags=re.S)
        new = new.replace('aria-label="Explore Vault and Lives"', 'aria-label="Explore GhostHeart\u2019s Vault"')
        new = re.sub(r'<section\b[^>]*class="journal-highlight journal-live"[^>]*>.*?</section>', '', new, flags=re.S)
        new = re.sub(r'<p\b[^>]*>\s*<strong>Next Sunday Live:</strong>.*?</p>', '', new, flags=re.S)
        new = new.replace('The next planned Sunday Live is October 11, 2026 at 10:00 a.m. Central. The viewing platform and link are pending.', '')
        new = new.replace('<p class="ghx-kicker">Readings &amp; Live</p>', '<p class="ghx-kicker">Reading</p>')
        new = new.replace(' Sunday readings will connect selected pages to the work unfolding around them; reading details will be announced when they are confirmed.', '')
        # Only the Live entry route: keep the independently approved My Promise reading.
        if not PATH_VISIBLE:
            new = re.sub(r'<a\b[^>]*href="(?:/|\../)*live/(?:index\.html)?"[^>]*>.*?</a>', '', new, flags=re.S)
        if new != old:
            path.write_text(new, encoding='utf-8', newline='\n')
    sitemap = ROOT / 'sitemap.xml'
    value = sitemap.read_text(encoding='utf-8')
    if not PATH_VISIBLE:
        value = re.sub(r'\s*<url>\s*<loc>https://www\.myghostheart\.com/live/</loc>.*?</url>', '', value, flags=re.S)
    sitemap.write_text(value, encoding='utf-8', newline='\n')
    feed = ROOT / 'journal/feed.xml'
    feed_text = feed.read_text(encoding='utf-8')
    feed_text = feed_text.replace(' Sunday readings will connect selected pages to the work unfolding around them; reading details will be announced when they are confirmed.', '')
    feed.write_text(feed_text, encoding='utf-8', newline='\n')
    print('Applied Live announcement-pending status; pathway visible:', PATH_VISIBLE, '; historical event source preserved.')

if __name__ == '__main__':
    apply()
