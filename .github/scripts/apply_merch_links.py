#!/usr/bin/env python3
"""Add the GhostHeart merch shop (Fourthwall) to the Explore menu and the footer on every page."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SHOP = 'https://ghostheart-studios-shop.fourthwall.com'
LINK = f'<a href="{SHOP}" rel="noopener" target="_blank">Merch</a>'

changed = 0
for path in ROOT.rglob('*.html'):
    if '.github' in path.parts or '.git' in path.parts:
        continue
    old = path.read_text(encoding='utf-8')
    new = old
    if True:
        # Explore menu: put Merch right after Projects.
        new = re.sub(r'(<nav aria-label="Explore GhostHeart".*?<a [^>]*GhostHeart_Projects\.html">Projects</a>)(?!<a href="https://ghostheart-studios-shop)',
                     lambda m: m.group(1) + LINK, new, count=1, flags=re.S)
        # Footer "Stay" list: put Merch right after The Vault.
        new = re.sub(r'(<nav aria-label="Stay">.*?<a [^>]*vault/">The Vault</a>)(?!<a href="https://ghostheart-studios-shop)',
                     lambda m: m.group(1) + LINK, new, count=1, flags=re.S)
    if new != old:
        path.write_text(new, encoding='utf-8', newline='\n')
        changed += 1
print('Added merch links on', changed, 'HTML pages')
