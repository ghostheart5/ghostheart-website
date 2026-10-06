#!/usr/bin/env python3
"""Apply the owner-approved four-tab navigation to every public HTML shell."""
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[2]
HEADER = '''<header class="nav ghx-header" data-nav-owner="shared">
<div class="ghx-wrap ghx-bar"><a class="ghx-brand" aria-label="GhostHeart home" href="/index.html">GHOST<span>HEART</span></a>
<nav aria-label="Main navigation" class="ghx-primary"><a href="/GhostHeart_Story.html">Awakening</a><a href="/albums/index.html">Music</a><a href="/live/index.html">Readings</a><a href="/GhostHeart_Projects.html">Projects</a></nav>
<button aria-controls="gateway-menu" aria-expanded="false" class="menu-toggle ghx-menu-toggle" type="button">Explore <span aria-hidden="true">+</span></button></div>
<nav aria-label="Explore GhostHeart" class="ghx-menu" hidden id="gateway-menu"><div class="ghx-wrap ghx-menu-grid">
<div><h2>Read &amp; share</h2><a href="/journal/">Blog</a><a href="/GhostHeart_Quotes.html">Quotes</a></div>
<div><h2>Find support</h2><a href="/GhostHeart_Resources.html">Help &amp; Resources</a></div>
<div><h2>Go deeper</h2><a href="/GhostHeart_Angel.html">GhostHeart and His Angel</a></div>
<div><h2>Stay connected</h2><a href="/index.html#join-the-signal">Stay Connected</a></div>
</div></nav></header>'''
PATTERN = re.compile(r'<header\b[^>]*class=["\'][^"\']*\bghx-header\b[^"\']*["\'][^>]*>.*?</header>', re.S | re.I)

def build_header(path):
    rel = path.relative_to(ROOT).as_posix()
    active = ('/albums/index.html' if rel.startswith('albums/') else
              '/live/index.html' if rel.startswith('live/') else
              {'GhostHeart_Story.html': '/GhostHeart_Story.html',
               'GhostHeart_Projects.html': '/GhostHeart_Projects.html',
               'journal/index.html': '/journal/',
               'GhostHeart_Resources.html': '/GhostHeart_Resources.html',
               'GhostHeart_Quotes.html': '/GhostHeart_Quotes.html',
               'GhostHeart_Angel.html': '/GhostHeart_Angel.html'}.get(rel))
    header = HEADER
    if rel == 'index.html':
        header = header.replace('class="ghx-brand"', 'class="ghx-brand" aria-current="page"', 1)
    if rel.startswith('journal/'):
        active = '/journal/'
    if active:
        header = header.replace(f'href="{active}"', f'aria-current="page" href="{active}"', 1)
    depth = len(path.relative_to(ROOT).parts) - 1
    # GitHub Pages serves 404.html at the missing URL, which can be nested.
    # Its navigation must resolve from the site root rather than that URL.
    prefix = '/' if rel == '404.html' else '../' * depth
    return re.sub(r'(href|src)="/([^"]*)"', lambda m: f'{m.group(1)}="{prefix}{m.group(2)}"', header)

changed = 0
for path in ROOT.rglob('*.html'):
    if '.github' in path.parts:
        continue
    relative = path.relative_to(ROOT).as_posix()
    if relative in {'GhostHeart_Story.html', 'GhostHeart_Projects.html', 'albums/index.html', 'live/index.html'} or relative.startswith(('journal/', 'live/')):
        # These shells are built from the canonical Home header by their generators.
        continue
    old = path.read_text(encoding='utf-8')
    new, count = PATTERN.subn(lambda _: build_header(path), old, count=1)
    if count and new != old:
        new = new.replace('>Join the Heartbeat<', '>Stay Connected<').replace('>Join the Signal<', '>Stay Connected<')
        path.write_text(new, encoding='utf-8', newline='\n')
        changed += 1
print('Updated navigation on', changed, 'HTML pages')
