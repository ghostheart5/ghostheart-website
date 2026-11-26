#!/usr/bin/env python3
"""Write sitemap.xml from the pages the build actually produced.

Runs in build_site.py just before apply_sitemap_dates.py, so the list can't go stale again
(Public Surface Scan, Nov 26, 2026: the hand-kept list had drifted).

A page is listed when it is a real page a visitor should land on:
- not a forwarding page (meta refresh) and not marked noindex,
- not in the old /ghostheart-website/ copy, the build sources, or a Google verification file,
- not one of the EXCLUDE pages below.

The order is stable (Home first, then by address) so a second build gives the same file.
"""
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://www.myghostheart.com'
SKIP_DIRS = {'.github', '.git', 'node_modules', 'assets', 'ghostheart-website'}
# Privacy pages for apps that are not released yet: kept online for the stores, not offered to search.
EXCLUDE = {
    '/apps/love-is-not-rebellion/privacy/',
    '/apps/the-unseen/privacy/',
    '/apps/unlabeled/privacy/',
    '/apps/words-that-hit/privacy/',
}


def address(page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')]
    return '/' + rel


def listed(page: Path) -> bool:
    rel = page.relative_to(ROOT)
    if rel.parts[0] in SKIP_DIRS or page.name.startswith('google') or page.name == '404.html':
        return False
    soup = BeautifulSoup(page.read_text(encoding='utf-8', errors='ignore'), 'html.parser')
    robots = soup.find('meta', attrs={'name': lambda v: v and v.lower() == 'robots'})
    if robots and 'noindex' in robots.get('content', '').lower():
        return False
    if soup.find('meta', attrs={'http-equiv': lambda v: v and v.lower() == 'refresh'}):
        return False
    return address(page) not in EXCLUDE


def main():
    pages = sorted({address(p) for p in ROOT.rglob('*.html') if listed(p)}, key=lambda a: (a != '/', a))
    body = ''.join(f'  <url>\n    <loc>{BASE}{a}</loc>\n  </url>\n' for a in pages)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(xml, encoding='utf-8', newline='\n')
    print(f'Sitemap: {len(pages)} pages listed from the built site.')


main()
