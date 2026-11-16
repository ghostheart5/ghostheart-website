#!/usr/bin/env python3
"""Owner Nov 1: lead into Wake the Heart Week, November 9-15.

The homepage and announcement already explain the week. Other public content
pages get one compact link, without changing their stories, catalog or services.
Use absolute dates so a static countdown cannot go stale. Preserve page bytes
outside the inserted context and the homepage's campaign share description.
"""
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CSS = '<link href="/assets/shared/wake-the-heart.css" rel="stylesheet"/>'
BANNER = ('<div class="gh-wake-context"><a href="/journal/wake-the-heart-week.html">'
          '<span>Wake the Heart Week</span><span class="gh-wake-date">November 9\u201315, 2026</span>'
          '<span>Explore the week <span aria-hidden="true">\u2192</span></span></a></div>')
PREVIOUS = re.compile(r'<div class="gh-wake-context">.*?</div>\n?', re.S)
FIRST_STYLE = re.compile(r'<link\b[^>]*\brel="stylesheet"[^>]*>|</head>')
HOME_DESCRIPTION = 'Wake the Heart Week, November 9\u201315, 2026: eight songs, one journey through The Awakening. Listen now and explore the week.'

count = 0
for page in sorted(ROOT.rglob('*.html')):
    relative = page.relative_to(ROOT)
    if any(part in {'.github', '.git', 'node_modules', 'output'} for part in relative.parts):
        continue
    text = page.read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in text or not re.search(r'<main\b', text):
        continue
    fixed = PREVIOUS.sub('', text)
    if relative.as_posix() not in {'index.html', 'journal/wake-the-heart-week.html'}:
        fixed = re.sub(r'(<main\b[^>]*>)', lambda m: m[1] + '\n' + BANNER, fixed, count=1)
        if CSS not in fixed:
            fixed = FIRST_STYLE.sub(lambda m: CSS + '\n' + m[0], fixed, count=1)
        count += 1
    if relative.as_posix() == 'index.html':
        def campaign_meta(match):
            tag = match[0]
            if re.search(r'(?:property|name)="(?:og:title|twitter:title)"', tag):
                value = 'GhostHeart | The Man Behind The Heart.'
            elif re.search(r'(?:property|name)="(?:description|og:description|twitter:description)"', tag):
                value = HOME_DESCRIPTION
            else:
                return tag
            return re.sub(r'content="[^"]*"', lambda _: 'content="' + escape(value, quote=True) + '"', tag, count=1)
        fixed = re.sub(r'<meta\b[^>]*>', campaign_meta, fixed)
    if fixed != text:
        page.write_text(fixed, encoding='utf-8', newline='\n')
print(f'Wake the Heart Week: campaign homepage and one contextual link on {count} public pages.')
