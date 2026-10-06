#!/usr/bin/env python3
"""Build the Awakening pages. Draft bodies are read only for an external preview.

No deployment, scheduling, subscriber calls, or source-file writes occur here.
"""
import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / '.github/content/awakening.json'
ORDER = ["Cruel", "I'm Not", "Papa Didn't Raise a Fool", "She Got to Me",
         "This Is GhostHeart", "GhostHeart's Oath", "You Can Be GhostHeart Too",
         "One Heart Many Voices"]
SUNDAY = 'Sunday, October 11, 2026 at 10:00 a.m. Central. Viewing link and platform to be confirmed.'
STATES = {'draft', 'unwritten', 'preserved_unapproved', 'approved'}


def validate(data):
    sections = data['sections']
    if [s['title'] for s in sections] != ORDER:
        raise ValueError('Campaign must contain the exact eight-song order')
    if [s['number'] for s in sections] != list(range(1, 9)):
        raise ValueError('Campaign section numbers must be 1–8')
    if data['sunday'] != dict(text=SUNDAY, platform=None, url=None, time='10:00', first_date='2026-10-11'):
        raise ValueError('Sunday time is confirmed; platform and viewing link are pending')
    routes = []
    for s in sections:
        if s['status'] not in STATES or not isinstance(s['ready'], bool):
            raise ValueError('Invalid approval state')
        if not re.fullmatch(r'/awakening/[a-z0-9-]+\.html', s['route']):
            raise ValueError('Invalid section route')
        routes.append(s['route'])
        if s['ready'] and (s['status'] != 'approved' or not s['approval'] or not s['source_sha256']):
            raise ValueError('Ready requires explicit approval and an exact source hash')
        if s['status'] == 'unwritten' and (s['source_key'] or s['source_sha256']):
            raise ValueError('Unwritten section cannot contain a manuscript')
        # Media must go through a separate source/approval review before integration.
        if any(v is not None for v in s['media'].values()):
            raise ValueError('Campaign media has not been verified for this implementation')
    if len(set(routes)) != 8:
        raise ValueError('Duplicate section routes')
    if sections[0]['source_key'] != 'cruel' or sections[3]['source_key'] != 'wife':
        raise ValueError('Cruel and the preserved wife source must stay in sections 1 and 4')
    return sections


def public_sections(sections):
    """Release only a contiguous approved opening; section four cannot jump Cruel."""
    ready = []
    for s in sections:
        if s['status'] != 'approved' or not s['ready'] or not s['approval']:
            break
        ready.append(s)
    return ready


def manuscript(section, source_map):
    if section['source_key'] is None:
        return ''
    source = source_map[section['source_key']]
    raw = Path(source['path']).read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != section['source_sha256'] or digest != source['sha256']:
        raise ValueError(f"Source changed: {section['title']}; review the new version first")
    # These supplied Markdown sources contain plain paragraphs, headings, and one
    # internal-status paragraph. Escape prose; never evaluate embedded HTML.
    blocks = re.split(r'\n\s*\n', raw.decode('utf-8-sig').replace('\r\n', '\n').strip())
    prose = [b for b in blocks if not b.startswith('#') and not b.startswith('**INTERNAL STATUS:')]
    return ''.join(f'<p>{escape(b)}</p>\n' for b in prose)


def absolute_shell(text):
    text = re.sub(r' aria-current="[^"]*"', '', text)
    text = re.sub(r'href="#([^"]+)"', r'href="/index.html#\1"', text)
    return re.sub(r'(href|src)="(?!https?:|/|#)([^"]+)"', r'\1="/\2"', text)


def shell(title, body, route, preview=False):
    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    header = absolute_shell(re.search(r'<header\b.*?</header>', home, re.S).group())
    footer = absolute_shell(re.search(r'<footer\b.*?</footer>', home, re.S).group())
    current = 'page' if route == '/awakening/' else 'location'
    header = header.replace('href="/awakening/index.html"', f'aria-current="{current}" href="/awakening/"')
    robots = '<meta name="robots" content="noindex,nofollow"/>' if preview else ''
    canonical = '' if preview else f'<link rel="canonical" href="https://www.myghostheart.com{route}"/>'
    banner = '<aside class="campaign-review" aria-label="Review status">Private local review · Drafts and unwritten sections · Not approved for publication</aside>' if preview else ''
    styles = ['shared/release-site', 'shared/ghostheart-world', 'shared/ghostheart-awakening', 'story/reading-page', 'story/awakening-campaign']
    links = ''.join(f'<link rel="stylesheet" href="/assets/{s}.css"/>' for s in styles)
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{escape(title)} | GhostHeart</title><meta name="description" content="The Awakening. Eight songs, beginning with Cruel. How We Got Here."/>
{robots}{canonical}{links}
<script defer src="/assets/shared/release-site.js"></script><script defer src="/assets/shared/ghostheart-world.js"></script>
</head><body class="release-site ghx-site campaign-site"><a class="skip-link" href="#main-content">Skip to content</a>
{header}{banner}<main id="main-content">{body}</main>{footer}</body></html>\n'''


def sunday():
    return f'<aside class="sunday-note" aria-labelledby="sunday-readings"><h2 class="ghx-kicker" id="sunday-readings">Sunday readings</h2><p>{SUNDAY}</p></aside>'


def signup():
    # Reuse the existing integration, field names, honeypot, and confirmation note.
    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    section = re.search(r'<section\b[^>]*id="join-the-signal".*?</section>', home, re.S).group()
    return absolute_shell(section)


def landing(sections, visible, preview):
    allowed = {s['number'] for s in visible}
    rows = []
    for s in sections:
        available = preview or s['number'] in allowed
        title = escape(s['title'])
        link = f'<a href="{s["route"]}">{title}<span aria-hidden="true"> →</span></a>' if available else f'<span>{title}</span>'
        state = s['status'].replace('_', ' ') if preview else ('Read the story' if available else 'Story coming soon')
        rows.append(f'<li><span class="campaign-number" aria-hidden="true">{s["number"]:02d}</span><div><h3>{link}</h3><p>{escape(state)}</p></div></li>')
    first = sections[0]
    begin = f'<a class="primary" href="{first["route"]}">{"Review Cruel draft" if preview else "Begin with Cruel"} →</a>' if preview or visible else '<p class="campaign-coming">Cruel · Story coming soon</p>'
    return f'''<header class="reading-hero"><div class="ghx-wrap"><p class="ghx-kicker">Part 1 · Eight-song campaign</p><h1>The Awakening</h1><p class="campaign-subtitle">How We Got Here</p><div class="ghx-actions">{begin}<a class="secondary" href="#campaign-order">The eight songs ↓</a></div></div></header>
