#!/usr/bin/env python3
"""When It Isn't Your Kitchen headline strip on every page (Dom, Nov 19, 2026, 19:07 UTC: "needs to go on distrokid as a single
and be the feature and main attraction across all my platforms. I want it headlined"; plan yes Nov 19, 22:06 UTC; release day
Monday, Nov 23 picked on the card at 20:52 UTC).

Adds one script tag (/assets/shared/kitchen-strip.js, no inline script) before </head> on every page. The script draws a slim strip at
the top of the page: "NEW SINGLE · When It Isn't Your Kitchen · Out Monday, Nov 23, 4 PM Central". At OUT_AT (Central) it says
"Out now" and links to LISTEN_URL, else VIDEO_URL, else the YouTube channel. Before OUT_AT it links to PRESAVE_URL, else the channel.
It hides itself at UNTIL (end of the 16 Days of Activism). Set SHOW = False and rebuild to remove it everywhere.
"""
from pathlib import Path
import re
from html import escape

ROOT = Path(__file__).resolve().parents[2]
SKIP = ('.github', '.git', 'node_modules', 'apps')
# Support pages stay calm: no promo strip above the crisis lines (Checker note, Nov 20).
CALM = ('GhostHeart_Resources.html', 'here-to-help/index.html')

SHOW = True
CHANNEL = 'https://www.youtube.com/@GhostHeart-M95RTK'
PRESAVE_URL = ''  # DistroKid pre-save (HyperFollow) link, once Dom sends it
VIDEO_URL = 'https://www.youtube.com/watch?v=z00btt9OHWg'  # Kitchen music video (v07d), public Mon, Nov 23, 4 PM Central
LISTEN_URL = ''   # streaming link page, once the stores are live
OUT_AT = '2026-11-23 16:00'
UNTIL = '2026-12-11 00:00'
WHEN = 'Out Monday, Nov 23 · 4 PM Central'

TAG_ID = 'kitchen-strip-js'
# Any earlier copy of the tag, whatever its attribute order (later build steps re-write tags and sort attributes).
OLD_TAG = re.compile(r'<script\b[^>]*\bid="' + TAG_ID + r'"[^>]*>\s*</script>')


def tag() -> str:
    attrs = {'channel': CHANNEL, 'presave': PRESAVE_URL, 'video': VIDEO_URL, 'listen': LISTEN_URL,
             'out-at': OUT_AT, 'until': UNTIL, 'when': WHEN}
    data = ' '.join(f'data-{k}="{escape(v, quote=True)}"' for k, v in attrs.items())
    return f'<script defer id="{TAG_ID}" src="/assets/shared/kitchen-strip.js" {data}></script>'


def main() -> None:
    n = 0
    t = tag()
    for p in sorted(ROOT.rglob('*.html')):
        rel = p.relative_to(ROOT).as_posix()
        if rel.split('/')[0] in SKIP or '/node_modules/' in rel:
            continue
        old = p.read_text(encoding='utf-8')
        if '</head>' not in old:
            continue
        new = OLD_TAG.sub('', old)  # settings may have changed since the last build: always write a fresh tag
        show = SHOW and rel not in CALM
        if show:
            new = new.replace('</head>', t + '</head>', 1)
        assert new.count(f'id="{TAG_ID}"') == (1 if show else 0), rel
        if new != old:
            p.write_text(new, encoding='utf-8')
            n += 1
    print(f'Kitchen headline strip: added to {n} pages.' if SHOW else 'Kitchen headline strip: off.')


main()
