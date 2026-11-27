#!/usr/bin/env python3
"""No veterans on the home page (Dom, Nov 21, 2026: "Nothing in bios or anything should say veterans anymore";
yes to this website draft Nov 21, 8:53 PM Central).

Runs after the week scripts in build_site.py, because apply_week2_home.py still finds the old Week 01 block in home.part.
- Takes out the Week 01 · Veterans Day featured block. Week 2 becomes the block that shows when no script has run;
  the week 3 and week 4 switches still pick the right week by date.
- Takes the "New · Veterans Day week" tag off the The Tribute Song merch card. The card itself stays.
- The banner picture's description says "a person with the flag" instead of "a veteran with the flag".
Left alone on purpose: the song's own lyrics in the player, and the Veterans Crisis Line and veterans housing line on the Find Support page, which are help, not promotion.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'

WEEK1 = re.compile(r'\n?[ \t]*<section[^>]*\bdata-week="1"[^>]*>.*?</section>\n?', re.S)
WEEK2_OPEN = re.compile(r'<section[^>]*\bdata-week="2"[^>]*>')
STAMP = re.compile(r'<span[^>]*>New · Veterans Day week</span>')
ALT_OLD = 'a veteran with the flag'
ALT_NEW = 'a person with the flag'


def main() -> None:
    s = HOME.read_text(encoding='utf-8')
    t = WEEK1.sub('\n', s, count=1)
    t = WEEK2_OPEN.sub(lambda m: re.sub(r'\s+hidden(?=[\s>])', '', m.group(0)), t, count=1)
    t = STAMP.sub('', t)
    t = t.replace(ALT_OLD, ALT_NEW)
    if t != s:
        HOME.write_text(t, encoding='utf-8')
    assert WEEK1.search(t) is None, 'Week 01 block still on the home page'
    assert 'Veterans Day' not in t and ALT_OLD not in t, 'home page still says veterans'
    w2 = WEEK2_OPEN.search(t)
    assert w2 and ' hidden' not in w2.group(0), 'week 2 block missing or still hidden by default'
    print('Home page no longer mentions veterans.')


main()
