#!/usr/bin/env python3
"""The rebuilt Merch view (Dom, Nov 22, 2026: "make it real"; then, after the new Home went live,
"nothing changed besides the home screen").

Runs right after apply_new_live.py in build_site.py.

What Dom approved on the local concept:
- the same look as the new Home, the designs as cards with every piece and its price as a row;
- two designs added that are in the shop but were not on the site, Trans Heart (five pieces) and
  You Can't Change Us (one tee): "yes and use the prices i chose". The prices are the ones set in
  the shop on Nov 22, 2026, the same low-end prices as the other designs ("i kept the prices on the
  lower end, i dont want to look greedy");
- so the count line reads "Seven designs, twenty-four pieces."

How: this step changes only the Merch view inside index.html (id="v-merch"). The five designs
already there, their links and prices are untouched. It adds the two cards from
.github/new-home/merch-cards.part after them, fixes the count line, and adds the look as one
<style> block from .github/new-home/merch.css just before the view. Heading sizes are left to the
size caps stylesheet.

To go back to the old Merch view, remove this script's line from build_site.py and rebuild.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
SRC = ROOT / '.github/new-home'
MARK = '<!-- NEW MERCH VIEW (Dom, Nov 22, 2026) -->'
OPEN = '<div class="view" id="v-merch" hidden>'
COUNT_OLD = 'Five designs, eighteen pieces.'
COUNT_NEW = 'Seven designs, twenty-four pieces.'
CARDS_END = '    </div>\n    <div class="row"><a class="btn ghost" href="https://ghostheart-studios-shop.fourthwall.com"'

html = HOME.read_text(encoding='utf-8')
if MARK not in html:
    assert html.count(OPEN) == 1, 'Merch view not found'
    start = html.index(OPEN)
    end = html.index('</main>', start)
    view = html[start:end]
    assert view.count(COUNT_OLD) == 1 and view.count(CARDS_END) == 1, 'Merch view changed upstream'
    assert view.count('<article class="m-card">') == 5 and view.count('fourthwall.com/products/') == 18
    cards = (SRC / 'merch-cards.part').read_text(encoding='utf-8')
    css = (SRC / 'merch.css').read_text(encoding='utf-8')
    view = view.replace(COUNT_OLD, COUNT_NEW).replace(CARDS_END, cards + CARDS_END)
    html = html[:start] + MARK + '\n<style id="nm-style">\n' + css + '</style>\n' + view + html[end:]
    HOME.write_text(html, encoding='utf-8')
    print('Merch view: rebuilt layout, seven designs, twenty-four pieces.')

t = HOME.read_text(encoding='utf-8')
assert t.count(MARK) == 1 and t.count('id="nm-style"') == 1 and t.count('id="v-merch"') == 1
assert t.count('<h1') == 1, 'the page must keep exactly one main heading'
view = t[t.index(OPEN):t.index('</main>', t.index(OPEN))]
assert view.count('<article class="m-card">') == 7 and view.count('fourthwall.com/products/') == 24
assert COUNT_NEW in view and COUNT_OLD not in view
assert view.count('<div') == view.count('</div>'), 'Merch view tags do not balance'
for picture in ('assets/protector/merch-trans-heart.jpg', 'assets/protector/merch-you-cant-change-us.jpg'):
    assert (ROOT / picture).is_file(), f'missing picture: {picture}'
