#!/usr/bin/env python3
"""The new home page: Protected by GhostHeart (Dom, Nov 11, 2026: "get the new website up").

Runs after apply_veterans_home.py in build_site.py, before Google Analytics and the meta and sitemap steps.

The page is the prototype Dom reviewed (Nov 10 and 11): the Protected by GhostHeart banner, the
studio wall, The Heart Wakes, the protector featured week (steel, black, one crimson heartbeat),
today's line, Sundays at the fire, and the Silver Thread signup. The Vault, About, Live and Merch
open on the same page (#vault, #story, #live, #merch). Work with GhostHeart, Projects and
Find Support go to their existing pages, where their forms already work.

Source: .github/protector-site/home.part (styles, page and script). Pictures: assets/protector/
and assets/wake-v3/img/. Songs: assets/wake-v3/audio/ and assets/music/preview/.
The head (title, share card, security policy, analytics) is kept from the page built before this step.
The signup posts to the same Mailchimp list as before. The fire box sends nothing.

To go back to the old home page, remove this script's line from build_site.py and rebuild.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'index.html'
SOURCE = ROOT / '.github/protector-site/home.part'
MARK = '<!-- PROTECTOR HOME (Dom, Nov 11, 2026) -->'
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Bebas+Neue&amp;family=IBM+Plex+Mono:wght@400;500;600'
         '&amp;family=Saira+Stencil+One&amp;family=Sedgwick+Ave&amp;family=Sedgwick+Ave+Display&amp;family=Space+Grotesk:wght@400;500;700'
         '&amp;display=swap" rel="stylesheet">')

html = HOME.read_text(encoding='utf-8')
if MARK not in html:
    head = html[:html.index('</head>')]
    head = re.sub(r'<link [^>]*href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>', FONTS, head, count=1)
    head = re.sub(r'\s*<link rel="stylesheet" href="/assets/wake-v3/site\.css">', '', head)
    head = head.replace('<meta name="viewport" content="width=device-width, initial-scale=1"/>',
                        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>')
    body = SOURCE.read_text(encoding='utf-8')
    HOME.write_text(head + '</head>\n<body>\n' + MARK + '\n' + body + '</body>\n</html>\n', encoding='utf-8')
    print('Home page: Protected by GhostHeart.')
