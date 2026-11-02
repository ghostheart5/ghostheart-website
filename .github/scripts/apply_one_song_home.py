#!/usr/bin/env python3
"""ONE HOME FOR THE 11 SONGS (owner 2026-11-02: "Fix the bigger jobs now", from the page-by-page audit).

The same eleven song previews were listed three times: Music (/music/), /albums/ and the Songs page.
Music is now their only home:
  * every link to /albums/... goes to /music/ (a song link lands on that song: #track-x -> #song-x),
  * /albums/ becomes a short page that forwards to Music (old shared links keep working),
  * the Songs page keeps only its Released recordings archive (its copy of the 11 previews is removed),
  * /albums/ leaves the site map.
Runs last in build_site.py so it covers every generated page.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
MUSIC = (ROOT / 'music/index.html').read_text(encoding='utf-8')
SONG_IDS = set(re.findall(r'id="song-([a-z0-9-]+)"', MUSIC))
assert len(SONG_IDS) == 11, SONG_IDS

LINK = re.compile(r'href="(?:https://www\.myghostheart\.com)?/albums/(?:index\.html)?(?:#([a-z0-9-]+))?"')


def new_href(match):
    frag = match.group(1)
    if frag and frag.startswith('track-'):
        slug = frag[len('track-'):]
        if slug not in SONG_IDS:
            raise ValueError(f'No song on Music for {frag}')
        return f'href="/music/#song-{slug}"'
    if frag in (None, 'awakening', 'youre-not-god'):
        return 'href="/music/#listen"' if frag else 'href="/music/"'
    raise ValueError(f'Unknown /albums/ anchor #{frag}')


FORWARD = '''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Music | GhostHeart</title><meta name="description" content="GhostHeart's songs live on the Music page."/><meta name="robots" content="noindex"/><link rel="canonical" href="https://www.myghostheart.com/music/"/>
<meta http-equiv="refresh" content="0; url=/music/"/>
<script>(function(){var h=location.hash;var m=/^#track-([a-z0-9-]+)$/.exec(h);location.replace('/music/'+(m?'#song-'+m[1]:(h==='#awakening'||h==='#youre-not-god')?'#listen':''));})();</script>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b0b0d;color:#f4efe6;font:18px/1.5 system-ui,sans-serif}a{color:#ff5a3c}</style>
</head><body><main><h1>Music</h1><p>The songs live on the Music page now. <a href="/music/">Go to Music →</a></p></main></body></html>
'''

SONG_FORWARD = ('<script data-song-forward="">(function(){var m=/^#song-audio-track-([a-z0-9-]+)$/.exec(location.hash);'
                'if(m)location.replace(\'/music/#song-\'+m[1]);})();</script>')


def main():
    changed = 0
    for path in ROOT.rglob('*.html'):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(('.github/', 'node_modules/')) or rel == 'albums/index.html':
            continue
        text = path.read_text(encoding='utf-8')
        new = LINK.sub(new_href, text)
        if rel == 'GhostHeart_Songs.html':
            new = new.replace('<a href="#existing-audio">Song previews</a>', '')
            new = new.replace('>Featured listening collections</a>', '>Music: the 11 song previews</a>')
            new, n = re.subn(r'<section aria-labelledby="existing-audio-title" class="g-section" id="existing-audio">.*?</ol></section></div></section>', '', new, flags=re.S)
            if n != 1 and 'id="existing-audio"' in new:
                raise ValueError('Songs page preview list not found')
            if 'data-song-forward' not in new:  # old shared links to a preview row land on that song in Music
                new = new.replace('</body>', SONG_FORWARD + '</body>', 1)
        if new != text:
            path.write_text(new, encoding='utf-8', newline='\n')
            changed += 1
    (ROOT / 'albums/index.html').write_text(FORWARD, encoding='utf-8', newline='\n')
    sm = ROOT / 'sitemap.xml'
    s = sm.read_text(encoding='utf-8')
    s2 = re.sub(r'\s*<url>\s*<loc>https://www\.myghostheart\.com/albums/</loc>.*?</url>', '', s, flags=re.S)
    if s2 != s:
        sm.write_text(s2, encoding='utf-8', newline='\n')
    print('One song home: /albums/ forwards to Music;', changed, 'pages re-pointed')


main()
