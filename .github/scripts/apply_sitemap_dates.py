#!/usr/bin/env python3
"""Give every sitemap address the date its page really last changed.

Last build step. Dates come from .github/content/sitemap-lastmod.json, so
shallow CI checkouts and the weekly Passages release build give the same
result. A build from a full clone refreshes that file from git history by
itself (Nov 26, 2026: the dates had been stuck at Nov 8). To force it:

    python3 .github/scripts/apply_sitemap_dates.py --refresh
"""
from pathlib import Path
import json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
SITEMAP = ROOT / 'sitemap.xml'
DATES = ROOT / '.github/content/sitemap-lastmod.json'
BASE = 'https://www.myghostheart.com'
URL = re.compile(r'(<url>\s*<loc>([^<]+)</loc>)(\s*<lastmod>[^<]*</lastmod>)?', re.S)


def page_file(loc: str) -> str:
    path = loc[len(BASE):].lstrip('/') if loc.startswith(BASE) else loc
    return path + 'index.html' if path == '' or path.endswith('/') else path


def full_clone() -> bool:
    out = subprocess.run(['git', 'rev-parse', '--is-shallow-repository'], cwd=ROOT,
                         capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() == 'false'


def refresh(locs):
    if not full_clone():
        sys.exit('Refusing to refresh sitemap dates from a shallow clone: run git fetch --unshallow first.')
    dates = {}
    for loc in locs:
        day = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', page_file(loc)], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        if day:
            dates[loc[len(BASE):] or '/'] = day
    DATES.write_text(json.dumps(dict(sorted(dates.items())), indent=2) + '\n', encoding='utf-8')
    return dates


def main():
    xml = SITEMAP.read_text(encoding='utf-8')
    locs = [m.group(2) for m in URL.finditer(xml)]
    if '--refresh' in sys.argv or full_clone():
        dates = refresh(locs)
    else:
        dates = json.loads(DATES.read_text(encoding='utf-8'))

    def fix(m):
        day = dates.get(m.group(2)[len(BASE):] or '/')
        if not day:
            return m.group(0)
        return f'{m.group(1)}\n    <lastmod>{day}</lastmod>'

    out = URL.sub(fix, xml)
    if out != xml:
        SITEMAP.write_text(out, encoding='utf-8', newline='\n')
    print(f'Sitemap dates: {sum(1 for l in locs if (l[len(BASE):] or "/") in dates)} of {len(locs)} addresses dated from page history.')


main()
