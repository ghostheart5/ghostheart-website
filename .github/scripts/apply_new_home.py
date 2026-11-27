#!/usr/bin/env python3
"""The rebuilt home page (Dom, Nov 22, 2026: "i want you to rebuild my homepage ... make it real").

Runs after apply_no_veterans_home.py in build_site.py, before the social links, size caps,
Google Analytics, meta and sitemap steps.

What Dom asked for and approved on the local concept (Nov 21 and 22):
- "fix the tabs so about is next to home, name about something else" -> the About tab is named
  GhostHeart ("just GhostHeart") and sits next to Home. Find Support is a red button.
- "remove the square image of the heart wakes and put effects on the big ghostheart scars wake the
  heart" and "can you zoom out" -> the Scars Wakes the Heart picture is shown whole, with a wake-up
  on load, a heartbeat glow, rain and lightning. People who turn motion off get the still picture.
  Then "the top picture is huge" -> it is 600px wide at most, inside the normal picture limit.
- The Tribute Song on the front page's merch row: "keep it off". The words that had gone
  missing from Home (the Heart Wakes line, The Silver Thread and its heart, the paint wall, the
  silver and black sliding bands): "fix it" -> they show again.
- "now fix the banner where the tabs are" -> bigger logo, slanted tabs, a red line under the bar.
- "normal size website" -> one normal-width column, less scrolling.

How: this step changes only index.html. It keeps everything the earlier steps built and the page's
own script relies on (the weekly Featured week blocks and their date switches, today's line, the
Silver Thread sign-up, the song player, and the Vault / About / Live / Merch views). It
- renames and reorders the menu and footer links,
- swaps the top banner for the animated one (same picture file),
- wraps the Sunday Live and sign-up blocks so they sit side by side,
- adds a row of merch pictures that opens the Merch view,
- and adds the new look as one <style> block from .github/new-home/home.css.
The size caps stylesheet is still the last stylesheet link, but this <style> block comes after it in
the page and a few of its rules are strong enough to beat a cap, so the size guard
(test_size_caps.cjs), which measures the finished page, is what protects the sizes on Home.
This change raises no size limit: test_size_caps.cjs is the same as before.

To go back to the old home page, remove this script's line from build_site.py and rebuild.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
SRC = ROOT / '.github/new-home'
MARK = '<!-- NEW HOME (Dom, Nov 22, 2026) -->'

NAV_OLD = ('<a href="#home" data-nav="home">Home</a><a href="#vault" data-nav="vault">The Vault</a>'
           '<a href="#story" data-nav="story">About</a><a href="#live" data-nav="live">Live</a>')
NAV_NEW = ('<a href="#home" data-nav="home">Home</a><a href="#story" data-nav="story">GhostHeart</a>'
           '<a href="#vault" data-nav="vault">The Vault</a><a href="#live" data-nav="live">Live</a>')
SUPPORT_OLD = '<a href="/GhostHeart_Resources.html">Find Support</a>\n  </nav>'
SUPPORT_NEW = '<a class="support" href="/GhostHeart_Resources.html">Find Support</a>\n  </nav>'
FOOT_OLD = '<a href="#vault">The Vault</a><a href="#story">About</a><a href="#live">Live</a>'
FOOT_NEW = '<a href="#story">GhostHeart</a><a href="#vault">The Vault</a><a href="#live">Live</a>'
TOPBAN = re.compile(r'<div class="topban">\s*(<img [^>]*>)\s*</div>')
FIRE_OPEN = '<section class="fire2">'
THREAD_OPEN = re.compile(r'<section [^>]*id="thread"[^>]*>')


def once(text, old, new, what):
    assert text.count(old) == 1, f'{what}: expected exactly one, found {text.count(old)}'
    return text.replace(old, new)


html = HOME.read_text(encoding='utf-8')
if MARK not in html:
    css = (SRC / 'home.css').read_text(encoding='utf-8')
    wake = (SRC / 'wake.part').read_text(encoding='utf-8')
    merch = (SRC / 'merch-row.part').read_text(encoding='utf-8')

    # 1. menu and footer: About becomes GhostHeart, next to Home; Find Support is the button
    html = once(html, NAV_OLD, NAV_NEW, 'main menu')
    html = once(html, SUPPORT_OLD, SUPPORT_NEW, 'Find Support in the menu')
    html = once(html, FOOT_OLD, FOOT_NEW, 'footer links')

    # 2. the top picture: same file, shown whole, with the wake-up, heartbeat, rain and lightning
    found = TOPBAN.findall(html)
    assert len(found) == 1, 'top banner not found'
    html = TOPBAN.sub(lambda m: wake.replace('<!--PICTURE-->', m.group(1)), html)

    # 3. Sunday Live and the sign-up side by side, then the merch row
    threads = list(THREAD_OPEN.finditer(html))
    assert html.count(FIRE_OPEN) == 1 and len(threads) == 1
    start = html.index(FIRE_OPEN)
    thread_end = html.index('</section>', threads[0].start()) + len('</section>')
    assert start < thread_end
    html = html[:start] + '<div class="nh-pair">' + html[start:thread_end] + '</div>\n' + merch + html[thread_end:]

    # 4. the new look, right after the page's own styles (so it wins) and before anything paints
    body_at = html.index('<body>')
    style_end = html.index('</style>', body_at) + len('</style>')
    html = html[:style_end] + '\n' + MARK + '\n<style id="nh-style">\n' + css + '</style>' + html[style_end:]
    HOME.write_text(html, encoding='utf-8')
    print('Home page: rebuilt layout (GhostHeart tab, animated top picture, normal size).')

if __name__ != '__nocheck__':
    t = HOME.read_text(encoding='utf-8')
    assert t.count(MARK) == 1 and t.count('id="nh-style"') == 1
    assert t.count('<h1') == 1, 'the page must keep exactly one main heading'
    assert '>About</a>' not in t.split('<main')[0], 'the menu still says About'
    assert t.count('class="nh-wake') == 1 and 'class="topban"' not in t
    assert t.count('<div class="nh-pair">') == 1 and t.count('class="nh-wear') == 1
    for week in ('2', '3', '4'):
        assert f'data-week="{week}"' in t, f'featured week {week} is missing'
    assert 'id="q-text"' in t and 'id="join"' in t and 'id="player"' in t
