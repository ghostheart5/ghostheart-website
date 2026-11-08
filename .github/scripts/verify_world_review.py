#!/usr/bin/env python3
"""Check the local World/Vault review draft after a full site build."""

from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import json
import re

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]


def page(relative):
    return BeautifulSoup((ROOT / relative).read_text(encoding="utf-8"), "html.parser")


home = page("index.html")
story = page("GhostHeart_Story.html")
love = page("woman-behind-the-scenes/index.html")
love_alias = page("love-behind-the-scenes/index.html")
alias = page("GhostHeart_Angel.html")
vault = page("vault/index.html")
awakening = page("awakening/index.html")
blog = page("journal/index.html")
films = page("GhostHeart_Videos.html")
start = page("start/index.html")
follow = page("follow/index.html")

assert story.select_one("h1").get_text(" ", strip=True) == "Enter My World."
assert story.select_one("#behind-the-scars h2").get_text(" ", strip=True) == "Behind the Scars"  # retired name dropped 2026-11-08 (owner: older songs off everywhere)
assert story.select_one('a[href="/GhostHeart_Resources.html"]')
assert love.select_one("h1").get_text(" ", strip=True) == "The Woman Behind the Scenes."
assert love.select_one('a[href="/music/"]')
# Dom, Nov 8 2026: older songs are off the site; their song notes forward to the Blog (apply_week1_songs_only.py).
for relative in ('journal/this-is-ghostheart.html', 'journal/ghosthearts-oath.html', 'journal/how-we-got-here-archive.html'):
    assert page(relative).select_one('meta[http-equiv="refresh"]')['content'] == '0; url=/journal/', relative
assert "GhostHeart and His Angel" not in story.get_text(" ", strip=True)
assert "GhostHeart and His Angel" not in love.get_text(" ", strip=True)
assert alias.select_one('meta[http-equiv="refresh"]')["content"].endswith("/woman-behind-the-scenes/")
assert love_alias.select_one('meta[http-equiv="refresh"]')["content"].endswith("/woman-behind-the-scenes/")
# Dom, Nov 8 2026: The Awakening is retired; the old album page forwards to Music (apply_no_awakening.py).
assert awakening.select_one('meta[http-equiv="refresh"]')["content"] == "0; url=/music/"
assert page("journal/how-we-got-here.html").select_one('meta[http-equiv="refresh"]')["content"].endswith("/GhostHeart_Story.html")
# Dom, Nov 8 2026: older films are off the site; Films points to The Heart Wakes premiere (apply_week1_songs_only.py).
film_cards = films.select('article.film[id]')
assert [card['id'] for card in film_cards] == ['film-the-heart-wakes'], [card['id'] for card in film_cards]
assert film_cards[0].select_one('a[href="https://www.youtube.com/@GhostHeart-M95RTK"]')
recordings = page('GhostHeart_Songs.html')
assert recordings.select_one('meta[http-equiv="refresh"]')['content'] == '0; url=/music/'
assert recordings.select_one('#human-too')  # old deep links still land before the forward
assert not films.select("main form")
assert not page("GhostHeart_Quotes.html").select("main form")
# Start Here retired 2026-11-01 (Dom): it only repeated Home and Enter My World.
assert 'content="0; url=/"' in (ROOT / "start/index.html").read_text(encoding="utf-8")
# Wake the Heart site: every Silver Thread email box posts to the approved Mailchimp list (test_wake_v3.py).
assert home.select("form") and all("list-manage.com/subscribe/post" in f["action"] for f in home.select("form"))
assert 'You?ll' not in follow.get_text()
assert 'approved' not in follow.select_one('meta[name="description"]')['content']
for relative, canonical in [('woman-behind-the-scenes/index.html', '/woman-behind-the-scenes/')]:
    document = page(relative)
    assert document.select_one('meta[property="og:url"]')['content'] == document.select_one('link[rel="canonical"]')['href'] == 'https://www.myghostheart.com' + canonical
    for property_name in ['og:title', 'og:description', 'og:image']:
        assert len(document.select(f'meta[property="{property_name}"]')) == 1
    image_url = document.select_one('meta[property="og:image"]')['content']
    # Audit Nov 6, 2026 (WEB-06): 1200x630 share JPGs instead of 2.5-4.4 MB PNGs (apply_audit_nov6.py).
    expected_image = 'ghostheart-rebel-share-1200x630.jpg' if relative == 'woman-behind-the-scenes/index.html' else 'ghostheart-awakening-share-1200x630.jpg'
    assert image_url == 'https://www.myghostheart.com/assets/story/' + expected_image
    assert (ROOT / image_url.removeprefix('https://www.myghostheart.com/')).is_file()
    assert document.select_one('meta[name="twitter:card"]')['content'] == 'summary_large_image'
