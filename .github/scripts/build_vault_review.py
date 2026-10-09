#!/usr/bin/env python3
"""Build the local review Vault from the site's already public catalogs."""

from html import escape
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]


def replace_unverified_signup(soup):
    """Keep a social connection path while email delivery remains unverified."""
    replacement = '''<section class="g-section" id="join-the-signal"><div class="g-wrap"><h2>Stay Connected.</h2>
<p>Find new work on GhostHeart's verified public profiles. Email updates are available on the <a href="/follow/">Stay Connected page</a>.</p>
<div class="ghx-actions"><a href="https://www.youtube.com/@GhostHeart-M95RTK" target="_blank" rel="noopener noreferrer">YouTube</a>
<a href="https://www.tiktok.com/@ghosthearted1" target="_blank" rel="noopener noreferrer">TikTok</a>
<a href="https://www.instagram.com/ghostheart131517/" target="_blank" rel="noopener noreferrer">Instagram</a></div></div></section>'''
    for section in soup.select('main section.g-follow'):
        section.replace_with(BeautifulSoup(replacement, 'html.parser'))
    for form in soup.select('main form'):
        form.decompose()
    return soup


def shell_piece(value):
    value = re.sub(r' aria-current="[^"]*"', '', value)
    value = re.sub(r'href="#([^"]+)"', r'href="/index.html#\1"', value)
    return re.sub(r'(href|src)="(?!https?:|/|#)([^"]+)"', r'\1="/\2"', value)


home_path = ROOT / 'index.html'
home = home_path.read_text(encoding='utf-8')
header = shell_piece(re.search(r'<header\b.*?</header>', home, re.S).group())
header = header.replace('href="/vault/"', 'aria-current="page" href="/vault/"', 1)
footer = shell_piece(re.search(r'<footer\b.*?</footer>', home, re.S).group())
manifest = json.loads((ROOT / '.github/content/music.json').read_text(encoding='utf-8'))
library = json.loads((ROOT / '.github/content/site-library.json').read_text(encoding='utf-8'))
live = json.loads((ROOT / '.github/content/live.json').read_text(encoding='utf-8'))

items = []
for group in manifest['groups']:
    for track in group['tracks']:
        title = track['title']
        items.append(dict(kind='songs', title=title, description=f"From {group['title']}.",
                          href=f"/albums/#{group['id']}", action='Listen in Music',
                          search=f"{title} {group['title']}", featured=title == 'Cruel'))

films = replace_unverified_signup(BeautifulSoup((ROOT / 'GhostHeart_Videos.html').read_text(encoding='utf-8'), 'html.parser'))
approved_video_ids = {
    'AOCRvtz92JM',  # This Is GhostHeart / Awakening
    'mBAsUNX3vHQ',  # GhostHeart's Oath / Awakening
    'z-FRCpG9vfw',  # I Won't Pretend to Speak for You / You're Not God
    '2SEng4dmgUc',  # Hey Preacher Man / You're Not God
    'ptYn4vh6DCQ',  # That Ain't Holy / You're Not God
}
public_video_ids = set()
for card in films.select('.g-film[id]'):
    direct = card.select_one('a[href^="https://www.youtube.com/watch?v="]')
    player = card.select_one('[data-video-id]')
    title = card.select_one('h3')
    if not (direct and player and title):
        continue
    video_id = parse_qs(urlsplit(direct['href']).query).get('v', [''])[0]
    assert video_id and video_id == player['data-video-id']
    assert video_id not in public_video_ids
    public_video_ids.add(video_id)
    if video_id not in approved_video_ids:
        # Keep old fragment URLs resolvable without placing unreviewed media
        # into the audience-facing collection.
        card.replace_with(BeautifulSoup(f'<span id="{card["id"]}" hidden></span>', 'html.parser'))
        continue
    description = card.select_one('h3 + p')
    title_text = title.get_text(' ', strip=True)
    desc_text = description.get_text(' ', strip=True) if description else ''
    items.append(dict(kind='videos', title=title_text, description=desc_text,
                      href=f"/GhostHeart_Videos.html#{card['id']}", action='Watch the film',
                      search=f"{title_text} {desc_text}", featured=video_id == 'AOCRvtz92JM'))
assert approved_video_ids <= public_video_ids and len(public_video_ids) == 23
film_intro = films.select_one('main .g-lead')
if film_intro:
    film_intro.string = "Only films tied clearly to The Awakening and You're Not God are in this review selection. Players load when you choose."
(ROOT / 'GhostHeart_Videos.html').write_text(str(films), encoding='utf-8', newline='\n')
quotes_path = ROOT / 'GhostHeart_Quotes.html'
quotes_page = replace_unverified_signup(BeautifulSoup(quotes_path.read_text(encoding='utf-8'), 'html.parser'))
quotes_path.write_text(str(quotes_page), encoding='utf-8', newline='\n')