<div class="reading-shell"><div class="campaign-overview"><section aria-labelledby="campaign-order"><h2 id="campaign-order">The Awakening · In order</h2><ol class="campaign-order">{''.join(rows)}</ol></section>{sunday()}</div></div>{signup()}'''


def section_body(section, visible, source_map, preview):
    body = manuscript(section, source_map)
    status = ''
    if preview:
        notes = {'draft': 'New prose draft — review truth, voice and privacy before approval. Adapted from lyrics; not a transcript or verified report.',
                 'preserved_unapproved': 'Preserved source — campaign section 04. The original Reading 01 label is unchanged in its source file. Adapted from the supplied brief; not a verbatim conversation. Publication approval is pending.',
                 'unwritten': 'Unwritten — no manuscript supplied or invented. Source-grounded prose and approval are still needed.',
                 'approved': 'Approved manuscript — local review only; no deployment receipt is implied.'}
        status = f'<p class="campaign-status">{notes[section["status"]]}</p>'
    pos = visible.index(section)
    neighbors = []
    for offset, label, rel in [(-1, 'Previous', 'prev'), (1, 'Next', 'next')]:
        idx = pos + offset
        if 0 <= idx < len(visible):
            target = visible[idx]
            neighbors.append(f'<a rel="{rel}" href="{target["route"]}"><span>{label} · {target["number"]:02d}</span>{escape(target["title"])}</a>')
    return f'''<header class="reading-hero"><div class="ghx-wrap"><p class="ghx-kicker">The Awakening · Section {section['number']:02d} of 08 · {escape(section['title'])}</p><h1>How We Got Here</h1>{status}</div></header>
<div class="reading-shell"><div class="reading-layout"><article class="reading-prose" aria-label="{escape(section['title'], quote=True)}">{body or '<p>No manuscript yet.</p>'}</article>{sunday()}</div>
<nav class="campaign-pagination" aria-label="Campaign reading order">{''.join(neighbors)}</nav><div class="reading-back"><a href="/awakening/">← All eight campaign sections</a></div></div>'''


def public_alias(title, destination, description):
    """Keep a legacy address usable without publishing an unapproved campaign page."""
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{escape(title)} | GhostHeart</title><meta name="description" content="{escape(description, quote=True)}"/>
<link rel="canonical" href="https://www.myghostheart.com{destination}"/>
<meta http-equiv="refresh" content="0; url={destination}"/></head>
<body><main><h1>{escape(title)}</h1><p><a href="{destination}">Read the page</a>.</p></main></body></html>
'''


def build(output, data, source_map=None, preview=False, check=False):
    output = output.resolve()
    if preview and (output == ROOT or ROOT in output.parents or output in ROOT.parents):
        raise ValueError('Private previews must be outside the website checkout')
    sections = validate(data)
    visible = sections if preview else public_sections(sections)
    pages = {'awakening/index.html': (shell('The Awakening', landing(sections, visible, preview), '/awakening/', preview)
             if preview else public_alias('The Awakening', '/GhostHeart_Story.html', 'Read the GhostHeart story.'))}
    for section in visible:
        pages[section['route'].lstrip('/')] = shell(f"{section['title']} — How We Got Here", section_body(section, visible, source_map or {}, preview), section['route'], preview)
    if not preview:
        pages['story/how-we-got-here.html'] = public_alias('How We Got Here', '/journal/how-we-got-here-archive.html', 'Read the earlier public introduction in the Blog archive.')
        for section in sections:
            rel = section['route'].lstrip('/')
            if rel not in pages and (output / rel).exists():
                raise ValueError(f'Stale non-approved article exists: {rel}; preserve and review before publishing')
    for rel, content in pages.items():
        path = output / rel
        if check:
            if not path.exists() or path.read_bytes() != content.encode('utf-8'):
                raise ValueError(f'Generated page differs: {rel}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8', newline='\n')
    return list(pages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview-dir', type=Path, help='External private output; never the website root')
    parser.add_argument('--sources', type=Path, help='Private source-map JSON kept outside this repository')
    parser.add_argument('--check', action='store_true', help='Check generated output without changing files')
    args = parser.parse_args()
    sources = json.loads(args.sources.read_text(encoding='utf-8')) if args.sources else {}
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    paths = build(args.preview_dir or ROOT, data, sources, bool(args.preview_dir), args.check)
    print(json.dumps({'mode': 'private-preview' if args.preview_dir else 'public-candidate', 'pages': paths, 'deployed': False}, indent=2))


if __name__ == '__main__':
    main()
