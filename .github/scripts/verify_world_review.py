#!/usr/bin/env python3
"""Check the local World/Vault review draft after a full site build."""

from pathlib import Path

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
assert len(blog.select("#entries article")) == 3
assert blog.select_one('a[href="/journal/how-we-got-here-archive.html"]')
assert page("journal/how-we-got-here.html").select_one('meta[http-equiv="refresh"]')["content"].endswith("/GhostHeart_Story.html")
assert len(films.select(".g-film[id]")) == 5
assert len(films.select("[id^=film-][hidden]")) >= 18
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
    assert image_url == 'https://www.myghostheart.com/assets/story/ghostheart-awakening-banner.png'
    assert (ROOT / image_url.removeprefix('https://www.myghostheart.com/')).is_file()
    assert document.select_one('meta[name="twitter:card"]')['content'] == 'summary_large_image'
live = page("live/index.html")
assert "No Live sessions are currently scheduled." in live.get_text(" ", strip=True)
assert not live.select_one("#next-live-title")
assert not live.select_one("#live-replay")
assert not live.select_one('time')

counts = {kind: len(vault.select(f'.vault-item[data-vault-kind="{kind}"]'))
          for kind in ("songs", "videos", "shorts", "quotes")}
assert counts == {"songs": 11, "videos": 6, "shorts": 5, "quotes": 17}, counts
music = page('albums/index.html')
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
assert home.select_one('#latest audio source')['src'] == '/assets/music/preview/awakening-01-cruel.mp3'
assert home.select_one('#home-story a')['href'] == '/GhostHeart_Story.html#behind-the-scars'
assert home.select_one('.canon-hero__line').get_text() == 'GhostHeart is the fictional reflection of one man’s real life—told through music, stories, and a mission to help people feel less alone.'
assert [section.get('id') for section in home.select('main > section')][:4] == ['home', 'latest', 'home-story', 'join-the-signal']
assert home.select_one("#home-vault h2").get_text(" ", strip=True) == "GhostHeart's Vault"
assert home.select_one('#home-vault a[href="/vault/"]')
assert not home.select_one("#home-lives")
assert not home.select_one('a[href="/live/"]')
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts or '.github' in path.parts:
        continue
    document = page(path.relative_to(ROOT))
    for link in document.select('a[href]'):
        target = link['href'].replace('../', '').lstrip('/')
        assert target not in {'live/', 'live/index.html'}, (path, link)
    text = document.get_text(' ', strip=True)
    assert 'The Awakening Begins' not in text, path
    assert 'Next Sunday Live' not in text, path
    assert 'Sunday readings will connect' not in text, path
assert home.select_one('a[href="/GhostHeart_Resources.html"]')
assert "Join the Signal" not in home.get_text(" ", strip=True)
for relative in ("index.html", "GhostHeart_Story.html", "woman-behind-the-scenes/index.html", "albums/index.html", "GhostHeart_Videos.html", "live/index.html", "vault/index.html", "journal/index.html", "GhostHeart_Projects.html", "GhostHeart_Resources.html", "start/index.html", "follow/index.html"):
    assert page(relative).select_one('link[href="/assets/shared/review-theme.css"]'), relative
print("PASS World review: paused Lives, scoped 39-item Vault, exact track fragments, trailer label, reading aliases, shared theme")