assert love.select_one('meta[property="og:image:alt"]')['content'] == love.select_one('.world-approved-art img')['alt']
assert love.select_one('meta[property="og:image:width"]')['content'] == '1200'
assert love.select_one('meta[property="og:image:height"]')['content'] == '630'
for card in films.select('.g-film[id]'):
    for link in card.select('.g-actions a[href^="/albums/"]'):
        assert 'Explore the album' not in link.get_text(), (card['id'], link)
library = json.loads((ROOT / '.github/content/site-library.json').read_text(encoding='utf-8'))
collection_paths = {f'/albums/{slug}/index.html' for slug in library['collections']}
catalog_text = (ROOT / 'assets/data/ghostheart-video-catalog.js').read_text(encoding='utf-8')
catalog = json.loads(re.search(r'Object\.freeze\((\[.*\])\);', catalog_text, re.S).group(1))
for film in catalog:
    for link in [film.get('song', {})] + film.get('related', []):
        if '/' + urlsplit(link.get('href', '')).path.lstrip('/') in collection_paths:
            assert link.get('label') not in {'Explore the album', 'GhostHeart album'}, film['key']
            assert not link.get('accessibleLabel', '').startswith('Explore the album '), film['key']
# Dom, Nov 8 2026: the old album pages forward to Music (apply_week1_songs_only.py).
for slug in ['broken-man', 'fatherhood', 'human-after-all', 'love-is-love', 'the-ones-we-carry', 'youre-not-god', 'ghostheart', 'ghosthearts-angel', 'uplifting']:
    assert page(f'albums/{slug}/index.html').select_one('meta[http-equiv="refresh"]')['content'] == '0; url=/music/', slug
# Owner 2026-11-02: Music (/music/) is the one home for the 11 songs; /albums/ only forwards there.
music = page('music/index.html')
assert page('albums/index.html').select_one('meta[http-equiv="refresh"]')['content'] == '0; url=/music/'
ids = [element['id'] for element in music.select('[id]')]
assert len(ids) == len(set(ids)), 'Duplicate Music IDs'
live_source = json.loads((ROOT / '.github/content/live.json').read_text(encoding='utf-8'))
assert live_source['public_enabled'] is False and live_source['public_path_enabled'] is True
assert live_source['starts_at'] == '2026-10-11T10:00:00-05:00'
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts or '.github' in path.parts:
        continue
    document = page(path.relative_to(ROOT))
    # Shared navigation has one Vault destination; quote deep links in content remain valid.
    for navigation in document.select('header, footer'):
        vault_links = navigation.select('a[href="/vault/"]')
        if vault_links:
            assert not navigation.select('a[href="/GhostHeart_Quotes.html"]'), (path, 'duplicate Vault navigation')
            if navigation.name == 'footer':
                assert len(vault_links) == 1, (path, 'duplicate Vault footer')
    for link in document.select('a[href]'):
        target = link['href'].replace('../', '').lstrip('/')
        assert not any(label in link.get_text(' ', strip=True) for label in ['GhostHeart and His Angel', 'Meet the Angel']), (path, link)
    text = document.get_text(' ', strip=True)
    assert 'The Awakening Begins' not in text, path
    if path.relative_to(ROOT).as_posix() != 'live/index.html':  # Dom, Nov 6 2026: Lives shows the next Sunday Live
        assert 'Next Sunday Live' not in text, path
    assert 'Sunday readings will connect' not in text, path
assert home.select_one('a[href="/GhostHeart_Resources.html"]')
assert "Join the Signal" not in home.get_text(" ", strip=True)
for relative in ("woman-behind-the-scenes/index.html",):
    document = page(relative)
    assert document.select_one('link[href="/assets/shared/review-theme.css"]') or document.select_one('link[href="/assets/loud/loud.css"]'), relative
print("PASS World review: story, Films with only The Heart Wakes, older song pages forwarded, reading aliases, shared theme on older pages")
