#!/usr/bin/env python3
"""Apply the owner-approved compact navigation to every public HTML shell."""
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[2]
HEADER = '''<header class="nav ghx-header" data-nav-owner="shared">
<div class="ghx-wrap ghx-bar"><a class="ghx-brand" aria-label="GhostHeart home" href="/index.html">GHOST<span>HEART</span></a>
<nav aria-label="Main navigation" class="ghx-primary"><a href="/index.html">Home</a><a href="/awakening/index.html">The Awakening</a><a href="/GhostHeart_Story.html">Enter My World</a><a href="/albums/index.html">Music</a></nav>
<button aria-controls="gateway-menu" aria-expanded="false" class="menu-toggle ghx-menu-toggle" type="button">Explore <span aria-hidden="true">+</span></button>
<a class="ghx-help-link" href="/GhostHeart_Resources.html">Help &amp; Resources</a></div>
<nav aria-label="Explore GhostHeart" class="ghx-menu" hidden id="gateway-menu"><div class="ghx-wrap ghx-menu-grid">
<div><h2>Go deeper</h2><a href="/GhostHeart_Story.html#behind-the-scars">Behind the Scars</a><a href="/woman-behind-the-scenes/">The Woman Behind the Scenes</a><a href="/vault/">GhostHeart's Vault</a></div>
<div><h2>Explore</h2><a href="/journal/">Blog</a><a href="/live/">Lives &amp; Readings</a><a href="/GhostHeart_Projects.html">Projects</a><a href="/follow/">Stay Connected</a></div>
</div></nav></header>'''
PATTERN = re.compile(r'<header\b[^>]*class=["\'][^"\']*\bghx-header\b[^"\']*["\'][^>]*>.*?</header>', re.S | re.I)

def build_header(path):
    rel = path.relative_to(ROOT).as_posix()
    active = ('/albums/index.html' if rel.startswith('albums/') else
              '/live/' if rel.startswith('live/') else
              {'awakening/index.html': '/awakening/index.html',
               'GhostHeart_Story.html': '/GhostHeart_Story.html',
               'GhostHeart_Projects.html': '/GhostHeart_Projects.html',
               'journal/index.html': '/journal/',
               'GhostHeart_Resources.html': '/GhostHeart_Resources.html',
               'GhostHeart_Quotes.html': '/vault/',
               'GhostHeart_Videos.html': '/vault/',
               'GhostHeart_Songs.html': '/albums/index.html',
               'follow/index.html': '/follow/',
               'start/index.html': '/index.html',
               'woman-behind-the-scenes/index.html': '/woman-behind-the-scenes/',
               'vault/index.html': '/vault/'}.get(rel))
    header = HEADER
    if rel == 'index.html':
        active = '/index.html'
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
    old = path.read_text(encoding='utf-8')
    new, count = PATTERN.subn(lambda _: build_header(path), old, count=1)
    if count and new != old:
        new = new.replace('>Join the Heartbeat<', '>Stay Connected<').replace('>Join the Signal<', '>Stay Connected<')
        path.write_text(new, encoding='utf-8', newline='\n')
        changed += 1
print('Updated navigation on', changed, 'HTML pages')
