#!/usr/bin/env python3
"""Keep <meta> tags in every page head self-closing, with no stray </meta>.

Runs after every other build step (build_site.py, before the sitemap dates).

Why: the pinned beautifulsoup4 4.13.5 (html.parser) mis-reads a page where a
<meta ...> written without "/>" comes before a <meta .../> written with it: it treats
the second one as an open element and closes it with </meta> before </head>. Many build
steps re-read the committed pages with BeautifulSoup, so once a page mixes both forms,
every build adds stray </meta> tags (26 pages, Nov 8, 2026). Writing every head <meta>
the same way ("/>") stops it; stray </meta> left by earlier builds are removed here
(</meta> is never valid HTML, because <meta> has no end tag). validate_site.py fails the
build if any page still has </meta>.

Only the <head> is touched, outside its script/style/noscript/template blocks. Safe to run twice.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SKIP = ('.github', '.git', 'node_modules', 'apps')
HEAD = re.compile(r'(<head\b[^>]*>)(.*?)(</head>)', re.I | re.S)
OPEN_META = re.compile(r'<meta\b((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)\s*/?\s*>', re.I)
END_META = re.compile(r'</meta\s*>', re.I)


RAW = re.compile(r'(<(script|style|noscript|template)\b.*?</\2\s*>)', re.I | re.S)


def fix_tags(part: str) -> str:
    part = END_META.sub('', part)
    return OPEN_META.sub(lambda m: f'<meta{m.group(1)}/>', part)


def fix_head(head: str) -> str:
    # Leave script/style/noscript/template blocks exactly as written.
    pieces = RAW.split(head)
    out, i = [], 0
    while i < len(pieces):
        out.append(fix_tags(pieces[i]))
        if i + 1 < len(pieces):
            out.append(pieces[i + 1])
        i += 3
    return ''.join(out)


def fix(html: str) -> str:
    return HEAD.sub(lambda m: m.group(1) + fix_head(m.group(2)) + m.group(3), html, count=1)


def main() -> int:
    changed = 0
    for page in sorted(ROOT.rglob('*.html')):
        if any(part in SKIP for part in page.relative_to(ROOT).parts):
            continue
        text = page.read_text(encoding='utf-8')
        new = fix(text)
        if new != text:
            page.write_text(new, encoding='utf-8')
            changed += 1
    print(f'Head <meta> tags self-closing, no stray </meta>: {changed} pages updated.')
    return 0


main()
