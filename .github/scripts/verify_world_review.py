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
assert story.select_one("#behind-the-scars h2").get_text(" ", strip=True) == "Behind the Scars — The Awakening"
assert story.select_one('a[href="/woman-behind-the-scenes/"]')
assert story.select_one('a[href="/journal/"]')
assert story.select_one('a[href="/GhostHeart_Resources.html"]')
assert love.select_one("h1").get_text(" ", strip=True) == "The Woman Behind the Scenes."
assert love.select_one('a[href="/albums/#track-she-got-to-me"]')
for relative, fragment in [('journal/this-is-ghostheart.html', 'track-this-is-ghostheart'), ('journal/ghosthearts-oath.html', 'track-ghosthearts-oath')]:
    assert page(relative).select_one(f'a[href="/albums/#{fragment}"]').get_text() == 'Listen to the song'
assert "GhostHeart and His Angel" not in story.get_text(" ", strip=True)
assert "GhostHeart and His Angel" not in love.get_text(" ", strip=True)
assert alias.select_one('meta[http-equiv="refresh"]')["content"].endswith("/woman-behind-the-scenes/")
assert love_alias.select_one('meta[http-equiv="refresh"]')["content"].endswith("/woman-behind-the-scenes/")
assert "Survival matters" in archive.get_text(" ", strip=True)
assert awakening.select_one("h1").get_text(" ", strip=True) == "The Awakening."
# The Blog lists every public entry (the archived introduction has its own card) plus every released Passage page.
public_entries = [p for p in json.loads((ROOT / ".github/content/journal.json").read_text(encoding="utf-8"))
                  if p["slug"] != "how-we-got-here" and (ROOT / "journal" / f'{p["slug"]}.html').exists()]
released_passages = [f for f in (ROOT / "passages").glob("*.html") if f.name != "index.html"]
assert len(blog.select("#entries article")) == len(public_entries) + len(released_passages)
assert blog.select_one("a[href=\"/passages/im-not.html\"]") and blog.select_one("#long-story a[href^=\"https://toohumantostayquiet.substack.com/\"]")
assert blog.select_one('a[href="/journal/how-we-got-here-archive.html"]')
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
actual_films = {card['id']: card for card in films.select('.g-film[id]')}
assert set(actual_films) == set(expected_films), set(actual_films)
for card_id, video_id in expected_films.items():
    card = actual_films[card_id]
    assert card.name == 'article' and not card.has_attr('hidden'), card_id
    assert card.select_one('h3') and card.select_one(f'button[data-video-id="{video_id}"]'), card_id
    assert card.select_one(f'a[href="https://www.youtube.com/watch?v={video_id}"]'), card_id
    assert (ROOT / card.select_one('.g-player img')['src'].lstrip('/')).is_file(), card_id
retained_film_aliases = films.select('.g-films > span[id^=film-][hidden]')
assert len(retained_film_aliases) == 12
assert all(not alias.select('button, iframe, a') for alias in retained_film_aliases)
assert 'cinematic remake' in actual_films['film-human-too-remake'].get_text(' ', strip=True)
assert "Why You Should Never Judge Someone's Worst Day" in actual_films['film-human-too-remake'].get_text(' ', strip=True)
assert 'Fixed vocal ending' in actual_films['film-the-man-beneath-the-moon'].get_text(' ', strip=True)
recordings = page('GhostHeart_Songs.html')
# Preserve the public preview fragments as usable rows, not hidden aliases.
preview_tracks = [track for group in json.loads((ROOT / '.github/content/music.json').read_text(encoding='utf-8'))['groups']
                  for track in group['tracks'] if track.get('audio')]
