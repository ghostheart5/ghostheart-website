#!/usr/bin/env python3
"""One sign-up per page (2026-11-01, Dom: "WHY DO YOU HAVE GET EMAIL UPDATES
AND SIGN UP ON THE SAME PAGE").

Final build step. A page that has the email sign-up box keeps only the box:
  - Home: the bottom "Join the Heart Rebellion" card drops its "Join by email"
    button and email note (the box sits under the hero buttons).
  - Blog front page: the top "Get email updates" button and the
    "Get new entries" button go.
  - Blog front page and posts: the "You can also sign up on the Stay Connected
    page" line under the box goes.
Menu and footer links to Stay Connected stay.
"""
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]


def fix(path, selectors):
    text = path.read_text(encoding='utf-8')
    doc = BeautifulSoup(text, 'html.parser')
    for selector in selectors:
        for node in doc.select(selector):
            parent = node.parent
            node.decompose()
            if parent and parent.name == 'div' and 'ctas' in (parent.get('class') or []) and not parent.find(True):
                parent.decompose()
    out = str(doc)
    if out != text:
        path.write_text(out, encoding='utf-8', newline='\n')
        return 1
    return 0


changed = fix(ROOT / 'index.html', ['.rebellion-actions a.rebellion-primary', '.rebellion-invite .rebellion-note'])
for path in sorted((ROOT / 'journal').glob('*.html')):
    doc_has_box = 'signal-signup-form' in path.read_text(encoding='utf-8')
    if doc_has_box:
        changed += fix(path, ['a.email-entry', '.journal-signup-fallback', '.qotd a[href="/follow/"]'])
print(f'One sign-up per page: cleaned {changed} pages.')
