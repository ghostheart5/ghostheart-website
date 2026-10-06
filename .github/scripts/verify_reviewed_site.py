#!/usr/bin/env python3
"""Verify the owner-approved public routes after the complete site build."""

from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]


def page(path):
    return BeautifulSoup((ROOT / path).read_text(encoding="utf-8"), "html.parser")


nav = ["Awakening", "Music", "Readings", "Projects"]
checks = 0
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts or ".github" in path.parts:
        continue
    soup = page(path.relative_to(ROOT))
    primary = soup.select_one('header.ghx-header nav[aria-label="Main navigation"]')
    if primary:
        actual = [link.get_text(" ", strip=True) for link in primary.select("a")]
        assert actual == nav, (path, actual)
        checks += 1
assert checks >= 44, checks

missing_page = page("404.html")
for element in missing_page.select("[href], [src]"):
    for name in ("href", "src"):
        url = element.get(name)
        if url and not url.startswith(("https://", "http://", "#")):
            assert url.startswith("/"), (name, url)
assert not page("GhostHeart_Privacy.html").select("script:not([src])")

story = page("GhostHeart_Story.html")
assert story.select_one("h1")
assert story.select_one('a[href*="GhostHeart_Angel.html"]')
assert story.select_one('a[href*="GhostHeart_Resources.html"]')
assert (ROOT / "journal/how-we-got-here-archive.html").is_file()

music = page("albums/index.html")
assert len(music.select("audio")) == 11
assert len(music.select(".music-youtube")) == 5
audio = list((ROOT / "assets/music/preview").glob("*.mp3"))
assert len(audio) == 11 and all(track.stat().st_size > 1_000_000 for track in audio)
assert max(track.stat().st_size for track in audio) < 100_000_000

source = (ROOT / ".github/content/my-promise.txt").read_text(encoding="utf-8").strip().split("\n\n")
rendered = [p.get_text(" ", strip=True) for p in page("live/my-promise.html").select(".reading-text p")]
assert len(rendered) == 15 and rendered == source[1:]

projects = page("GhostHeart_Projects.html")
assert projects.select_one("#axiomara")
assert projects.select_one('a[href*="play.google.com/store/apps/details?id=com.ghostheart5.chronospark"]')

resources = page("GhostHeart_Resources.html")
main = resources.select_one("#resources-main")
baseline = json.loads((ROOT / ".github/reviewed-inputs/resources-baseline.json").read_text(encoding="utf-8"))
cards = {}
for card in main.select(".resource-grid .resource"):
    cards[card["id"]] = {
        "text": " ".join(card.stripped_strings),
        "links": sorted(a.get("href", "") for a in card.select("a[href]")),
        "tags": card.get("data-tags", ""),
    }
assert cards == baseline["cards"] and len(cards) == 16
assert sorted(a.get("href", "") for a in main.select("a[href]")) == baseline["main_links"]
assert " ".join(main.select_one(".boundary").stripped_strings) == baseline["boundary"]
assert main.select_one('.filter[data-filter="all"]')["aria-pressed"] == "true"
assert main.select_one(".urgent").sourceline < main.select_one(".catalog").sourceline

posts = json.loads((ROOT / ".github/content/journal.json").read_text(encoding="utf-8"))
assert len(posts) == 4
for slug in ("ghosthearts-oath", "this-is-ghostheart", "youre-not-god"):
    article = page(f"journal/{slug}.html")
    assert article.select_one('[data-comment-status="pending"]')
    assert not article.select(".journal-comments form")

urls = [loc.text for loc in ET.parse(ROOT / "sitemap.xml").iter()
        if loc.tag.endswith("}loc")]
assert len(urls) == len(set(urls)), "Duplicate sitemap URLs"
print(f"PASS reviewed site: {checks} navigation shells, 11 MP3s, 15 exact reading paragraphs, 16 resources, 4 Journal entries")
