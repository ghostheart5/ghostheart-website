#!/usr/bin/env python3
"""Every official GhostHeart profile linked from the site (tools and offers check, Nov 21 2026).

The check found Instagram, Bluesky, Pinterest and X missing from the home and Work With
GhostHeart pages, and Bluesky, Pinterest and X missing from every other page's profile list.
This step adds the missing ones, in the same style as the links already there. Idempotent.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

# Order shown on the site. Handles from the owner's handle list.
PROFILES = [
    ('YouTube', 'https://www.youtube.com/@GhostHeart-M95RTK'),
    ('TikTok', 'https://www.tiktok.com/@ghosthearted1'),
    ('Spotify', 'https://open.spotify.com/artist/68OskMXP10WmzJPexLzRc7'),
    ('Instagram', 'https://www.instagram.com/ghostheart131517/'),
    ('Bluesky', 'https://bsky.app/profile/myghostheart.com'),
    ('Pinterest', 'https://www.pinterest.com/ghostheart131517/'),
    ('X', 'https://x.com/ghostheartgp'),
]
NEW = {'Bluesky', 'Pinterest', 'X'}
SKIP_DIRS = {'.git', '.github', 'node_modules'}

PROFILE_NAV = re.compile(r'(<nav aria-label="Official GhostHeart profiles">)(.*?)(</nav>)', re.S)
FIRST_LINK = re.compile(r'<a ([^>]*?)href="[^"]+"([^>]*)>([^<]*?)(\s*↗)?</a>')


def link_like(sample: re.Match, name: str, url: str) -> str:
    before, after, _, arrow = sample.groups()
    return f'<a {before}href="{url}"{after}>{name}{" ↗" if arrow else ""}</a>'


def fill_nav(match: re.Match) -> str:
    start, inner, end = match.groups()
    sample = FIRST_LINK.search(inner)
    if not sample:
        return match.group(0)
    added = ''.join(link_like(sample, name, url) for name, url in PROFILES
                    if name in NEW and url not in inner)
    return f'{start}{inner}{added}{end}'


# Wake v3 footer (home and Work With GhostHeart): one link per line after YouTube.
FOOTER_YT = ('    <a href="https://www.youtube.com/@GhostHeart-M95RTK" '
             'target="_blank" rel="noopener">YouTube ↗</a>\n')


def fill_wake_footer(text: str) -> str:
    start = text.find('<footer><div class="wrap">')
    if start < 0:
        return text
    end = text.find('</footer>', start)
    block = text[start:end]
    if FOOTER_YT not in block:
        return text
    lines = ''.join(f'    <a href="{url}" target="_blank" rel="noopener">{name} ↗</a>\n'
                    for name, url in PROFILES
                    if name not in ('YouTube', 'Spotify') and url not in block)
    block = block.replace(FOOTER_YT, FOOTER_YT + lines, 1)
    return text[:start] + block + text[end:]


# Shared loud footer (most pages): the "Listen" column ends with YouTube.
LISTEN_YT = ('<a href="https://www.youtube.com/@GhostHeart-M95RTK" rel="noopener" '
             'target="_blank">YouTube ↗</a></div>')


def fill_listen_column(text: str) -> str:
    start = text.find('<p class="foot-h">Listen</p>')
    if start < 0:
        return text
    end = text.find(LISTEN_YT, start)
    if end < 0:
        return text
    column = text[start:end]
    lines = ''.join(f'<a href="{url}" rel="noopener" target="_blank">{name} ↗</a>'
                    for name, url in PROFILES
                    if name not in ('YouTube', 'Spotify') and url not in column)
    cut = end + len(LISTEN_YT) - len('</div>')
    return text[:cut] + lines + text[cut:]


# Stay Connected page: the button row that lists the profiles.
FOLLOW_ROW = re.compile(r'(<div class="ghx-actions">)(<a href="https://www\.youtube\.com/@GhostHeart-M95RTK".*?)(</div>)', re.S)


def fill_follow(match: re.Match) -> str:
    start, inner, end = match.groups()
    added = ''.join(f'<a href="{url}" rel="noopener noreferrer" target="_blank">{name}</a>'
                    for name, url in PROFILES if url not in inner)
    return f'{start}{inner}{added}{end}'


changed = 0
for page in sorted(ROOT.rglob('*.html')):
    if SKIP_DIRS & set(page.relative_to(ROOT).parts):
        continue
    text = page.read_text(encoding='utf-8')
    new = PROFILE_NAV.sub(fill_nav, text)
    new = fill_wake_footer(new)
    new = fill_listen_column(new)
    if page.relative_to(ROOT).as_posix() == 'follow/index.html':
        new = FOLLOW_ROW.sub(fill_follow, new, count=1)
    if new != text:
        page.write_text(new, encoding='utf-8')
        changed += 1
print(f'Social links: all seven official profiles linked on {changed} pages.')
