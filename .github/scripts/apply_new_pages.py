#!/usr/bin/env python3
"""The new look on the separate pages in the top bar (Dom, Nov 22, 2026: "make it real"; then,
after the new Home went live, "nothing changed besides the home screen").

Runs after the Home steps in build_site.py, before the social links, size caps, Google Analytics,
meta and sitemap steps.

Every page listed in PAGES below gets:
- the same eight tabs as Home (Home, GhostHeart, The Vault, Live, Work with GhostHeart, Projects,
  Merch, Find Support), Find Support as the red button;
- the new look from /assets/new-look/pages.css, linked right after the shared site.css. The size
  caps stylesheet is still added last by apply_size_caps.py, so it keeps the last word.
Pages not listed keep the older top bar and look.

Work with GhostHeart (here-to-help/index.html), approved on the local concept:
- "dont change the fact that it doesnt push the money like i want it": prices stay folded away
  under "Service details and prices", exactly as before;
- new: "What finished work looks like", four made-up example jobs (Dom: "yes" to making them), and
  one real finished job, To Those Who Served;
- the request form, the email line, the price list and the custom song block are the same HTML as
  before, moved into the new layout, so the form scripts and the order tests see no difference.
Two lines of the concept are worded differently here to keep Dom's standing rules: the song is "a
tribute song" (Nov 21: nothing should say veterans), and the line about which tools made the track
is left out (no AI labels).

To go back, remove this script's line from build_site.py and rebuild.
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / '.github/new-home'
MARK = '<!-- NEW LOOK (Dom, Nov 22, 2026) -->'
CSS_LINK = '<link rel="stylesheet" href="/assets/new-look/pages.css">'
SITE_CSS = '<link rel="stylesheet" href="/assets/wake-v3/site.css">'
FONT_OLD = 'family=Anton&amp;family=Bebas+Neue'
FONT_NEW = 'family=Anton&amp;family=Sedgwick+Ave+Display&amp;family=Bebas+Neue'
NAV = [('/', 'Home'), ('/#story', 'GhostHeart'), ('/#vault', 'The Vault'), ('/#live', 'Live'),
       ('/here-to-help/', 'Work with GhostHeart'), ('/GhostHeart_Projects.html', 'Projects'),
       ('/#merch', 'Merch'), ('/GhostHeart_Resources.html', 'Find Support')]
NAV_RE = re.compile(r'<nav aria-label="Main" class="menu" id="menu">.*?</nav>', re.S)
MAIN_RE = re.compile(r'<main id="main">.*?</main>', re.S)
TAGS = re.compile(r'<[^>]+>')


def words(html):
    return ' '.join(TAGS.sub(' ', html).split())


def shell(html, path):
    """The top bar, the font and the stylesheet. `path` is the page's own address."""
    assert len(NAV_RE.findall(html)) == 1, f'{path}: menu not found'
    links = []
    for href, name in NAV:
        extra = ' aria-current="page"' if href == path else ''
        extra += ' class="support"' if name == 'Find Support' else ''
        links.append(f'<a{extra} href="{href}">{name}</a>')
    html = NAV_RE.sub(lambda m: '<nav aria-label="Main" class="menu" id="menu">\n' + '\n'.join(links) + '\n</nav>', html)
    assert html.count(SITE_CSS) == 1 and html.count(FONT_OLD) == 1, f'{path}: stylesheet or font link not found'
    html = html.replace(SITE_CSS, SITE_CSS + CSS_LINK).replace(FONT_OLD, FONT_NEW)
    body = re.search(r'<body([^>]*)>', html)
    assert body and 'class=' not in body.group(1), f'{path}: body tag changed'
    return html.replace(body.group(0), f'<body class="newlook"{body.group(1)}>\n{MARK}', 1)


def work(html):
    old_main = MAIN_RE.search(html)
    assert old_main, 'Work page: main not found'
    doc = BeautifulSoup(old_main.group(0), 'html.parser')
    form = doc.select_one('form#help-form')
    label = form.find('p', class_='mono')
    assert label and label.get_text(strip=True) == 'Tell me what you need'
    label.decompose()                        # it is the card's heading now
    form['class'] = [c for c in form.get('class', []) if c != 'panel']
    prices = doc.select_one('.help-side details.more')
    prices['class'] = [c for c in prices.get('class', []) if c != 'panel']
    song = doc.select_one('.song-opt')
    song_label = song.find('p', class_='mono')
    assert song_label and song_label.get_text(strip=True) == 'A song from your story'
    song_label.decompose()
    for el in song.select('[style]'):
        del el['style']
    song_inner = ''.join(str(c) for c in song.contents).strip()
    new = (SRC / 'work.part').read_text(encoding='utf-8')
    for mark, piece in (('<!--HELP-FORM-->', str(form)), ('<!--PRICES-->', str(prices)), ('<!--SONG-->', song_inner)):
        assert new.count(mark) == 1
        new = new.replace(mark, piece)
    # nothing the old page said may be lost
    now = words(new)
    for el in BeautifulSoup(old_main.group(0), 'html.parser').select('h1, p, li, td, th, summary, label, option, button, a'):
        text = words(str(el))
        assert not text or text in now, f'Work page words missing: {text[:70]}'
    return html[:old_main.start()] + new.rstrip('\n') + html[old_main.end():]


PAGES = {'here-to-help/index.html': ('/here-to-help/', work)}

for relative, (path, body) in PAGES.items():
    page = ROOT / relative
    html = page.read_text(encoding='utf-8')
    if MARK not in html:
        html = body(shell(html, path))
        page.write_text(html, encoding='utf-8')
        print(f'New look: {relative}')
    t = page.read_text(encoding='utf-8')
    assert t.count(MARK) == 1 and t.count(CSS_LINK) == 1 and t.count('<h1') == 1, relative
    assert t.index(SITE_CSS) < t.index(CSS_LINK), relative
    assert [words(a) for a in re.findall(r'<a[^>]*>.*?</a>', NAV_RE.search(t).group(0), flags=re.S)] == [n for _, n in NAV], relative
assert (ROOT / 'assets/new-look/pages.css').is_file()
for sample in ('resume', 'flyer', 'deck', 'tracker'):
    assert (ROOT / f'assets/work-samples/{sample}.pdf').is_file() and (ROOT / f'assets/work-samples/{sample}.jpg').is_file(), sample
