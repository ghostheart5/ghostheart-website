#!/usr/bin/env python3
"""The rebuilt Live view (Dom, Nov 22, 2026: "make it real"; then, after the new Home went live,
"nothing changed besides the home screen").

Runs right after apply_new_vault.py in build_site.py.

What Dom said about this page on the local concept (Nov 22): "change the 1 2 3. i dont want the
comment part, i removed it from the live, just do words from the heart. ghostheart words and quotes
that touched ghosthearts heart". So:
- the three numbered steps (One picture / The story / Your turn) are gone, and so is the line about
  an hour of picture quotes and the comments;
- the page says what the Live is in his words: "GhostHeart's words, and quotes that touched
  GhostHeart's heart.";
- Sundays, 10 AM Central and TikTok are three plates; today's line sits beside them (the same line
  Home shows); the Watch on TikTok button stays;
- the care line stays, with "creative community space" in place of "creative community
  conversation" (wording he approved on the concept: "wording is fine");
- "Take a seat" at the end opens the one sign-up on Home. The page keeps one sign-up form.

How: this step replaces only the Live view inside index.html (id="v-live"). It keeps what the page's
script and the site tests need: the #live landing spot, a <section>, and one <h2> that reads
"Words from the heart". The look comes from .github/new-home/live.css, added as one <style> block
just before the view.

To go back to the old Live view, remove this script's line from build_site.py and rebuild.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
SRC = ROOT / '.github/new-home'
MARK = '<!-- NEW LIVE VIEW (Dom, Nov 22, 2026) -->'
OPEN = '<div class="view" id="v-live" hidden>'
NEXT = '<!-- ================= MERCH'

html = HOME.read_text(encoding='utf-8')
if MARK not in html:
    assert html.count(OPEN) == 1 and html.count(NEXT) == 1, 'Live view not found'
    start, end = html.index(OPEN), html.index(NEXT)
    old = html[start:end]
    assert old.rstrip().endswith('</div>') and '<div class="view"' not in old[len(OPEN):]
    # what must carry over from the old view, word for word
    for keep in ('<b>Sundays</b> · 10 AM Central · TikTok', 'https://www.tiktok.com/@ghosthearted1',
                 'The next live date shows here only once it’s confirmed.',
                 'If you need more than a song can give, <a href="/GhostHeart_Resources.html">Find Support</a> is here.'):
        assert keep in old, f'Live view changed upstream: {keep[:50]}'
    new = (SRC / 'live.part').read_text(encoding='utf-8')
    css = (SRC / 'live.css').read_text(encoding='utf-8')
    html = html[:start] + MARK + '\n<style id="nl-style">\n' + css + '</style>\n' + new + '\n' + html[end:]
    HOME.write_text(html, encoding='utf-8')
    print('Live view: rebuilt layout, Words from the Heart only.')

t = HOME.read_text(encoding='utf-8')
assert t.count(MARK) == 1 and t.count('id="nl-style"') == 1 and t.count('id="v-live"') == 1
assert t.count('<h1') == 1, 'the page must keep exactly one main heading'
assert t.count('<form') == 1, 'the page must keep exactly one sign-up form'
view = t[t.index(OPEN):t.index(NEXT)]
assert 'id="live"' in view and '<section' in view and view.count('<h2') == 1
assert view.count('<div') == view.count('</div>'), 'Live view tags do not balance'
for gone in ('One picture', 'Your turn', 'comments', 'picture quotes'):
    assert gone not in view, f'Live view still says: {gone}'
for there in ('Sundays', '10 AM Central', 'TikTok', 'GhostHeart’s words, and quotes that touched GhostHeart’s heart.',
              'The next live date shows here only once it’s confirmed.', 'https://www.tiktok.com/@ghosthearted1'):
    assert there in view, f'Live view is missing: {there}'