# Public links verified in the owner's authorized YouTube audit on 2026-10-06.
# This is an initial catalog, with a complete backfill still to review.
public_shorts = [
    ('Cruel', '2fq-XQxtFuo'),
    ("Mercy That Leaves an Empty Seat", 'ofU09J3bkHI'),
    ('Would You Leave the Porch Light On?', '5HUWedEnnsA'),
    ('A Child Should Never Have to Earn Love', 'bkm3czEmk5g'),
    ('Son, You Did No Wrong', '5b43JyYmIts'),
]
assert len({video_id for _, video_id in public_shorts}) == 5
for title, video_id in public_shorts:
    awakening = title == 'Cruel'
    items.append(dict(kind='shorts', title=title,
                      description='From The Awakening.' if awakening else "From That Ain't Holy / You're Not God.",
                      href=f'https://www.youtube.com/shorts/{video_id}', action='Watch the Short',
                      search=title + (" Awakening" if awakening else " That Ain't Holy You're Not God"),
                      related_href='/albums/index.html#awakening' if awakening else '/albums/index.html#youre-not-god',
                      featured=False))

for index, quote in enumerate(library['quotes'], 1):
    items.append(dict(kind='quotes', title=f"Quote {index:02}", description=quote,
                      href=f"/GhostHeart_Quotes.html#quote-{index:02}", action='View in Quote Vault',
                      search=quote, featured=index == 1))
assert len(library['quotes']) == 17 and len(items) == 38


def card(item):
    kind = item['kind']
    title = escape(item['title'])
    description = escape(item['description'])
    search = escape(item['search'].lower(), quote=True)
    hidden = '' if item['featured'] else ' hidden'
    inner = f'<blockquote>{description}</blockquote>' if kind == 'quotes' else f'<p>{description}</p>'
    related = (f'<a href="{item["related_href"]}">Listen to the song</a>' if item.get('related_href') else '')
    return (f'<article class="vault-item" data-vault-kind="{kind}" data-vault-featured="{str(item["featured"]).lower()}" '
            f'data-vault-search="{search}"{hidden}><span class="vault-type">{kind[:-1].title()}</span>'
            f'<h2>{title}</h2>{inner}<a href="{escape(item["href"], quote=True)}">{escape(item["action"])}</a>{related}</article>')

