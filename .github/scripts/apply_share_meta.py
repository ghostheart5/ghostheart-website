#!/usr/bin/env python3
"""Give every public page a share preview (audit 2026-10-26: /live/ and Projects had none).

Final build step. A page that already names an og:image is left exactly as it is.
For the rest, the preview is built from the page's own <title>, meta description and
canonical link, plus a share image. Redirect stubs are skipped. Idempotent.
"""
from html import escape, unescape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://www.myghostheart.com'
DEFAULT_IMAGE = SITE + '/assets/story/ghostheart-scars-rooftop-rain.png'
IMAGES = {'assets/platforms/index.html': SITE + '/assets/platforms/header.jpg'}


def first(pattern, text):
    match = re.search(pattern, text, re.I | re.S)
    return unescape(match.group(1).strip()) if match else ''


def url_for(route):
    route = route.replace('\\', '/')
    if route.endswith('index.html'):
        route = route[: -len('index.html')]
    return SITE + '/' + route


added = 0
for page in sorted(ROOT.rglob('*.html')):
    route = str(page.relative_to(ROOT)).replace('\\', '/')
    if '.github' in page.parts or 'node_modules' in page.parts:
        continue
    html = page.read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in html or 'og:image' in html or '</head>' not in html:
        continue
    title = first(r'<title[^>]*>(.*?)</title>', html) or 'GhostHeart'
    description = (first(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html)
                   or first(r'<meta[^>]*content="([^"]*)"[^>]*name="description"', html))
    canonical = (first(r'<link[^>]*rel="canonical"[^>]*href="([^"]*)"', html)
                 or first(r'<link[^>]*href="([^"]*)"[^>]*rel="canonical"', html)
                 or url_for(route))
    tags = [
        ('property', 'og:type', 'website'),
        ('property', 'og:site_name', 'GhostHeart'),
        ('property', 'og:title', title),
        ('property', 'og:url', canonical),
        ('property', 'og:image', IMAGES.get(route, DEFAULT_IMAGE)),
        ('name', 'twitter:card', 'summary_large_image'),
    ]
    if description:
        tags.insert(3, ('property', 'og:description', description))
    meta = ''.join(f'<meta content="{escape(value, quote=True)}" {kind}="{key}"/>'
                   for kind, key, value in tags if f'{kind}="{key}"' not in html)
    page.write_text(html.replace('</head>', meta + '</head>', 1), encoding='utf-8')
    added += 1
print('Share previews added:', added)
