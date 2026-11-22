#!/usr/bin/env python3
"""Size caps on every page (Dom, Nov 21 2026).

Dom: "THE WHOLE SITE IS HUGE AGAIN, EVERYTIME THEY CHANGE SOMETHING THE WHOLE WEBSITE GOES BACK TO
HUGE LAYOUT, A LOT OF SCROLLING". The October size fixes lived in a stylesheet the November
redesigns stopped loading, so the big sizes came back. This step links one small stylesheet,
/assets/shared/size-caps.css, as the LAST thing in the head of every page, so its limits win over
whatever styles a page brings. .github/scripts/test_size_caps.cjs fails the website checks when a
page goes over the limits.

Runs near the end of build_site.py, after every step that rewrites a head. Idempotent.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LINK = '<link rel="stylesheet" href="/assets/shared/size-caps.css" id="gh-size-caps">'
SKIP_DIRS = {'.git', '.github', 'node_modules', 'ghostheart-website'}
# Any earlier copy of the link, in whatever attribute order a later build step re-wrote it.
OLD = re.compile(r'\s*<link[^>]*/assets/shared/size-caps\.css[^>]*>')

count = 0
for page in sorted(ROOT.rglob('*.html')):
    if SKIP_DIRS & set(page.relative_to(ROOT).parts):
        continue
    html = page.read_text(encoding='utf-8')
    if '</head>' not in html:
        continue
    new = OLD.sub('', html)
    new = new.replace('</head>', LINK + '</head>', 1)
    if new != html:
        page.write_text(new, encoding='utf-8')
    count += 1
print(f'Size caps stylesheet linked last on {count} pages.')
