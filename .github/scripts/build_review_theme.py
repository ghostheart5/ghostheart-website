#!/usr/bin/env python3
"""Load the shared review theme after page-specific styles on public shells."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STYLESHEET = '<link rel="stylesheet" href="/assets/shared/review-theme.css"/>'
changed = 0
for page in ROOT.rglob('*.html'):
    if '.github' in page.parts:
        continue
    html = page.read_text(encoding='utf-8')
    if 'ghx-site' not in html or 'review-theme.css' in html:
        continue
    if '</head>' not in html:
        continue
    page.write_text(html.replace('</head>', STYLESHEET + '</head>', 1), encoding='utf-8', newline='\n')
    changed += 1
print(f'Applied shared review theme to {changed} HTML shells')
