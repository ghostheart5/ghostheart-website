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
    # Dom, Nov 8 2026: older songs are off the site, so the reading's page forwards to the Blog
    # (apply_week1_songs_only.py). The approved text above stays unchanged in the source.
    article = BeautifulSoup(target.read_text(), 'html.parser')
    assert article.select_one('meta[http-equiv="refresh"]')['content'] == '0; url=/journal/'
    index = BeautifulSoup((ROOT/'journal/index.html').read_text(), 'html.parser')
    assert not index.select_one('#e-cruel') and 'Cruel' not in index.get_text(' ', strip=True)
    assert SLUG not in (ROOT/'journal/feed.xml').read_text()
    assert not any(node.text == 'https://www.myghostheart.com'+ROUTE
                   for node in ET.parse(ROOT/'sitemap.xml').iter() if node.tag.endswith('}loc'))
    print(f'PASS: exact approved source ({len(paragraphs)} paragraphs) kept; its page forwards to the Blog (older songs off the site)')
