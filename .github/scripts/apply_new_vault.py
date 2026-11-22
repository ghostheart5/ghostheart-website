#!/usr/bin/env python3
"""The rebuilt Vault view (Dom, Nov 22, 2026: "make it real"; then, after the new Home went live,
"nothing changed besides the home screen").

Runs right after apply_new_ghostheart.py in build_site.py.

What Dom approved on the local concept: the name on the left and the search on the right, the album
with its songs as rows, and under it "Out as videos": the songs that are out on YouTube (To Those
Who Served, The Parts You Hide, The Man Beneath the Moon, and Too Small from Wednesday Nov 25,
4 PM Central).

How: this step changes only the Vault view inside index.html (id="v-vault"). The view's own words,
search box, feeling buttons, song list and player are untouched; the page's script still builds
them. This step adds the "Out as videos" block after the view's section, and the look as one
<style> block from .github/new-home/vault.css just before the view. Heading sizes are left to the
size caps stylesheet.

To go back to the old Vault view, remove this script's line from build_site.py and rebuild.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
SRC = ROOT / '.github/new-home'
MARK = '<!-- NEW VAULT VIEW (Dom, Nov 22, 2026) -->'
OPEN = '<div class="view" id="v-vault" hidden>'
SECTION_END = '  </div></div></section>\n</div>'

html = HOME.read_text(encoding='utf-8')
if MARK not in html:
    assert html.count(OPEN) == 1, 'Vault view not found'
    start = html.index(OPEN)
    end = html.index(SECTION_END, start)
    assert '<div class="view"' not in html[start + len(OPEN):end], 'Vault view end not found'
    videos = (SRC / 'vault-videos.part').read_text(encoding='utf-8')
    css = (SRC / 'vault.css').read_text(encoding='utf-8')
    cut = end + len('  </div></div></section>\n')
    html = (html[:start] + MARK + '\n<style id="nv-style">\n' + css + '</style>\n'
            + html[start:cut] + videos + html[cut:])
    HOME.write_text(html, encoding='utf-8')
    print('Vault view: rebuilt layout, with the Out as videos list.')

t = HOME.read_text(encoding='utf-8')
assert t.count(MARK) == 1 and t.count('id="nv-style"') == 1 and t.count('id="v-vault"') == 1
assert t.count('<h1') == 1, 'the page must keep exactly one main heading'
view = t[t.index(OPEN):t.index('<!-- ================= STORY')]
for piece in ('id="vault"', 'id="vq"', 'id="moods"', 'id="vcount"', 'id="albums"', 'id="nv-vids"'):
    assert view.count(piece) == 1, f'Vault view: {piece} should be there once'
assert view.count('class="nv-vid"') == 4 and view.count('<div') == view.count('</div>')
