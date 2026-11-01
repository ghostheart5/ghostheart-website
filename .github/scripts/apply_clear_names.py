#!/usr/bin/env python3
"""One name for each place (2026-11-01, site audit: "Overlapping destination
names and repeated social directories create unnecessary decisions").

Final build step. Menu, header and footer labels that pointed two different
names at one page, or one name at two different pages, now agree:

  "Help & Resources"  -> "Find Support"   (it sat next to "I'm Here to Help",
                                            which is the hire-me page)
  "GhostHeart's Vault" -> "The Vault"      (the footer already said this)
  "Live" (footer)     -> "Lives"           (the page is named "Lives")
  Explore menu heading "Enter My World" -> "The Story" (the top bar already has
                                            an "Enter My World" link to a
                                            different page)
  Explore menu "Merch" goes; Merch stays in the top bar on every screen size.

Link targets do not change. Idempotent.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = r'href="(?:/|(?:\.\./)*)GhostHeart_Resources\.html"'
RULES = [
    (re.compile(r'(<a\b[^>]*' + RESOURCES + r'[^>]*>)Help &amp; Resources</a>'), r'\1Find Support</a>'),
    (re.compile(r'(<a\b[^>]*' + RESOURCES + r'[^>]*>(?:<span class="n">\d+</span>)?<div><h3>)Help &amp;<br/?>Resources</h3>'), r'\1Find<br/>Support</h3>'),
    (re.compile(r'(<a\b[^>]*href="(?:/|(?:\.\./)*)vault/"[^>]*>)GhostHeart\'s Vault</a>'), r'\1The Vault</a>'),
    (re.compile(r'(<a\b[^>]*href="(?:/|(?:\.\./)*)live/"[^>]*>)Live</a>'), r'\1Lives</a>'),
]
MENU = re.compile(r'(<nav\b[^>]*id="gateway-menu"[^>]*>)(.*?)(</nav>)', re.S)
MENU_MERCH = re.compile(r'<a\b[^>]*href="https://ghostheart-studios-shop\.fourthwall\.com"[^>]*>Merch</a>')


def fix_menu(match):
    body = MENU_MERCH.sub('', match.group(2)).replace('<h2>Enter My World</h2>', '<h2>The Story</h2>', 1)
    return match.group(1) + body + match.group(3)


changed = 0
for path in ROOT.rglob('*.html'):
    if any(part in {'.github', 'node_modules', '.git'} for part in path.relative_to(ROOT).parts):
        continue
    text = path.read_text(encoding='utf-8')
    fixed = MENU.sub(fix_menu, text, count=1)
    for pattern, replacement in RULES:
        fixed = pattern.sub(replacement, fixed)
    if fixed != text:
        path.write_text(fixed, encoding='utf-8', newline='\n')
        changed += 1
print(f'Clear names: updated {changed} pages.')
