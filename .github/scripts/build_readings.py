#!/usr/bin/env python3
"""Build the Readings tab from the owner-confirmed next Sunday Live details."""
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LIVE = json.loads((ROOT / '.github/content/live.json').read_text(encoding='utf-8'))
assert LIVE['time_zone'] == 'America/Chicago'
assert LIVE['platform'] is None and LIVE['view_url'] is None
when = datetime.fromisoformat(LIVE['starts_at'])
assert when.strftime('%Y-%m-%d %H:%M %z') == '2026-10-11 10:00 -0500'

home = (ROOT / 'index.html').read_text(encoding='utf-8')
def shell_piece(value):
    value = re.sub(r' aria-current="[^"]*"', '', value)
    value = re.sub(r'href="#([^"]+)"', r'href="/index.html#\1"', value)
    return re.sub(r'(href|src)="(?!https?:|/|#)([^"]+)"', r'\1="/\2"', value)
header = shell_piece(re.search(r'<header\b.*?</header>', home, re.S).group())
# The shared navigation builder marks the Explore destination active after generation.
footer = shell_piece(re.search(r'<footer\b.*?</footer>', home, re.S).group())
html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Readings | GhostHeart</title><meta name="description" content="Readings and Sunday Live updates from GhostHeart."/>
<link rel="canonical" href="https://www.myghostheart.com/live/"/>
<link rel="stylesheet" href="/assets/shared/release-site.css"/><link rel="stylesheet" href="/assets/shared/ghostheart-world.css"/>
<link rel="stylesheet" href="/assets/journal/highlights.css"/><script defer src="/assets/shared/ghostheart-world.js"></script>
</head><body class="ghx-site"><a class="skip-link" href="#main-content">Skip to content</a>{header}
<main id="main-content"><div class="ghx-wrap readings-page"><p class="ghx-kicker">GhostHeart / Lives &amp; Readings</p>
<h1>Lives &amp; Readings.</h1><p class="ghx-lead">The planned gathering and approved readings, with details added only when confirmed.</p>
<section class="readings-event" aria-labelledby="next-live-title"><p class="ghx-kicker">Planned Sunday Live</p>
<h2 id="next-live-title">{escape(LIVE['title'])}</h2>
<p><time datetime="{LIVE['starts_at']}">Sunday, October 11, 2026 at 10:00 a.m. Central</time></p>
<p><strong>Planned passage:</strong> {escape(LIVE['planned_passage_title'])}. Its full text has not been provided for this site draft.</p>
<p>Viewing platform and link are pending. There is no Watch Live link yet.</p></section>
<section class="readings-event" id="live-replay" aria-labelledby="replay-title"><p class="ghx-kicker">Replay</p><h2 id="replay-title">No replay available yet.</h2><p>If a recording is approved and published later, its link can be added here.</p></section>
<section class="readings-event" aria-labelledby="promise-title"><p class="ghx-kicker">Separate approved reading</p><h2 id="promise-title">My Promise</h2><p>This public reading remains available separately from the planned first Live passage.</p><a href="/live/my-promise.html">Read My Promise</a></section>
<p><a href="/GhostHeart_Story.html">Enter My World</a> or <a href="/journal/">read the Blog</a>.</p>
</div></main>{footer}</body></html>\n'''
path = ROOT / 'live/index.html'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(html, encoding='utf-8', newline='\n')
source = (ROOT / '.github/content/my-promise.txt').read_text(encoding='utf-8').strip()
blocks = source.split('\n\n')
assert blocks[0] == 'My Promise' and len(blocks) == 16
paragraphs = ''.join(f'<p>{escape(block)}</p>' for block in blocks[1:])
article = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>My Promise | GhostHeart</title><meta name="description" content="My Promise, a separate approved GhostHeart reading."/>
<link rel="canonical" href="https://www.myghostheart.com/live/my-promise.html"/>
<link rel="stylesheet" href="/assets/shared/release-site.css"/><link rel="stylesheet" href="/assets/shared/ghostheart-world.css"/>
<link rel="stylesheet" href="/assets/journal/highlights.css"/><script defer src="/assets/shared/ghostheart-world.js"></script>
</head><body class="ghx-site"><a class="skip-link" href="#main-content">Skip to content</a>{header}
<main id="main-content"><article class="ghx-wrap reading-article"><a class="reading-back" href="/live/">← Readings &amp; Live</a>
<header><p class="ghx-kicker">Approved reading</p><h1>My Promise</h1><p>A promise to keep learning, listening, and choosing care.</p></header>
<div class="reading-text">{paragraphs}</div><p class="reading-return"><a href="/live/">Return to Readings &amp; Live</a></p>
</article></main>{footer}</body></html>\n'''
(ROOT / 'live/my-promise.html').write_text(article, encoding='utf-8', newline='\n')
print('Built Readings page and My Promise for', LIVE['starts_at'])
