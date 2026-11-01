#!/usr/bin/env python3
"""Check back in (2026-11-01, owner yes; site audit: "Save a song or line on the
device. Return to the playback position or reading point. Show what has changed
since the last visit. Provide clear reset and removal controls").

Final build step. Adds the shared stylesheet and script (assets/shared/check-back-in.*)
to the pages that use it: Home (its panel lives in .github/loud-pages/index.html.loud),
Music, the Vault, and every blog post, Passage and story chapter. Adds a "Saved on
this device" section to the Privacy page. Idempotent. The stylesheet goes before the
page's first stylesheet, so each page's own theme still loads last. Approved readings
whose bytes are locked (test_cruel_reading.py) are left exactly as they are.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CSS = '<link href="/assets/shared/check-back-in.css" rel="stylesheet"/>'
JS = '<script defer src="/assets/shared/check-back-in.js"></script>'
LOCKED = {'journal/cruel-something-needs-to-change.html'}
FIRST_STYLESHEET = re.compile(r'<link\b[^>]*\brel="stylesheet"[^>]*>|</head>')
pages = [ROOT / 'index.html', ROOT / 'music/index.html', ROOT / 'vault/index.html']
for folder in ('journal', 'passages', 'story'):
    pages += sorted((ROOT / folder).glob('*.html'))

changed = 0
for page in pages:
    text = page.read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in text or page.relative_to(ROOT).as_posix() in LOCKED:
        continue
    fixed = FIRST_STYLESHEET.sub(lambda m: CSS + '\n' + m.group(0), text.replace(CSS + '\n', ''), count=1)
    if JS not in fixed:
        fixed = fixed.replace('</body>', JS + '\n</body>', 1)
    assert CSS in fixed and JS in fixed, page
    if fixed != text:
        page.write_text(fixed, encoding='utf-8', newline='\n')
        changed += 1

privacy = ROOT / 'GhostHeart_Privacy.html'
text = privacy.read_text(encoding='utf-8')
NOTE = ('<h2 id="saved-on-this-device">Saved on this device</h2>\n'
        '<p>If you save a song, film or line, or stop partway through a song or a reading, this website remembers it '
        'in your own browser (local storage) so you can check back in later. It also keeps a visit count and the time '
        'of your last visit, to welcome you back and show what is new. None of this is sent to GhostHeart or anyone '
        'else. Clear it any time by clearing this '
        'site’s data in your browser.</p>\n')
anchor = '<h2>What is collected</h2>'
if 'id="saved-on-this-device"' not in text:
    assert text.count(anchor) == 1, 'privacy page section anchor'
    privacy.write_text(text.replace(anchor, NOTE + anchor, 1), encoding='utf-8', newline='\n')
print(f'Check back in: added to {changed} pages; privacy note present.')