cards = '\n'.join(card(item) for item in items)
page = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>GhostHeart’s Vault | GhostHeart</title><meta name="description" content="Explore GhostHeart songs, films, and quotes already shared with the public."/>
<link rel="canonical" href="https://www.myghostheart.com/vault/"/><link rel="icon" href="/favicon.ico"/>
<link rel="stylesheet" href="/assets/shared/release-site.css"/><link rel="stylesheet" href="/assets/shared/ghostheart-world.css"/><link rel="stylesheet" href="/assets/vault/vault.css"/>
<script defer src="/assets/shared/ghostheart-world.js"></script><script defer src="/assets/vault/vault.js"></script>
<meta property="og:type" content="website"/><meta property="og:site_name" content="GhostHeart"/><meta property="og:title" content="GhostHeart’s Vault"/><meta property="og:url" content="https://www.myghostheart.com/vault/"/>
</head><body class="ghx-site"><a class="skip-link" href="#main-content">Skip to content</a>{header}
<main id="main-content" class="vault-page"><section class="vault-hero ghx-wrap"><p class="ghx-kicker">A growing collection</p><h1>GhostHeart’s Vault.</h1><p>Songs, films, and words already shared. Start with a few, or find what speaks to you.</p>
<div class="vault-hero-links"><a href="/GhostHeart_Story.html">Enter My World</a><a href="/GhostHeart_Resources.html">Help &amp; Resources</a></div></section>
<section class="vault-library ghx-wrap" aria-label="Explore the Vault"><div class="vault-controls"><label for="vault-search">Find a title or theme</label><div class="vault-search-row"><input id="vault-search" type="search" placeholder="Search the Vault" autocomplete="off"/><button id="vault-clear" type="button">Clear</button></div></div>
<div class="vault-filters" aria-label="Filter the Vault"><button type="button" data-vault-filter="featured" aria-pressed="true">Featured</button><button type="button" data-vault-filter="songs" aria-pressed="false">Songs</button><button type="button" data-vault-filter="videos" aria-pressed="false">Videos</button><button type="button" data-vault-filter="shorts" aria-pressed="false">Shorts</button><button type="button" data-vault-filter="quotes" aria-pressed="false">Quotes</button><button type="button" data-vault-filter="all" aria-pressed="false">All</button></div>
<p id="vault-count" class="vault-count" role="status" aria-live="polite">3 featured selections shown.</p>
<div class="vault-grid">{cards}</div><p id="vault-empty" class="vault-empty" hidden>No matches. Try another title or theme.</p>
<p class="vault-source-note">Songs open Music, films open the existing film collection, Shorts open their public YouTube pages, and quotes open the Quote Vault. Only The Awakening and You’re Not God songs, films, and Shorts are shown while other media are reviewed. No downloads are offered here.</p>
<noscript><p><a href="/albums/">Music</a> · <a href="/GhostHeart_Videos.html">Films</a> · <a href="/GhostHeart_Quotes.html">Quote Vault</a></p></noscript></section></main>{footer}</body></html>\n'''
output = ROOT / 'vault/index.html'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(page, encoding='utf-8', newline='\n')

home_latest = f'''<section class="vault-latest ghx-wrap" aria-labelledby="latest-title" id="latest"><div class="vault-latest-head"><p class="ghx-kicker">From GhostHeart</p><h2 id="latest-title">A story. A song. A line.</h2><p>Start with what speaks to you; the selections here are curated by hand.</p></div><div class="vault-latest-grid">
<article><span>Start reading</span><h3>Behind the Scars</h3><p>The public beginning of the life behind GhostHeart.</p><a href="/GhostHeart_Story.html#behind-the-scars">Enter My World</a></article>
<article><span>Featured song</span><h3>Cruel</h3><p>From the approved GhostHeart’s Awakening listening sequence.</p><a href="/albums/index.html#awakening">Listen in Music</a></article>
<article><span>Today’s quote</span><blockquote data-daily-quote>{escape(library['quotes'][0])}</blockquote><a href="/GhostHeart_Quotes.html">Explore the Quote Vault</a></article>
<article><span>Featured film</span><h3>This Is GhostHeart</h3><p>The name, the scars, and the reason a hidden heart chose to be seen.</p><a href="/GhostHeart_Videos.html#film-this-is-ghostheart">Watch the film</a></article>
</div><div class="vault-latest-next"><a href="/journal/">Read the Blog</a><a href="/GhostHeart_Resources.html">Help &amp; Resources</a></div></section>'''
home_paths = f'''<section class="home-discovery ghx-wrap" aria-label="Explore Vault and Lives">
<article class="home-discovery-card" id="home-vault" aria-labelledby="home-vault-title"><p class="ghx-kicker">The approved collection</p><h2 id="home-vault-title">GhostHeart's Vault</h2>
<p>Find a song, film, Short, or quote that stays with you. Music and moving images here are limited to The Awakening and You're Not God while other work is reviewed.</p>
<p class="home-discovery-meta">11 songs · 5 films · 5 Shorts · 17 quotes</p><a href="/vault/">Explore GhostHeart's Vault</a></article>
<article class="home-discovery-card" id="home-lives" aria-labelledby="home-lives-title"><p class="ghx-kicker">Planned Sunday Live</p><h2 id="home-lives-title">Lives &amp; Readings</h2>
<p><strong>{escape(live['title'])}</strong> is planned for <time datetime="{escape(live['starts_at'], quote=True)}">October 11, 2026 at 10:00 a.m. Central</time>. The platform, viewing link, and replay are pending.</p>
<a href="/live/">Lives &amp; Readings details</a></article></section>'''
assert 'id="latest"' not in home
assert home.count('<section class="signup-section"') == 1
home = home.replace('<section class="signup-section"', home_paths + '\n' + home_latest + '\n<section class="signup-section"', 1)
home = home.replace('<script defer src="assets/shared/ghostheart-world.js"></script>', '<script defer src="assets/shared/ghostheart-world.js"></script>\n<script defer src="assets/journal/daily-quote.js"></script>\n<link rel="stylesheet" href="assets/vault/vault.css"/>', 1)
home_path.write_text(home, encoding='utf-8', newline='\n')

# Keep the new public reading and collection discoverable if this review is
# later approved. The old relationship URL remains a noindex compatibility alias.
sitemap_path = ROOT / 'sitemap.xml'
ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', ns)
site_map = ET.fromstring(sitemap_path.read_text(encoding='utf-8'))
targets = {
    'https://www.myghostheart.com/GhostHeart_Story.html',
    'https://www.myghostheart.com/GhostHeart_Angel.html',
    'https://www.myghostheart.com/love-behind-the-scenes/',
    'https://www.myghostheart.com/woman-behind-the-scenes/',
    'https://www.myghostheart.com/vault/',
}
for entry in list(site_map):
    loc = entry.find(f'{{{ns}}}loc')
    if loc is not None and loc.text in targets:
        site_map.remove(entry)
for url in sorted(targets - {'https://www.myghostheart.com/GhostHeart_Angel.html', 'https://www.myghostheart.com/love-behind-the-scenes/'}):
    entry = ET.SubElement(site_map, f'{{{ns}}}url')
    ET.SubElement(entry, f'{{{ns}}}loc').text = url
    ET.SubElement(entry, f'{{{ns}}}lastmod').text = '2026-10-06'
ET.indent(site_map, space='  ')
sitemap_path.write_text('<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(site_map, encoding='unicode') + '\n', encoding='utf-8', newline='\n')
print(f"Built scoped Vault from {len(items)} public links: 11 songs, 5 films, 5 verified Shorts, 17 quotes")
