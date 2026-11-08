#!/usr/bin/env python3
"""Week 1 premiere (Dom, Nov 8, 2026). Runs last in build_site.py.

Dom: "MONDAY SHOULD BE ONLY- 9AM-TIKTOK/INSTAGRAM, 12 PRIEMERE, 6PM TIKTOK/INSTAGRAM. THE WEBSITE PREMIERE IS ALSO AT 12"
and "THE HEART WAKES WAS A DRAFT AND IS CURRENTLY BEING FINISHED".

- Week 1 (To Those Who Served) opens on the home page Monday, Nov 9, 2026 at 12 PM Central, not Sunday 7 PM.
  Later weeks keep their Sunday 7 PM opening.
- Before a week opens, its songs are listed by name only, with no player, so nothing plays before the premiere.
- The song "The Heart Wakes" is held off the site until Dom finishes it: it leaves Week 1 and has no player.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / 'assets/wake-v3/site.js'

SWAPS = [
    ('{nm:"To Those Who Served",up:"2026-11-08",a:', '{nm:"To Those Who Served",up:"2026-11-08",at:"2026-11-09 12:00",a:'),
    ('songs:["The Heart Wakes","To Those Who Served"]', 'songs:["To Those Who Served"]'),
    ('if(NOW>=w.up+" 19:00")live=i', 'if(NOW>=(w.at||w.up+" 19:00"))live=i'),
    ('(up?"Out now":"Goes up Sunday night")', '(up?"Out now":(w.at?"Premieres Monday at 12 PM Central":"Goes up Sunday night"))'),
    ('var songs=(w.songs||[w.nm]).map(songLi).join("");',
     'var songs=(w.songs||[w.nm]).map(up?songLi:function(x){return \'<li>\'+x+\'</li>\'}).join("");'),
    ('AUDIO={"The Heart Wakes":"/assets/wake-v3/audio/the-heart-wakes.mp3",', 'AUDIO={'),
]


def main() -> None:
    s = JS.read_text(encoding='utf-8')
    t = s
    for old, new in SWAPS:
        if old in t:
            assert t.count(old) == 1, old
            t = t.replace(old, new)
    if t != s:
        JS.write_text(t, encoding='utf-8')
    assert 'the-heart-wakes.mp3' not in t and '"The Heart Wakes","To Those Who Served"' not in t
    print('Week 1 premieres Monday 12 PM Central; no players before a week opens; The Heart Wakes held off the site.')


main()
