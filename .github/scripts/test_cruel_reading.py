#!/usr/bin/env python3
"""Verify the exact approved reading and its separate journal route."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'cruel-something-needs-to-change'
ROUTE = '/journal/' + SLUG + '.html'
SOURCE = ROOT / '.github/reviewed-inputs/content/cruel-reading.txt'
EXPECTED_SHA = '6b6c074b85b70685907000a42a80a606611b3a7e179a2d285a6ef9644f135b4d'
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA, 'Approved reading bytes changed'
title, *paragraphs = raw.decode('utf-8').strip().split('\n\n')
posts = json.loads((ROOT / '.github/content/journal.json').read_text())
post = next(p for p in posts if p['slug'] == SLUG)
assert post['title'] == title and post['paragraphs'] == paragraphs
assert post['summary'] == paragraphs[0] and post['comments_enabled'] is True
assert post['published'] == '2026-10-10T19:00:00-05:00'
clock = os.environ.get('GHOSTHEART_JOURNAL_BUILD_NOW')
now = datetime.fromisoformat(clock.replace('Z', '+00:00')) if clock else datetime.now(timezone.utc)
due = datetime.fromisoformat(post['published'])
target = ROOT / ROUTE.lstrip('/')
if now < due:
    assert not target.exists(), 'Normal generator must exclude a not-yet-due article'
    print('PASS: exact approved source; ordinary build holds the future article')
else:
    article = BeautifulSoup(target.read_text(), 'html.parser')
    assert article.select_one('article.journal-article h1').get_text() == title
    rendered = [p.get_text() for p in article.select('.journal-prose > p')]
    assert rendered == paragraphs, 'Rendered body differs from exact owner text'
    assert len(article.select('[data-comment-thread]')) == 1
    assert len(article.select('form.signal-signup-form')) == 1
    assert article.select('script[src*="comments"]')
    music_actions = article.select('.journal-continue a[href="/albums/#track-cruel"]')
    assert len(music_actions) == 1, 'Duplicate Cruel listening CTA'
    assert article.select_one('link[rel="canonical"]')['href'] == 'https://www.myghostheart.com'+ROUTE
    for tag in article.select('main a[href], main img[src]'):
        url = tag.get('href') or tag.get('src')
        parts = urlsplit(url)
        if not url.startswith('/') or url.startswith('//'):
            continue
        path = unquote(parts.path).lstrip('/')
        if parts.path.endswith('/'):
            path += 'index.html'
        dest = ROOT / path
        assert dest.is_file(), url
        if parts.fragment:
            assert BeautifulSoup(dest.read_text(), 'html.parser').find(id=unquote(parts.fragment)), url
    index = BeautifulSoup((ROOT/'journal/index.html').read_text(), 'html.parser')
    assert index.select_one(f'a[href="{ROUTE}"]')
    assert SLUG in (ROOT/'journal/feed.xml').read_text()
    assert any(node.text == 'https://www.myghostheart.com'+ROUTE
               for node in ET.parse(ROOT/'sitemap.xml').iter() if node.tag.endswith('}loc'))
    print(f'PASS: exact title and {len(paragraphs)} approved paragraphs; navigation, metadata, links; comment box on')
