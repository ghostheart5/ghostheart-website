#!/usr/bin/env python3
"""One Live schedule (2026-11-01, site audit: "Feed every location from one
current event record").

Final build step. The list of upcoming Lives on the Lives page
(.github/loud-pages/live/index.html.loud, the <li data-live-slot> rows) is the
only place a Live date is written. This copies those rows, hidden, into the
home page's "Coming next" card, so assets/shared/next-live.js rolls the home
page to the same next Live as the Lives page. The visible text (for visitors
without JavaScript) is the first Live that hasn't ended when the site is built.

To add a Live: add a row to the Lives page list. Nothing on the home page.
"""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
live = BeautifulSoup((ROOT / 'live/index.html').read_text(encoding='utf-8'), 'html.parser')
slots = [(escape(s['data-live-hide-after']), escape(s['data-live-when'])) for s in live.select('li[data-live-slot]')]
assert slots, 'Lives page must list at least one Live'

now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
shown = next((when for ends, when in slots if ends > now), slots[-1][1])
rows = ''.join(f'<span data-live-slot data-live-hide-after="{ends}" data-live-when="{when}" hidden></span>' for ends, when in slots)
line = (f'<p data-live-next>Next Live: <span data-live-slot-label data-live-until="{slots[-1][0]}" data-live-after="coming soon">'
        f'{shown}</span>, on <a href="https://www.tiktok.com/@ghosthearted1">TikTok</a>.{rows}</p>')

home = ROOT / 'index.html'
text = home.read_text(encoding='utf-8')
pattern = re.compile(r'<p(?: data-live-next)?>Next Live: <span\b.*?</p>', re.S)
assert len(pattern.findall(text)) == 1, 'home page must have exactly one Next Live line'
home.write_text(pattern.sub(lambda _: line, text, count=1), encoding='utf-8', newline='\n')
print(f'Live schedule: home page follows the Lives page ({len(slots)} Lives, showing {shown}).')
