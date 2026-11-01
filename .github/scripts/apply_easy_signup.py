#!/usr/bin/env python3
"""Easy signup (2026-10-31, Dom: "how don't I have one subscriber?").

Final build step. Every Mailchimp signup form on the site now finishes in the
same tab instead of opening a new one (phones often block or lose new tabs),
and the note under each form says so.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
FORM = re.compile(r'<form\b[^>]*list-manage\.com/subscribe/post[^>]*>')
OLD_NOTE = 'You’ll finish signup in a new Mailchimp tab.'
NEW_NOTE = 'Mailchimp opens to finish signup.'
changed = 0
for path in ROOT.rglob('*.html'):
    if any(part in {'.github', 'node_modules', '.git'} for part in path.relative_to(ROOT).parts):
        continue
    text = path.read_text(encoding='utf-8')
    fixed = FORM.sub(lambda m: re.sub(r'\s(?:target="_blank"|rel="noopener noreferrer")', '', m.group(0)), text)
    fixed = fixed.replace(OLD_NOTE, NEW_NOTE)
    if fixed != text:
        path.write_text(fixed, encoding='utf-8', newline='\n')
        changed += 1
print(f'Easy signup: same-tab Mailchimp forms on {changed} pages.')
