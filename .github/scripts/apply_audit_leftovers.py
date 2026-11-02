#!/usr/bin/env python3
"""Audit leftovers (2026-11-02, owner: "Yes, build the preview" on the Nov 2 recheck).

Final build step. Plain text swaps on the finished pages, safe to run twice.

- One footer: the older short footers (ghx-footer / gateway-footer) get the
  same main links as the Home footer (Music, Films, Lives, Blog), say
  "Find Support", and point "Stay Connected" at /follow/ (the old
  #join-the-signal spot is gone).
- Blog: the Wake the Heart Week post is labelled "Coming Nov 9" so it does
  not read as happening now.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN = ('<a href="/music/">Music</a><a href="/GhostHeart_Videos.html">Films</a>'
        '<a href="/live/">Lives</a><a href="/journal/">Blog</a>')
OPENERS = ('<div class="ghx-footer-bottom"><span>© 2026 GhostHeart</span>',
           '<div class="gateway-footnote"><span>© 2026 GhostHeart</span>')
SUPPORT = ['<a href="/GhostHeart_Resources.html">Support &amp; resources</a>',
           '<a href="/GhostHeart_Resources.html">Support</a>',
           '<a href="/GhostHeart_Resources.html">Find support</a>']
SWAPS = [
    ('<a href="/index.html#join-the-signal">Stay Connected</a>', '<a href="/follow/">Stay Connected</a>'),
    ('<a href="/follow/index.html">Follow by email</a>', '<a href="/follow/">Stay Connected</a>'),
]
BLOG_OLD = '<small>Announcement · October 30, 2026</small><h3>Wake the Heart Week</h3>'
BLOG_NEW = '<small>Coming Nov 9 · Announcement · October 30, 2026</small><h3>Wake the Heart Week</h3>'

footers = 0
for path in sorted(ROOT.rglob('*.html')):
    if any(p in path.parts for p in ('.github', 'node_modules', '.git', 'apps')):
        continue
    text = path.read_text(encoding='utf-8')
    out = text
    for opener in OPENERS:
        if opener in out and MAIN not in out:
            out = out.replace(opener, opener + MAIN)
    if MAIN in out:
        for old in SUPPORT:
            out = out.replace(old, '<a href="/GhostHeart_Resources.html">Find Support</a>')
        for old, new in SWAPS:
            out = out.replace(old, new)
    if path.relative_to(ROOT).as_posix() == 'journal/index.html':
        out = out.replace(BLOG_OLD, BLOG_NEW)
    if out != text:
        path.write_text(out, encoding='utf-8', newline='\n')
        footers += 1

print(f'Audit leftovers: {footers} pages updated.')

# Site map: list the Before the Heart Wakes page and stamp the Nov 2 update
# (a fixed date, so a rebuild on another day gives the same file).
sitemap = ROOT / 'sitemap.xml'
text = sitemap.read_text(encoding='utf-8')
out = text
if '<loc>https://www.myghostheart.com/awakening/</loc>' not in out:
    out = out.replace('</urlset>', '  <url>\n    <loc>https://www.myghostheart.com/awakening/</loc>\n    <lastmod>2026-11-02</lastmod>\n  </url>\n</urlset>')
import re
out = re.sub(r'<lastmod>2026-(09|10)-\d\d</lastmod>', '<lastmod>2026-11-02</lastmod>', out)
if out != text:
    sitemap.write_text(out, encoding='utf-8', newline='\n')
    print('Audit leftovers: site map updated.')
