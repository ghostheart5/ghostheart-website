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
assert story.select_one("#behind-the-scars h2").get_text(" ", strip=True) == "Behind the Scars"
assert story.select_one('a[href="/woman-behind-the-scenes/"]')
assert story.select_one('a[href="/journal/"]')
assert story.select_one('a[href="/GhostHeart_Resources.html"]')
assert love.select_one("h1").get_text(" ", strip=True) == "The Woman Behind the Scenes."
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
assert not start.select("form") and not follow.select("form") and not home.select("form")
live = page("live/index.html")
assert live.select_one("#next-live-title").get_text(" ", strip=True) == "The Awakening Begins"
assert "I'm a Nobody, Are You a Nobody Too?" in live.get_text(" ", strip=True)
assert live.select_one("#live-replay") and "No replay available yet" in live.select_one("#live-replay").get_text(" ", strip=True)
assert live.select_one('a[href="/live/my-promise.html"]')

counts = {kind: len(vault.select(f'.vault-item[data-vault-kind="{kind}"]'))
          for kind in ("songs", "videos", "shorts", "quotes")}
assert counts == {"songs": 11, "videos": 5, "shorts": 5, "quotes": 17}, counts
assert len(vault.select('.vault-item[data-vault-featured="true"]')) == 3
assert {button["data-vault-filter"] for button in vault.select("[data-vault-filter]")} == {
    "featured", "songs", "videos", "shorts", "quotes", "all"
}
assert all(card.select_one("a[href]") for card in vault.select(".vault-item"))
assert not vault.select("a[download]")
assert all(card.select_one('a[href="/albums/index.html#youre-not-god"]') for card in
           vault.select('.vault-item[data-vault-kind="shorts"]')[1:])
assert {a["href"] for a in vault.select('.vault-item[data-vault-kind="shorts"] a[href^="https://www.youtube.com/shorts/"]')} == {
    'https://www.youtube.com/shorts/2fq-XQxtFuo',
    'https://www.youtube.com/shorts/ofU09J3bkHI',
    'https://www.youtube.com/shorts/5HUWedEnnsA',
    'https://www.youtube.com/shorts/bkm3czEmk5g',
    'https://www.youtube.com/shorts/5b43JyYmIts',
}
assert home.select_one("#latest [data-daily-quote]")
assert home.select_one("#home-vault h2").get_text(" ", strip=True) == "GhostHeart's Vault"
assert home.select_one('#home-vault a[href="/vault/"]')
assert home.select_one("#home-lives h2").get_text(" ", strip=True) == "Lives & Readings"
assert home.select_one('#home-lives a[href="/live/"]')
assert home.select_one('a[href="/GhostHeart_Resources.html"]')
assert "Join the Signal" not in home.get_text(" ", strip=True)
for relative in ("index.html", "GhostHeart_Story.html", "woman-behind-the-scenes/index.html", "albums/index.html", "GhostHeart_Videos.html", "live/index.html", "vault/index.html", "journal/index.html", "GhostHeart_Projects.html", "GhostHeart_Resources.html", "start/index.html", "follow/index.html"):
    assert page(relative).select_one('link[href="/assets/shared/review-theme.css"]'), relative
print("PASS World review: Home Vault/Lives paths, scoped 38-item Vault, reading aliases, shared theme")
