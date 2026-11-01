#!/usr/bin/env python3
"""One home for each thing (2026-11-01, Dom: "theres a alot of duplicate
information on multiple pages").

Final build step. Pages that only repeated other pages now send visitors to
the one page that holds that information:

  /workshop/ (and /apps/)    -> Projects (Deal Vector moved onto Projects)
  /start/                    -> Home
  /GhostHeart_Versions.html  -> Enter My World

Links to the retired pages are pointed straight at their new home, and the
retired addresses leave the sitemap.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://www.myghostheart.com'
RETIRED = {
    'workshop/index.html': ('/GhostHeart_Projects.html', 'Projects', 'Apps and tools now live on the Projects page.'),
    'apps/index.html': ('/GhostHeart_Projects.html', 'Projects', 'Apps and tools now live on the Projects page.'),
    'start/index.html': ('/', 'GhostHeart', 'Start on the GhostHeart home page.'),
    'GhostHeart_Versions.html': ('/GhostHeart_Story.html', 'Enter My World', 'The story continues in Enter My World.'),
}


def stub(target, name, note):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta content="width=device-width,initial-scale=1" name="viewport"/><title>{name} | GhostHeart</title><meta content="{note} This address moved; follow the link to the current page." name="description"/><meta content="noindex,follow" name="robots"/><link href="{BASE}{target}" rel="canonical"/><meta content="0; url={target}" http-equiv="refresh"/><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#080808;color:#eae3d6;font-family:Arial,sans-serif;text-align:center;padding:24px}}h1{{font-family:Anton,Impact,sans-serif;text-transform:uppercase;font-size:clamp(32px,7vw,64px);margin:0 0 16px}}a{{color:#ff2b4a;font-weight:700;font-size:20px}}</style></head>
<body><main><h1>{name}</h1><p>{note}</p><p><a href="{target}">Go to {name}</a></p></main></body></html>
'''


for relative, (target, name, note) in RETIRED.items():
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stub(target, name, note), encoding='utf-8', newline='\n')

LINKS = [
    (re.compile(r'href="(?:https://www\.myghostheart\.com)?(?:/|\.\./)*(?:workshop|apps)/(?:index\.html)?(#[^"]*)?"'), 'href="/GhostHeart_Projects.html"'),
    (re.compile(r'href="(?:https://www\.myghostheart\.com)?(?:/|\.\./)*start/(?:index\.html)?(#[^"]*)?"'), 'href="/"'),
    (re.compile(r'href="(?:https://www\.myghostheart\.com)?(?:/|\.\./)*GhostHeart_Versions\.html(#[^"]*)?"'), 'href="/GhostHeart_Story.html"'),
]
changed = 0
for path in ROOT.rglob('*.html'):
    relative = path.relative_to(ROOT).as_posix()
    if any(part in {'.github', 'node_modules', '.git'} for part in path.relative_to(ROOT).parts) or relative in RETIRED:
        continue
    text = path.read_text(encoding='utf-8')
    fixed = text
    for pattern, replacement in LINKS:
        # Leave canonical/refresh tags of other redirect stubs alone.
        fixed = pattern.sub(lambda m: replacement if 'rel="canonical"' not in fixed[m.end():m.end() + 20] else m.group(0), fixed)
    if fixed != text:
        path.write_text(fixed, encoding='utf-8', newline='\n')
        changed += 1

sitemap = ROOT / 'sitemap.xml'
xml = sitemap.read_text(encoding='utf-8')
for loc in ('/start/', '/workshop/', '/GhostHeart_Versions.html'):
    xml = re.sub(r'\s*<url>\s*<loc>' + re.escape(BASE + loc) + r'</loc>.*?</url>', '', xml, flags=re.S)
sitemap.write_text(xml, encoding='utf-8')
print(f'Single home: {len(RETIRED)} retired addresses, links updated on {changed} pages.')
