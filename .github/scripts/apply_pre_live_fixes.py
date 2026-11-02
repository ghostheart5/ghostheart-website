#!/usr/bin/env python3
"""Pre-Live fixes (2026-11-01, owner: "GO" on the page-by-page audit).

Final build step. Plain text swaps on the finished pages (no re-parsing, so
nothing else on a page moves). Each swap runs only where its old text is
present, so the step is safe to run twice.

- Dead YouTube videos: Heart of the Ashes now uses the working official
  music video (G6_x8P5R1pA, owner's YouTube list, Nov 2); the This Is GhostHeart and Oath blog posts point to the
  working trailer (AOCRvtz92JM) and lyric video (mBAsUNX3vHQ).
- Music: the "What comes next" button names Sunday Lives, not the retired
  World Is Watching show.
- Films: the Oct 26 "new Short every day this week" note goes; upload notes
  ("Fixed vocal ending", "YouTube title: ...") become plain labels.
- Typos and names: "Human Afterall", "The Start campaign" (Blueprint: The
  Starts), the Work with GhostHeart page label, the Awakening page's
  "public reading" (readings are off the site).
- Sign-up note: the form no longer opens Mailchimp, so the note says to tap
  the link in the email instead.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SIGNUP_OLD = 'Mailchimp opens to finish signup. Confirm through the email it sends.'
SIGNUP_NEW = 'Then tap the link in the email Mailchimp sends you.'

SWAPS = {
    'GhostHeart_Songs.html': [
        ('Watch the fixed vocal ending video', 'Watch the video'),
    ],
    'journal/this-is-ghostheart.html': [
        ('https://www.youtube.com/watch?v=kF1Cc_GB6AM', 'https://www.youtube.com/watch?v=AOCRvtz92JM'),
    ],
    'journal/ghosthearts-oath.html': [
        ('https://www.youtube.com/watch?v=DQcl28CHE_o', 'https://www.youtube.com/watch?v=mBAsUNX3vHQ'),
    ],
    'music/index.html': [
        ('href="/live/">The World Is Watching ↗</a>', 'href="/live/">Sunday Lives ↗</a>'),
    ],
    'GhostHeart_Videos.html': [
        ('<p class="g-small">Fixed vocal ending</p>', '<p class="g-small">Broken Man</p>'),
        ('the life behind the name. Fixed vocal ending"', 'the life behind the name. Broken Man"'),
        ('Human Too cinematic remake · YouTube title: Why You Should Never Judge Someone\'s Worst Day', 'Human After All · cinematic remake'),
        ('Human Too cinematic remake YouTube title: Why You Should Never Judge Someone\'s Worst Day', 'Human After All cinematic remake'),
    ],
    'albums/broken-man/index.html': [
        ('<p class="g-small">Fixed vocal ending</p>', '<p class="g-small">Broken Man</p>'),
        ('the life behind the name. Fixed vocal ending"', 'the life behind the name. Broken Man"'),
    ],
    'albums/human-after-all/index.html': [
        ('<p>We are Human Afterall.</p>', '<p>We are Human After All.</p>'),
        ('Human Too cinematic remake · YouTube title: Why You Should Never Judge Someone\'s Worst Day', 'Human After All · cinematic remake'),
        ('Human Too cinematic remake YouTube title: Why You Should Never Judge Someone\'s Worst Day', 'Human After All cinematic remake'),
    ],
    'index.html': [
        ('The Start campaign kicks off January 4, 2027.', 'The Starts begins January 4, 2027.'),
    ],
    'here-to-help/index.html': [
        ('✶ GhostHeart Studios / I’m Here to Help</span>', '✶ GhostHeart Studios / Work with GhostHeart</span>'),
    ],
    'awakening/index.html': [
        ('Start with the public reading, listen to the songs, or watch', 'Listen to the songs, or watch'),
    ],
}

# The "New Short" note under the featured film (that week ended Nov 1).
OLD_SHORT = re.compile(r'<p class="new-short"><small>NEW SHORT · <time datetime="2026-10-26">.*?</p>', re.S)

changed = 0
for rel, swaps in SWAPS.items():
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    out = text
    for old, new in swaps:
        out = out.replace(old, new)
    if rel == 'GhostHeart_Videos.html':
        out = OLD_SHORT.sub('', out)
    if out != text:
        path.write_text(out, encoding='utf-8', newline='\n')
        changed += 1


signup = 0
for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if SIGNUP_OLD in text:
        path.write_text(text.replace(SIGNUP_OLD, SIGNUP_NEW), encoding='utf-8', newline='\n')
        signup += 1

print(f'Pre-Live fixes: {changed} pages fixed, sign-up note updated on {signup} pages.')
