#!/usr/bin/env python3
"""Before the Heart Wakes (2026-11-01, owner: "EVERYTHING IN THE WEBSITE THAT SAYS
THE AWAKENING NEEDS TO SAY BEFORE THE HEART WAKES").

Final build step. Every published page and the blog feed say "Before the Heart Wakes"
where they said "The Awakening": menu, campaign, page titles, share text and readings.
The sources (content JSON, templates, LOUD pages) still use the old wording; this
step renames the finished output, so it holds however a page was generated.

Unchanged on purpose (owner, same day): the album title "GhostHeart's Awakening",
lowercase prose ("where the awakening began"; the album blurb "One awakening."), and addresses
such as /awakening/, so no link breaks. Idempotent.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = 'Before the Heart Wakes'
RENAMES = [
    ('The Awakening campaign', NAME),  # "The Before the Heart Wakes campaign" reads badly
    ('THE AWAKENING', NAME.upper()),
    ('The Awakening', NAME),
]

files = [p for p in ROOT.rglob('*.html')
         if not any(part in {'.github', '.claude', 'node_modules', '.git'} for part in p.relative_to(ROOT).parts)]
files.append(ROOT / 'journal/feed.xml')

changed = 0
for path in files:
    text = path.read_text(encoding='utf-8')
    fixed = text
    for old, new in RENAMES:
        fixed = fixed.replace(old, new)
    if fixed != text:
        path.write_text(fixed, encoding='utf-8', newline='\n')
        changed += 1
    assert 'The Awakening' not in fixed and 'THE AWAKENING' not in fixed, path
print(f'Campaign name: "{NAME}" on {changed} files.')