assert len(preview_tracks) == 11
assert {row['id'] for row in recordings.select('#existing-audio li.music-track[id]')} == {
    'song-audio-' + track['id'] for track in preview_tracks
}, 'Published preview fragments changed'
for track in preview_tracks:
    row = recordings.select_one('#song-audio-' + track['id'] + '.music-track')
    assert row and row.name == 'li' and not row.has_attr('hidden'), track['id']
    assert not any(parent.has_attr('hidden') for parent in row.parents), track['id']
    assert row.select_one('h3').get_text() == track['title'], track['id']
    player = row.select_one('audio[controls][preload="none"]')
    assert player and player.select_one('source')['src'] == track['audio'], track['id']
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
assert recordings.select_one('.music-jump a[href="/albums/index.html"]').get_text() == 'Featured listening collections'
assert not films.select("main form")
assert not page("GhostHeart_Quotes.html").select("main form")
assert start.select_one('a[href="/albums/index.html#youre-not-god"]')
assert not start.select("form") and not home.select("form")
form = follow.select_one("form.signal-signup-form")
assert form and form.get("method") == "post" and "list-manage.com/subscribe/post" in form["action"]
assert form.select_one("input[name=EMAIL][required]") and form.select_one("input[name^=b_a7ab330423f3b936c48b8d8ba_]")
assert 'You?ll' not in follow.get_text()
assert 'approved' not in follow.select_one('meta[name="description"]')['content']
for relative, canonical in [('woman-behind-the-scenes/index.html', '/woman-behind-the-scenes/'), ('vault/index.html', '/vault/'), ('albums/index.html', '/albums/')]:
    document = page(relative)
    assert document.select_one('meta[property="og:url"]')['content'] == document.select_one('link[rel="canonical"]')['href'] == 'https://www.myghostheart.com' + canonical
    for property_name in ['og:title', 'og:description', 'og:image']:
        assert len(document.select(f'meta[property="{property_name}"]')) == 1
    image_url = document.select_one('meta[property="og:image"]')['content']
    expected_image = 'ghostheart-rebel-in-the-rain.png' if relative == 'woman-behind-the-scenes/index.html' else 'ghostheart-awakening-banner.png'
    assert image_url == 'https://www.myghostheart.com/assets/story/' + expected_image
    assert (ROOT / image_url.removeprefix('https://www.myghostheart.com/')).is_file()
    assert document.select_one('meta[name="twitter:card"]')['content'] == 'summary_large_image'
assert love.select_one('meta[property="og:image:alt"]')['content'] == love.select_one('.world-approved-art img')['alt']
assert love.select_one('meta[property="og:image:width"]')['content'] == '1374'
assert love.select_one('meta[property="og:image:height"]')['content'] == '1145'
live = page("live/index.html")
assert " ".join(live.select_one("#live-status-title").get_text().split()) == "Next Live: Sunday, November 1, 2026, 10:00 a.m. Central."
assert live.select_one("#live-status-title [data-live-until][data-live-after]")
assert live.select_one('a[href="/live/my-promise.html"]')
assert live.select_one('a[href="/follow/"]')
assert not live.select_one("#next-live-title")
assert not live.select_one("#live-replay")
assert not live.select_one('time')

counts = {kind: len(vault.select(f'.vault-item[data-vault-kind="{kind}"]'))
          for kind in ("songs", "videos", "shorts", "quotes")}
assert counts == {"songs": 11, "videos": 6, "shorts": 5, "quotes": 17}, counts
assert vault.select_one('.vault-hero .ghx-kicker').get_text() == 'A selected collection'
vault_films_link = vault.select_one('.vault-hero-links > a.vault-films-link[href="/GhostHeart_Videos.html"]')
assert vault_films_link and vault_films_link.get_text() == 'Browse Films'
assert not any(parent.name == 'noscript' or parent.has_attr('hidden') for parent in vault_films_link.parents)
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
music = page('albums/index.html')
assert music.select_one('a[href="/GhostHeart_Songs.html#released-recordings"]').get_text() == 'Released recordings archive'
assert music.select_one('a[href="/GhostHeart_Videos.html"]').get_text() == 'Films'
assert 'Featured listening collections' in music.select_one('.music-hero').get_text(' ', strip=True)
for relative in ['journal/this-is-ghostheart.html', 'journal/ghosthearts-oath.html']:
    assert 'Short song introduction' in page(relative).select_one('.journal-meta').get_text(' ', strip=True)
ids = [element['id'] for element in music.select('[id]')]
assert len(ids) == len(set(ids)), 'Duplicate Music IDs'
for card in vault.select('.vault-item[data-vault-kind="songs"]'):
    href = card.select_one('a')['href']
    assert href.startswith('/albums/#track-'), href
    target = music.find(id=href.split('#', 1)[1])
    assert target and target.select_one('h3').get_text() == card.select_one('h2').get_text(), href
