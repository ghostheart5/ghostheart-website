#!/usr/bin/env python3
"""Google Analytics on myghostheart.com (Dom's yes, Nov 8, 2026, 13:09 UTC: "3. yes").

Runs last in build_site.py. The measurement ID (G-...) lives in .github/content/google-analytics.json.
While it is empty this step changes nothing, so the site stays exactly as it is until the property exists.

When the ID is set, every page gets:
- /assets/shared/ghostheart-ga.js (no inline script), which adds Google's gtag script only on the public domain (www.myghostheart.com and
  myghostheart.com), never on local previews or test runs, and only once per page
- Google's script and data addresses added to the page's Content-Security-Policy
and the privacy page gets a "Google Analytics" paragraph next to the Metricool one.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SKIP = ('.github', '.git', 'node_modules', 'apps')
ID_OK = re.compile(r'^G-[A-Z0-9]{4,16}$')

SCRIPT_SRC = 'https://www.googletagmanager.com'
CONNECT_SRC = 'https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com'

LOADER = '<script defer id="ghostheart-ga-loader" src="/assets/shared/ghostheart-ga.js" data-ga-id="%s"></script>'

PRIVACY = ('<h2>Google Analytics</h2>\n<p>GhostHeart also uses Google Analytics to count visits, pages viewed and roughly where '
           'visitors come from. Google Analytics sets cookies in your browser to tell a new visit from a returning one. '
           'GhostHeart sees only totals, never who you are. Learn more about '
           '<a href="https://policies.google.com/technologies/partner-sites" rel="noopener" target="_blank">how Google uses '
           'information from sites that use its services</a>, or turn it off with the '
           '<a href="https://tools.google.com/dlpage/gaoptout" rel="noopener" target="_blank">Google Analytics opt-out add-on</a>.</p>\n')
PRIVACY_AFTER = re.compile(r'(<h2>Website visit analytics</h2>\s*<p>.*?</p>\s*)', re.S)
CSP_META = re.compile(r'(<meta\b[^>]*\bhttp-equiv="Content-Security-Policy"[^>]*\bcontent=")([^"]*)(")', re.I)


def measurement_id() -> str:
    mid = json.loads((ROOT / '.github/content/google-analytics.json').read_text(encoding='utf-8')).get('measurement_id', '').strip()
    if mid and not ID_OK.match(mid):
        raise SystemExit(f'google-analytics.json: "{mid}" is not a Google Analytics measurement ID (G-...)')
    return mid


def csp(policy: str) -> str:
    parts = [p.strip() for p in policy.split(';') if p.strip()]
    out = []
    for p in parts:
        name = p.split()[0]
        if name == 'script-src' and SCRIPT_SRC not in p:
            p += ' ' + SCRIPT_SRC
        if name == 'connect-src' and 'google-analytics.com' not in p:
            p += ' ' + CONNECT_SRC
        out.append(p)
    return '; '.join(out)


def apply(html: str, mid: str, privacy: bool = False) -> str:
    if 'id="ghostheart-ga-loader"' not in html:
        if '</head>' not in html:
            return html
        html = html.replace('</head>', LOADER % mid + '</head>', 1)
    html = CSP_META.sub(lambda m: m.group(1) + csp(m.group(2)) + m.group(3), html)
    if privacy and '<h2>Google Analytics</h2>' not in html:
        html = PRIVACY_AFTER.sub(lambda m: m.group(1) + PRIVACY, html, count=1)
    return html


def main() -> None:
    mid = measurement_id()
    if not mid:
        print('Google Analytics: no measurement ID yet, nothing added.')
        return
    n = 0
    for p in ROOT.rglob('*.html'):
        rel = p.relative_to(ROOT).as_posix()
        if rel.split('/')[0] in SKIP or '/node_modules/' in rel:
            continue
        old = p.read_text(encoding='utf-8')
        new = apply(old, mid, privacy=rel == 'GhostHeart_Privacy.html')
        if new != old:
            p.write_text(new, encoding='utf-8')
            n += 1
    print(f'Google Analytics {mid} added to {n} pages.')


if __name__ == '__main__':
    main()
