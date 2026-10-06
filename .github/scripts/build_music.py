#!/usr/bin/env python3
"""Build the two-group local Music listening page from verified track data."""
import argparse
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / '.github/content/music.json'
AWAKENING = ["Cruel", "I'm Not", "Papa Didn't Raise a Fool", "She Got to Me", "This Is GhostHeart", "GhostHeart's Oath", "You Can Be GhostHeart Too", "One Heart Many Voices"]
YNG = ["I Won't Pretend to Speak for You", "Hey Preacher Man", "That Ain't Holy"]


def shell_piece(text):
    text = re.sub(r' aria-current="[^"]*"', '', text)
    text = re.sub(r'href="#([^"]+)"', r'href="/index.html#\1"', text)
    return re.sub(r'(href|src)="(?!https?:|/|#)([^"]+)"', r'\1="/\2"', text)


def build(check=False):
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    groups = data['groups']
    assert [g['id'] for g in groups] == ['awakening', 'youre-not-god']
    assert [t['title'] for t in groups[0]['tracks']] == AWAKENING
    assert [t['title'] for t in groups[1]['tracks']] == YNG
    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    header = shell_piece(re.search(r'<header\b.*?</header>', home, re.S).group())
    header = header.replace('<a href="/albums/index.html">Music</a>', '<a aria-current="page" href="/albums/index.html">Music</a>')
    footer = shell_piece(re.search(r'<footer\b.*?</footer>', home, re.S).group())
    sections = []
    for group in groups:
        rows = []
        for number, track in enumerate(group['tracks'], 1):
            audio = track['audio']
            if audio:
                path = ROOT / audio.lstrip('/')
                if not path.is_file() or path.stat().st_size < 100_000:
                    raise ValueError(f'Playable audio missing or empty: {track["title"]}')
                player = (f'<audio controls preload="none" aria-label="Play {escape(track["title"], quote=True)}">'
                          f'<source src="{escape(audio, quote=True)}" type="audio/mpeg"/>'
                          'Your browser does not support this audio player.</audio>')
            else:
                player = '<p class="music-unavailable">Audio for this exact track is being verified.</p>'
            youtube = (f'<a class="music-youtube" href="{escape(track["youtube"], quote=True)}" target="_blank" rel="noopener noreferrer"'
                       f' aria-label="Open {escape(track["title"], quote=True)} on YouTube">YouTube ↗</a>') if track['youtube'] else ''
            recording_note = (f'<p class="music-recording-title">Audio recording: {escape(track["recording_title"])}</p>'
                              if track.get('recording_title') else '')
            rows.append(f'<li class="music-track"><div class="music-track-heading"><span class="music-number">{number:02d}</span>'
                        f'<h3>{escape(track["title"])}</h3>{youtube}</div>{recording_note}{player}</li>')
        sections.append(f'<section class="music-group" id="{group["id"]}" aria-labelledby="{group["id"]}-title">'
                        f'<div class="music-group-head"><p class="ghx-kicker">{len(group["tracks"])} songs</p>'
                        f'<h2 id="{group["id"]}-title">{escape(group["title"])}</h2><p>{escape(group["description"])}</p></div>'
                        f'<ol class="music-tracks">{"".join(rows)}</ol></section>')
    body = f'''<div class="music-page ghx-wrap"><header class="music-hero"><p class="ghx-kicker">GhostHeart / Music</p>
<h1>Listen to the songs.</h1><p class="ghx-lead">Start with GhostHeart's Awakening or You're Not God. Play the audio here, then follow a song to YouTube when a matching video is available.</p>
<nav class="music-jump" aria-label="Music groups"><a href="#awakening">GhostHeart's Awakening</a><a href="#youre-not-god">You're Not God</a></nav></header>
{''.join(sections)}<p class="music-scope">These are the two groups in this review. The other recordings remain in the archive while the Music page is being settled.</p></div>'''
    html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Music | GhostHeart</title><meta name="description" content="Listen to GhostHeart's Awakening and You're Not God."/>
<link rel="canonical" href="https://www.myghostheart.com/albums/"/>
<link rel="stylesheet" href="/assets/shared/release-site.css"/><link rel="stylesheet" href="/assets/shared/ghostheart-world.css"/>
<link rel="stylesheet" href="/assets/music/listening-room.css"/><script defer src="/assets/shared/ghostheart-world.js"></script>
</head><body class="ghx-site"><a class="skip-link" href="#main-content">Skip to content</a>{header}
<main id="main-content">{body}</main>{footer}</body></html>\n'''
    path = ROOT / 'albums/index.html'
    if check:
        if path.read_text(encoding='utf-8') != html:
            raise ValueError('Music output differs; rebuild required')
    else:
        path.write_text(html, encoding='utf-8', newline='\n')
    print('Music:', sum(bool(t['audio']) for g in groups for t in g['tracks']), 'playable audio tracks;', sum(bool(t['youtube']) for g in groups for t in g['tracks']), 'matching YouTube links')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
