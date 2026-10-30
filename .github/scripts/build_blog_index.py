#!/usr/bin/env python3
"""Build the Blog entry list and add released Passages to the journal feed.

Runs at the end of build_passages.py, which passes in its parsed `passages` and build clock `now`
(with `open` already decided against the build clock). The Blog index lists
every journal.json entry plus every released Passage, newest first, so a
Saturday Passage release updates the Blog and /journal/feed.xml without a hand
edit. Passages that only link to an existing Blog entry (Passage 01) are not
listed twice. The archived How We Got Here entry keeps its own archive card.
"""
from datetime import datetime, time, timezone
from email.utils import format_datetime, parsedate_to_datetime
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://www.myghostheart.com"
INDEX = ROOT / "journal/index.html"
FEED = ROOT / "journal/feed.xml"
ARCHIVED = {"how-we-got-here"}
PASSAGE_IMAGE = "/assets/story/ghostheart-awakening-banner.webp"
CENTRAL_NOON = time(12, 0)


def long_date(at: datetime) -> str:
    return at.strftime("%B ") + str(at.day) + at.strftime(", %Y")


def released_at(p: dict) -> datetime:
    """A late release keeps its scheduled date in the file and says the real day in release_label."""
    match = re.search(r"Released (\w{3}) (\d{1,2}), (\d{4})", p.get("release_label", ""))
    if not match:
        return p["at"]
    day = datetime.strptime(" ".join(match.groups()), "%b %d %Y").date()
    if day == p["at"].date():
        return p["at"]
    return datetime.combine(day, CENTRAL_NOON, tzinfo=p["at"].tzinfo)


def entries() -> list[dict]:
    items = []
    for post in json.loads((ROOT / ".github/content/journal.json").read_text(encoding="utf-8")):
        # Same rule as build_journal.py: only published entries whose time has come.
        if post["slug"] in ARCHIVED or post.get("status", "published") != "published":
            continue
        if datetime.fromisoformat(post["published"]) > now:  # noqa: F821 (provided by build_passages.py)
            continue
        items.append({"href": f'/journal/{post["slug"]}.html', "title": post["title"], "summary": post["summary"],
                      "label": post["category"], "at": datetime.fromisoformat(post["published"]), "image": post["image"],
                      "passage": None})
    for p in passages:  # noqa: F821 (provided by build_passages.py)
        if not p["open"] or p.get("link"):
            continue
        items.append({"href": p["href"], "title": p["title"], "summary": p.get("teaser", ""),
                      "label": f'Passage {p["number"]}', "at": released_at(p), "image": p.get("image") or PASSAGE_IMAGE,
                      "passage": p})
    return sorted(items, key=lambda item: item["at"], reverse=True)


def lead(item: dict) -> str:
    title = escape(item["title"])
    return (f'  <article class="lead-post journal-feature">\n'
            f'    <a class="thumb" href="{item["href"]}" style="background-image:url(\'{item["image"]}\')" aria-label="Read {title}"></a>\n'
            f'    <div>\n'
            f'      <small>{escape(item["label"])} · {long_date(item["at"])}</small>\n'
            f'      <h2>{title}</h2>\n'
            f'      <p>{escape(item["summary"])}</p>\n'
            f'      <a class="btn dark" href="{item["href"]}">Read the entry ↗</a>\n'
            f'    </div>\n'
            f'  </article>')


def row(number: int, item: dict) -> str:
    return (f'    <article><a href="{item["href"]}"><span class="no">{number:02d}</span><div>'
            f'<small>{escape(item["label"])} · {long_date(item["at"])}</small><h3>{escape(item["title"])}</h3>'
            f'<p>{escape(item["summary"])}</p></div><span class="go">Read ↗</span></a></article>')


def replace(text: str, name: str, body: str) -> str:
    start, end = f"<!--BLOG-{name}:START-->", f"<!--BLOG-{name}:END-->"
    if start not in text:
        raise SystemExit(f"Blog index: {name} markers missing from journal/index.html")
    return re.sub(re.escape(start) + ".*?" + re.escape(end), lambda _: f"{start}\n{body}\n  {end}", text, flags=re.S)


items = entries()
index = INDEX.read_text(encoding="utf-8")
index = replace(index, "LEAD", lead(items[0]))
rows = "\n".join(row(n, item) for n, item in enumerate(items[1:], start=2))
index = replace(index, "LIST", f'  <div class="posts journal-highlights">\n{rows}\n  </div>')
INDEX.write_text(index, encoding="utf-8")


def feed_item(item: dict) -> str:
    p = item["passage"]
    url = SITE + item["href"]
    body = "".join(f"<p>{escape(text.removeprefix('> '))}</p>" for text in p["paragraphs"])
    return ("    <item>\n"
            f"      <title>{escape(item['title'])}</title>\n"
            f"      <link>{url}</link>\n"
            f"      <category>{escape(item['label'])}</category>\n"
            f"      <pubDate>{format_datetime(item['at'])}</pubDate>\n"
            f'      <guid isPermaLink="true">{url}</guid>\n'
            f"      <description>{escape(body, quote=False)}</description>\n"
            "    </item>")


feed = FEED.read_text(encoding="utf-8")
blocks = re.findall(r"    <item>.*?</item>", feed, flags=re.S)
kept = [b for b in blocks if f"<link>{SITE}/passages/" not in b]
kept += [feed_item(item) for item in items if item["passage"]]


def pub(block: str) -> datetime:
    return parsedate_to_datetime(re.search(r"<pubDate>(.*?)</pubDate>", block).group(1))


kept.sort(key=pub, reverse=True)
head = feed[:feed.index(blocks[0])] if blocks else feed[:feed.index("  </channel>")]
newest = max((pub(b) for b in kept), default=datetime.now(timezone.utc))
head = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", f"<lastBuildDate>{format_datetime(newest)}</lastBuildDate>", head)
FEED.write_text(head + "\n".join(kept) + "\n  </channel>\n</rss>\n", encoding="utf-8", newline="\n")
print(f"Blog index: {len(items)} entries; feed carries {sum(1 for i in items if i['passage'])} Passages")