trailer = music.select_one('#track-this-is-ghostheart a')
assert trailer['href'] == 'https://www.youtube.com/watch?v=AOCRvtz92JM'
assert trailer.get_text() == 'Watch trailer'
assert vault.select_one('.vault-item[data-vault-kind="videos"] a[href="https://www.youtube.com/watch?v=9sbFgjM_SDE"]')
assert len(vault.select('.vault-item[data-vault-featured="true"]')) == 3
assert {button["data-vault-filter"] for button in vault.select("[data-vault-filter]")} == {
    "featured", "songs", "videos", "shorts", "quotes", "all"
}
assert all(card.select_one("a[href]") for card in vault.select(".vault-item"))
assert not vault.select("a[download]")
assert all(card.select_one('a[href="/albums/#track-that-aint-holy"]') for card in
           vault.select('.vault-item[data-vault-kind="shorts"]')[1:])
assert vault.select('.vault-item[data-vault-kind="shorts"]')[0].select_one('a[href="/albums/#track-cruel"]')
assert {a["href"] for a in vault.select('.vault-item[data-vault-kind="shorts"] a[href^="https://www.youtube.com/shorts/"]')} == {
    'https://www.youtube.com/shorts/2fq-XQxtFuo',
    'https://www.youtube.com/shorts/ofU09J3bkHI',
    'https://www.youtube.com/shorts/5HUWedEnnsA',
    'https://www.youtube.com/shorts/bkm3czEmk5g',
    'https://www.youtube.com/shorts/5b43JyYmIts',
}
assert home.select_one("#home-vault [data-daily-quote]")
assert home.select_one('#latest .label span').get_text() == 'FEATURED NOW'
assert home.select_one('#latest .ctas a')['href'] == 'https://www.youtube.com/watch?v=RtFTIssLd0s'
assert home.select_one('#latest .ctas a').get_text() == 'Watch the full film'
assert not home.select_one('#latest audio')
assert home.select_one('#home-story a')['href'] == '/GhostHeart_Story.html#behind-the-scars'
assert home.select_one('.canon-hero__line').get_text() == 'GhostHeart is the fictional reflection of one man’s real life—told through music, stories, and a mission to help people feel less alone.'
assert [section.get('id') for section in home.select('main > section')][:5] == ['home', 'latest', 'home-story', 'mission-board', 'everywhere']
assert not home.select_one('section#join-the-signal'), 'One email signup block on the homepage: the Heart Rebellion invitation'
assert home.select_one('aside#join-the-signal.rebellion-invite'), 'Old #join-the-signal links land on the Heart Rebellion invitation'
assert home.select_one("#home-vault h2").get_text(" ", strip=True) == "The Vault"
assert not home.select('#home-vault .door[href="/GhostHeart_Quotes.html"], .sitefoot a[href="/GhostHeart_Quotes.html"]')
assert len(home.select('#home-story a[href^="/GhostHeart_Story.html"]')) == 1
assert 'Live day: Sunday.' in home.get_text()

assert home.select_one('#home-vault a[href="/vault/"]')
assert not home.select_one("#home-lives")
assert home.select_one('#mission-board a[href="/live/"]')
assert not home.select_one('#mission-board form')
assert home.select_one('#mission-board a[href="/GhostHeart_Resources.html"]')
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
    assert 'Next Sunday Live' not in text, path
    assert 'Sunday readings will connect' not in text, path
assert home.select_one('a[href="/GhostHeart_Resources.html"]')
assert "Join the Signal" not in home.get_text(" ", strip=True)
for relative in ("index.html", "GhostHeart_Story.html", "woman-behind-the-scenes/index.html", "albums/index.html", "GhostHeart_Videos.html", "live/index.html", "vault/index.html", "journal/index.html", "GhostHeart_Projects.html", "GhostHeart_Resources.html", "start/index.html", "follow/index.html"):
    # LOUD redesign (2026-10-14): redesigned routes use the LOUD stylesheet instead of the review theme.
    document = page(relative)
    assert document.select_one('link[href="/assets/shared/review-theme.css"]') or document.select_one('link[href="/assets/loud/loud.css"]'), relative
print("PASS World review: visible pending Lives, scoped 39-item Vault, exact track fragments, trailer label, reading aliases, shared theme")
