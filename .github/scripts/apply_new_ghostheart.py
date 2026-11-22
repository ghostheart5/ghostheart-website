#!/usr/bin/env python3
"""The rebuilt GhostHeart (About) view (Dom, Nov 22, 2026: "make it real"; then, after the new Home
went live, "nothing changed besides the home screen").

Runs right after apply_new_home.py in build_site.py.

What Dom approved on the local concept (Nov 21 and 22: "yes all 7"): the page in two parts
("Built from the heart" beside the picture, then "Behind the scars" with its three plates beside
the story), the hard lines pulled out big, a heartbeat line between the parts, and the ways onward
(whole story, the title song, a song, Find Support) in one row at the end.

Every word is the same as before; only the layout changed. The picture is still the Protected by
GhostHeart picture with its heartbeats: Dom is making a new picture for this spot, and it swaps in
here when it is ready.

How: this step changes only the About view inside index.html (id="v-story"). It keeps what the
page's own script needs: the #story landing spot, #banner with .banner-frame inside it, and a
<section> for the red strip the script adds on top. The look comes from .github/new-home/ghostheart.css,
added as one <style> block just before the view.

To go back to the old About view, remove this script's line from build_site.py and rebuild.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
SRC = ROOT / '.github/new-home'
MARK = '<!-- NEW GHOSTHEART VIEW (Dom, Nov 22, 2026) -->'
OPEN = '<div class="view" id="v-story" hidden>'
NEXT = '<!-- ================= LIVE'
TAGS = re.compile(r'<[^>]+>')


def words(html):
    """The visible words, in order, without tags or spacing differences."""
    return ' '.join(TAGS.sub(' ', html).split())


html = HOME.read_text(encoding='utf-8')
if MARK not in html:
    assert html.count(OPEN) == 1 and html.count(NEXT) == 1, 'About view not found'
    start = html.index(OPEN)
    end = html.index(NEXT)
    old = html[start:end]
    assert old.rstrip().endswith('</div>')

    pictures = re.findall(r'<div class="banner-frame">(.*?)\n    </div>\n  </div>', old, flags=re.S)
    assert len(pictures) == 1, 'About picture not found'
    picture = pictures[0].strip()
    safe = '<span class="stamp s safe">you’re safe here</span>'
    assert safe in picture
    picture = picture.replace(safe, '').strip()

    new = (SRC / 'ghostheart.part').read_text(encoding='utf-8').replace('<!--PICTURE-->', picture)
    css = (SRC / 'ghostheart.css').read_text(encoding='utf-8')

    # no word may be lost: every sentence of the old view must still be in the new one
    was, now = words(old), words(new)
    for piece in re.findall(r'<p[^>]*>(.*?)</p>', old, flags=re.S):
        text = words(piece)
        if text.startswith('Read the whole story'):
            text = 'Read the whole story: Behind the Scars'
        assert text in now or all(part in now for part in text.split(' · ')), f'About words missing: {text[:70]}'
    for line in ('Built from', 'the heart.', 'Behind', 'the scars', 'Not one wound', 'Not one label', 'Still here',
                 'Play The Heart Wakes', 'Stay with a song', 'no one has to disclose their own pain to belong here.',
                 'you’re safe here'):
        assert line in was and line in now, f'About words missing: {line}'

    html = html[:start] + MARK + '\n<style id="ng-style">\n' + css + '</style>\n' + new + '\n' + html[end:]
    HOME.write_text(html, encoding='utf-8')
    print('GhostHeart (About) view: rebuilt layout, same words.')

t = HOME.read_text(encoding='utf-8')
assert t.count(MARK) == 1 and t.count('id="ng-style"') == 1 and t.count('id="v-story"') == 1
assert t.count('<h1') == 1, 'the page must keep exactly one main heading'
view = t[t.index(OPEN):t.index(NEXT)]
assert 'id="story"' in view and 'id="banner"' in view and 'class="banner-frame"' in view and '<section' in view
assert view.count('<div') == view.count('</div>'), 'About view tags do not balance'
