#!/usr/bin/env python3
"""Website audit fixes, Nov 6, 2026 (owner: "fix the remaining").

Final build step (after apply_wake_v3.py). Plain text changes on the finished pages, safe to run twice.
Apps (apps/) are left alone.

- WEB-04: every page gets a referrer policy and a Content-Security-Policy meta tag right after
  <meta charset>. The policy lists only the origins the pages use (inventory in the PR).
  It has no form-action (Mailchimp decides where its sign-up form redirects), and frame-ancestors
  and HSTS cannot be set from a meta tag on GitHub Pages.
- WEB-06: share previews (og:image / twitter:image) for /awakening/, /passages/ and
  /woman-behind-the-scenes/ point at 1200x630 JPGs instead of 2.5-4.4 MB PNGs
  (made by .github/scripts/optimize_images.py).
- WEB-07: internal links ending in index.html use the folder address (/music/ not /music/index.html).
- WEB-08: the menu column titles ("The Story", "Explore") on the older pages came before the page's
  h1 as h2 headings; they become <p class="menu-heading"> with the same look (CSS in the menu styles).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://www.myghostheart.com'
SKIP = ('.github', '.git', 'node_modules', 'apps')

CSP = '; '.join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://tracker.metricool.com https://www.youtube.com https://s.ytimg.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' data: https://fonts.gstatic.com",
    "img-src 'self' data: blob: https:",
    "media-src 'self' blob: https:",
    "connect-src 'self' https://pgqaqqliefpofsktjhjq.supabase.co https://tracker.metricool.com",
    "frame-src https://www.youtube-nocookie.com https://www.youtube.com",
    "object-src 'none'",
    "base-uri 'self'",
])
HEAD_META = ('<meta name="referrer" content="strict-origin-when-cross-origin">'
             f'<meta http-equiv="Content-Security-Policy" content="{CSP}">')
CHARSET = re.compile(r'<meta\s+charset=["\']?[\w-]+["\']?\s*/?>', re.I)

SHARE = {
    'awakening/index.html': ('ghostheart-awakening-banner.png', 'ghostheart-awakening-share-1200x630.jpg'),
    'passages/index.html': ('ghostheart-awakening-banner.png', 'ghostheart-awakening-share-1200x630.jpg'),
    'passages/im-not.html': ('ghostheart-awakening-banner.png', 'ghostheart-awakening-share-1200x630.jpg'),
    'passages/its-not-the-1950s.html': ('ghostheart-awakening-banner.png', 'ghostheart-awakening-share-1200x630.jpg'),
    'passages/papa-didnt-raise-no-fool.html': ('ghostheart-awakening-banner.png', 'ghostheart-awakening-share-1200x630.jpg'),
    'woman-behind-the-scenes/index.html': ('ghostheart-rebel-in-the-rain.png', 'ghostheart-rebel-share-1200x630.jpg'),
}
META = re.compile(r'<meta\b[^>]*>', re.I)
HREF = re.compile(r'(<a\b[^>]*?\bhref=)(["\'])([^"\']*)\2', re.I)
H2 = re.compile(r'<h2(\s[^>]*)?>(.*?)</h2>', re.I | re.S)


def head_meta(html: str) -> str:
    # Earlier steps may re-serialize these tags (attribute order, "/>"), so match them loosely.
    html = re.sub(r'<meta\b[^>]*\bname="referrer"[^>]*>', '', html, flags=re.I)
    html = re.sub(r'<meta\b[^>]*\bhttp-equiv="Content-Security-Policy"[^>]*>', '', html, flags=re.I)
    m = CHARSET.search(html)
    if m:
        return html[:m.end()] + HEAD_META + html[m.end():]
    return re.sub(r'(<head\b[^>]*>)', lambda h: h.group(1) + HEAD_META, html, count=1, flags=re.I)


def share_image(route: str, html: str) -> str:
    if route not in SHARE:
        return html
    old, new = SHARE[route]
    old_url, new_url = f'{SITE}/assets/story/{old}', f'{SITE}/assets/story/{new}'

    def fix(m):
        tag = m.group(0)
        if re.search(r'(property|name)="(og:image|twitter:image)"', tag):
            return tag.replace(old_url, new_url)
        if re.search(r'property="og:image:width"', tag):
            return re.sub(r'content="\d+"', 'content="1200"', tag)
        if re.search(r'property="og:image:height"', tag):
            return re.sub(r'content="\d+"', 'content="630"', tag)
        return tag
    return META.sub(fix, html)


def folder_link(href: str) -> str:
    if href.startswith(SITE):
        rest = href[len(SITE):]
        return SITE + folder_link(rest) if rest.startswith('/') else href
    if re.match(r'^[a-z][a-z0-9+.-]*:|^//|^#', href, re.I):
        return href
    path, sep, tail = re.match(r'([^?#]*)([?#]?)(.*)', href).groups()
    if path == 'index.html':
        path = './'
    elif path.endswith('/index.html'):
        path = path[: -len('index.html')]
    return path + sep + tail


def links(html: str) -> str:
    return HREF.sub(lambda m: m.group(1) + m.group(2) + folder_link(m.group(3)) + m.group(2), html)


def menu_headings(html: str) -> str:
    h1 = html.find('<h1')
    if h1 < 0:
        return html
    before = H2.sub(lambda m: f'<p class="menu-heading">{m.group(2)}</p>', html[:h1])
    return before + html[h1:]


def main() -> None:
    changed = 0
    for page in sorted(ROOT.rglob('*.html')):
        rel = page.relative_to(ROOT)
        if any(part in SKIP for part in rel.parts):
            continue
        route = rel.as_posix()
        text = page.read_text(encoding='utf-8')
        out = links(share_image(route, head_meta(text)))
        if 'http-equiv="refresh"' not in out:
            out = menu_headings(out)
        if out != text:
            page.write_text(out, encoding='utf-8', newline='\n')
            changed += 1
    print(f'Audit Nov 6: {changed} pages updated (referrer, CSP, share images, folder links, menu titles).')


main()
