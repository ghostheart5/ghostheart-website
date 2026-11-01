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


nav = ["Home", "Music", "Enter My World", "Work with GhostHeart", "Merch"]  # renamed 2026-11-01 (owner yes)
# Owner request 2026-10-31: The Awakening lives under Enter My World; Stay Connected left the menu.
# Site audit 2026-11-01 (apply_clear_names.py): one name per place; Merch stays in the top bar only.
explore = {"The Awakening", "Behind the Scars", "The Woman Behind the Scenes", "The Vault", "Blog", "Lives", "Projects"}
checks = 0
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts or ".github" in path.parts:
        continue
    soup = page(path.relative_to(ROOT))
    primary = soup.select_one('header.ghx-header nav[aria-label="Main navigation"]')
    if primary:
        actual = [link.get_text(" ", strip=True) for link in primary.select("a")]
        assert actual == nav, (path, actual)
        toggle = soup.select_one('header.ghx-header button[aria-controls="gateway-menu"]')
        assert toggle and toggle.get_text(" ", strip=True).startswith("Explore")
        assert toggle.get("aria-expanded") == "false"
        assert soup.select_one('header.ghx-header a.ghx-help-link').get_text(" ", strip=True) == "Find Support"
        menu = soup.select_one('header.ghx-header nav#gateway-menu')
        assert menu and {a.get_text(" ", strip=True) for a in menu.select("a")} == explore
        styles = [a.get("href", "") for a in soup.select('link[rel="stylesheet"]')]
        relative = path.relative_to(ROOT).as_posix()
        if relative == 'GhostHeart_Story.html':
            assert styles[-3:] == ['/assets/loud/loud.css', '/assets/shared/compact-readings.css', '/assets/story/story-bottom-compact.css'], path
        elif relative.startswith('passages/'):
            assert styles[-2:] == ['/assets/loud/loud.css', '/assets/shared/compact-readings.css'], path
        else:
            assert styles and (styles[-1].endswith('/assets/shared/review-theme.css') or styles[-1] in ('/assets/loud/loud.css', '/assets/loud/loud-skin.css')), path
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
assert story.select_one('a[href="/woman-behind-the-scenes/"]')
assert story.select_one('#behind-the-scars')
assert story.select_one('h1').get_text(' ', strip=True) == 'Enter My World.'
assert page('GhostHeart_Angel.html').select_one('a[href="/woman-behind-the-scenes/"]')
assert story.select_one('a[href*="GhostHeart_Resources.html"]')
assert (ROOT / "journal/how-we-got-here-archive.html").is_file()

music = page("albums/index.html")
assert len(music.select("audio")) == 11
assert len(music.select(".music-youtube")) == 6
audio = list((ROOT / "assets/music/preview").glob("*.mp3"))
assert len(audio) == 11 and all(track.stat().st_size > 1_000_000 for track in audio)
assert max(track.stat().st_size for track in audio) < 100_000_000

# Owner decision 2026-11-01: readings are off the site; the My Promise text is kept in .github/content only.
assert not (ROOT / "live/my-promise.html").exists()
assert (ROOT / ".github/content/my-promise.txt").exists()

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
assert len(posts) == 6
for slug in ("ghosthearts-oath", "this-is-ghostheart", "youre-not-god"):
    article = page(f"journal/{slug}.html")
    # Comments switched on 2026-10-31 (Dom's yes); new comments wait for review before they show.
    assert len(article.select('[data-comment-thread]')) == 1, "Conversation box must be on the post"
    assert article.select('script[src*="/assets/journal/comments"]'), "Comment box script must load"
    assert len(article.select("form.signal-signup-form")) == 1

urls = [loc.text for loc in ET.parse(ROOT / "sitemap.xml").iter()
        if loc.tag.endswith("}loc")]
assert len(urls) == len(set(urls)), "Duplicate sitemap URLs"
print(f"PASS reviewed site: {checks} navigation shells, 11 MP3s, My Promise unpublished, 16 resources, 6 Journal entries")
