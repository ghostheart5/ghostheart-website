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
archive = page("journal/how-we-got-here-archive.html")
awakening = page("awakening/index.html")
blog = page("journal/index.html")
films = page("GhostHeart_Videos.html")
start = page("start/index.html")
follow = page("follow/index.html")

assert story.select_one("h1").get_text(" ", strip=True) == "Enter My World."
assert story.select_one("#behind-the-scars h2").get_text(" ", strip=True) == "Behind the Scars — Before the Heart Wakes"  # renamed 2026-11-01 (owner)
assert story.select_one('a[href="/GhostHeart_Resources.html"]')
assert love.select_one("h1").get_text(" ", strip=True) == "The Woman Behind the Scenes."
assert love.select_one('a[href="/music/#song-she-got-to-me"]')
for relative, fragment in [('journal/this-is-ghostheart.html', 'song-this-is-ghostheart'), ('journal/ghosthearts-oath.html', 'song-ghosthearts-oath')]:
    assert page(relative).select_one(f'a[href="/music/#{fragment}"]').get_text() == 'Listen to the song'
assert "GhostHeart and His Angel" not in story.get_text(" ", strip=True)
assert "GhostHeart and His Angel" not in love.get_text(" ", strip=True)
assert alias.select_one('meta[http-equiv="refresh"]')["content"].endswith("/woman-behind-the-scenes/")
assert love_alias.select_one('meta[http-equiv="refresh"]')["content"].endswith("/woman-behind-the-scenes/")
assert "Survival matters" in archive.get_text(" ", strip=True)
assert awakening.select_one("h1").get_text(" ", strip=True) == "Before the Heart Wakes."
assert page("journal/how-we-got-here.html").select_one('meta[http-equiv="refresh"]')["content"].endswith("/GhostHeart_Story.html")
# A fragment must identify a visible player card, not only a compatibility span.
expected_films = {
    'film-this-is-ghostheart': 'AOCRvtz92JM',
    'film-ghosthearts-oath': 'mBAsUNX3vHQ',
    'film-i-wont-pretend-to-speak-for-you': 'z-FRCpG9vfw',
    'film-hey-preacher-man': '2SEng4dmgUc',
    'film-that-aint-holy': 'ptYn4vh6DCQ',
    'film-the-dad': 'cBNxq4y1ahU',
    'film-human-too-remake': 'ARCFOZSOC_o',
    'film-the-man-beneath-the-moon': '_mUU-toMlM8',
    'film-rebellion': 'FaT_Ibrs9Y0',
    'film-just-not-this-morning': 'XWmMYqkvdzg',
    'film-look-at-me': 'nVC1kB0MREA',
    'film-cruel': '9sbFgjM_SDE',
}
# Wake the Heart site (Dom, Nov 6 2026): every film card keeps its old address and its YouTube link.
actual_films = {card['id']: card for card in films.select('article.film[id]')}
assert set(actual_films) == set(expected_films), set(actual_films)
for card_id, video_id in expected_films.items():
    card = actual_films[card_id]
    assert not card.has_attr('hidden') and card.select_one('h3'), card_id
    assert card.select_one(f'a[href="https://www.youtube.com/watch?v={video_id}"]'), card_id
    assert (ROOT / card.select_one('img')['src'].lstrip('/')).is_file(), card_id
assert 'cinematic remake' in actual_films['film-human-too-remake'].get_text(' ', strip=True)
assert 'Human After All' in actual_films['film-human-too-remake'].get_text(' ', strip=True)  # owner 2026-11-01: plain label, no YouTube title
assert 'Broken Man' in actual_films['film-the-man-beneath-the-moon'].get_text(' ', strip=True)  # owner 2026-11-01: no upload notes shown
recordings = page('GhostHeart_Songs.html')
# Owner 2026-11-02 ("fix the bigger jobs now"): the 11 previews live only on Music. The Songs page keeps the
# Released recordings archive; old #song-audio-track-* links forward to the same song on Music.
assert not recordings.select('#existing-audio, li.music-track')
assert recordings.select_one('script[data-song-forward]')
for link in recordings.select('.record-card a[href*="GhostHeart_Videos.html#"]'):
    fragment = urlsplit(link['href']).fragment
    assert fragment in actual_films, (link, 'Recording action targets a hidden or absent film')
assert recordings.select_one('#song-the-dad .record-actions a[href="https://www.youtube.com/watch?v=cBNxq4y1ahU"]')
for record_id, film_id in [('human-too', 'film-human-too-remake'), ('song-the-man-beneath-the-moon', 'film-the-man-beneath-the-moon'), ('song-rebellion', 'film-rebellion')]:
    assert recordings.select_one(f'#{record_id} .record-actions a[href="/GhostHeart_Videos.html#{film_id}"]')
ashes = recordings.select_one('#song-just-not-this-morning')
assert not ashes.select_one('a[href*="#film-hey-preacher-man"]')
assert 'all five' not in str(ashes).lower()
assert {urlsplit(link['href']).fragment for link in ashes.select('.record-actions a[href*="GhostHeart_Videos.html#"]')} == {'film-just-not-this-morning', 'film-look-at-me'}
assert [parse_qs(urlsplit(link['href']).query)['v'][0] for link in ashes.select('.gh-track-list li a')] == ['9pI_nXdjTR4', 'kYOkJn-AlyI', '1uThHaD_HaA', 'C-v0URkntUQ', 'xR6egEJgTv4']
assert 'original 3:55 version' in recordings.select_one('#song-rebellion').get_text(' ', strip=True)
assert 'new 5:30 version' in recordings.select_one('#song-you-cant-change-us-20260906').get_text(' ', strip=True)
assert 're-released or merged' not in recordings.get_text(' ', strip=True)
assert 'reuse the same public preview' not in recordings.get_text(' ', strip=True)
assert recordings.select_one('#released-recordings h2').get_text(' ', strip=True) == 'Released recordings archive'
assert recordings.select_one('.music-jump a[href="/music/"]').get_text() == 'Music: the 11 song previews'
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
for slug in ['broken-man', 'fatherhood', 'human-after-all', 'love-is-love', 'the-ones-we-carry', 'youre-not-god']:
    collection = page(f'albums/{slug}/index.html')
    prose = collection.select_one('#about .l-prose').get_text(' ', strip=True).lower()
    assert not any(phrase in prose for phrase in ['is an album', 'this album']), slug
# Owner 2026-11-02: Music (/music/) is the one home for the 11 songs; /albums/ only forwards there.
music = page('music/index.html')
assert page('albums/index.html').select_one('meta[http-equiv="refresh"]')['content'] == '0; url=/music/'
for relative in ['journal/this-is-ghostheart.html', 'journal/ghosthearts-oath.html']:
    assert 'Short song introduction' in page(relative).select_one('.journal-meta').get_text(' ', strip=True)
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
print("PASS World review: story, film and song addresses, recordings archive, reading aliases, shared theme on older pages")
