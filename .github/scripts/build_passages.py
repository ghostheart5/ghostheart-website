#!/usr/bin/env python3
"""Build the Passages list and reading pages from .github/content/passages/*.md.

Runs after apply_loud_design.py has written passages/index.html. A Passage is
published only when its file says `status: ready` AND its date has passed at
build time (PASSAGES_BUILD_NOW / GHOSTHEART_JOURNAL_BUILD_NOW override the clock
for tests). Everything else shows as a locked, dated card.
"""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / ".github/content/passages"
INDEX = ROOT / "passages/index.html"
SITE = "https://www.myghostheart.com"
START, END = "<!--PASSAGES-LIST:START-->", "<!--PASSAGES-LIST:END-->"


def build_now() -> datetime:
    raw = os.environ.get("PASSAGES_BUILD_NOW") or os.environ.get("GHOSTHEART_JOURNAL_BUILD_NOW")
    if raw:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


def parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n?(.*)\Z", text, re.S)
    if not match:
        raise SystemExit(f"Passages: {path.name} needs a --- header")
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"')
    for key in ("number", "title", "date", "status"):
        if not meta.get(key):
            raise SystemExit(f"Passages: {path.name} is missing {key}")
    if meta["status"] not in ("draft", "ready"):
        raise SystemExit(f"Passages: {path.name} status must be draft or ready")
    body = re.sub(r"<!--.*?-->", "", match.group(2), flags=re.S).strip()
    meta["paragraphs"] = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    meta["at"] = datetime.fromisoformat(meta["date"])
    meta["slug"] = path.stem.split("-", 1)[1]
    meta["day"] = meta["at"].strftime("%a, %b ") + str(meta["at"].day)
    if meta["status"] == "ready" and not meta.get("link") and not meta["paragraphs"]:
        raise SystemExit(f"Passages: {path.name} is ready but has no text")
    return meta


now = build_now()
passages = sorted((parse(p) for p in CONTENT.glob("[0-9][0-9]-*.md")), key=lambda m: m["number"])
for p in passages:
    p["href"] = p.get("link") or (f"/passages/{p['slug']}.html" if p["status"] == "ready" else None)
    p["open"] = bool(p["href"]) and p["at"] <= now
open_ones = [p for p in passages if p["open"]]
latest = open_ones[-1] if open_ones else None


def card(p: dict) -> str:
    when = f'<div class="when">{escape(p["day"])} · <b>7 PM CT</b></div>'
    title = escape(p["title"])
    if p.get("release_label") and p["open"]:
        when = f'<div class="when">{escape(p["release_label"])}</div>'
    state = "open" if p["open"] else "locked"
    latest_class = " latest" if p is latest else ""
    if p["open"]:
        teaser = f'<p class="tease">{escape(p["teaser"])}</p>' if p.get("teaser") else ""
        new = "New · " if p is latest else ""
        panel = (f'<div class="meta"><span class="live">{new}Out now</span> · The reading for the song</div>'
                 f'{teaser}<a class="btn red" href="{p["href"]}">Read Passage {p["number"]}</a>')
    else:
        panel = '<div class="meta">Coming · The reading for the song</div><span class="act">Not yet available</span>'
    return (f'<details class="p {state}{latest_class}" id="p{p["number"]}" data-at="{p["date"]}" '
            f'data-title="{title}" data-day="{escape(p["day"])}">'
            f'<summary><span class="no">{p["number"]}</span><div><h2>{title}</h2>{when}</div></summary>'
            f'<div class="passage-panel">{panel}</div></details>')


index = INDEX.read_text(encoding="utf-8")
if START not in index:
    raise SystemExit("Passages: list markers missing from passages/index.html")
cards = "\n".join(card(p) for p in reversed(passages))
index = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: START + "\n" + cards + "\n  " + END, index, flags=re.S)
index = re.sub(r'(<span class="num" id="passageCount">)\d+(</span>)', lambda m: m.group(1) + f"{len(passages):02d}" + m.group(2), index)
upcoming = next((p for p in passages if not p["open"] and p["at"] > now), None)
drop = (f'NEXT PASSAGE <b>{upcoming["number"]} · {escape(upcoming["title"])}</b> {escape(upcoming["day"]).upper()} · 7 PM CT'
        if upcoming else "<b>MORE PASSAGES COMING</b>")
index = re.sub(r'(<div class="next-drop" id="nextDrop">).*?(</div>)', lambda m: m.group(1) + drop + m.group(2), index, count=1, flags=re.S)
INDEX.write_text(index, encoding="utf-8")


def paragraph(text: str) -> str:
    if text.startswith("> "):
        text = " ".join(line.strip().removeprefix("> ") for line in text.splitlines())
        return f'    <p class="pull">{escape(text)}</p>'
    text = " ".join(line.strip() for line in text.splitlines())
    return f"    <p>{escape(text)}</p>"


def reading_page(p: dict) -> str:
    page = index
    title = f'{p["title"]} · Passage {p["number"]} | GhostHeart'
    desc = p.get("teaser") or f'Passage {p["number"]}: the reading for {p["title"]}, from GhostHeart.'
    url = f'{SITE}/passages/{p["slug"]}.html'
    page = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", page, count=1)
    page = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + escape(desc, quote=True), page, count=1)
    page = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + escape(desc, quote=True), page, count=1)
    page = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + escape(title, quote=True), page, count=1)
    page = re.sub(r'(<meta property="og:type" content=")[^"]*', lambda m: m.group(1) + "article", page, count=1)
    page = page.replace(f'{SITE}/passages/"', f'{url}"')
    i = passages.index(p)
    prev_p = next((q for q in reversed(passages[:i]) if q["open"]), None)
    next_p = next((q for q in passages[i + 1:] if q["open"]), None)
    nav = []
    if prev_p:
        nav.append(f'<a class="btn ghost" href="{prev_p["href"]}">← Passage {prev_p["number"]}</a>')
    nav.append('<a class="btn red" href="/passages/">All Passages</a>')
    if next_p:
        nav.append(f'<a class="btn ghost" href="{next_p["href"]}">Passage {next_p["number"]} →</a>')
    audio = ""
    if p.get("audio"):
        audio = (f'  <div class="pair"><div><small>The song for this Passage</small><strong>{escape(p["title"])}</strong></div>'
                 f'<audio controls preload="none"><source src="/assets/music/preview/{escape(p["audio"], quote=True)}" type="audio/mpeg"></audio></div>\n')
    main = (f'<main class="reading">\n<header class="pg-hero r-hero">\n'
            f'  <span class="kicker">✶ Passage {p["number"]} · {escape(p["day"])} · 7 PM CT</span>\n'
            f'  <h1 class="display">{escape(p["title"])}</h1>\n</header>\n'
            f'<article class="r-body">\n' + "\n".join(paragraph(x) for x in p["paragraphs"]) + "\n</article>\n"
            f'<section class="r-end">\n{audio}'
            f'  <p class="care">Some parts of the story are hard to hear. You can pause or step away. '
            f'If you need support now, see <a href="/GhostHeart_Resources.html">Help &amp; Resources</a>.</p>\n'
            f'  <div class="ctas">{"".join(nav)}</div>\n</section>\n</main>')
    if p.get("release_label"):
        main = re.sub(r'<span class="kicker">.*?</span>',
                      lambda _: f'<span class="kicker">Passage {p["number"]} — {escape(p["release_label"])}</span>',
                      main, count=1)
    return re.sub(r"<main>.*?</main>", lambda _: main, page, count=1, flags=re.S)


published = set()
for p in passages:
    target = ROOT / "passages" / f'{p["slug"]}.html'
    if p["open"] and not p.get("link"):
        target.write_text(reading_page(p), encoding="utf-8")
        published.add(target.name)
for stale in (ROOT / "passages").glob("*.html"):
    if stale.name != "index.html" and stale.name not in published:
        stale.unlink()

sitemap = ROOT / "sitemap.xml"
value = sitemap.read_text(encoding="utf-8")
# Earlier pipeline steps rewrite the sitemap with ElementTree (which drops comments),
# so remove every Passages URL entry before adding the current ones.
value = re.sub(r"\s*<!-- PASSAGES:(START|END) -->", "", value)
value = re.sub(r"\s*<url>\s*<loc>" + re.escape(SITE) + r"/passages/[^<]*</loc>.*?</url>", "", value, flags=re.S)
entries = [f"{SITE}/passages/"] + [f"{SITE}/passages/{name}" for name in sorted(published)]
block = "\n  <!-- PASSAGES:START -->\n" + "\n".join(
    f"  <url>\n    <loc>{loc}</loc>\n  </url>" for loc in entries) + "\n  <!-- PASSAGES:END -->\n"
value = value.rstrip().removesuffix("</urlset>").rstrip() + block + "</urlset>\n"
sitemap.write_text(value, encoding="utf-8", newline="\n")
print(f"Passages: {len(passages)} listed, {len(open_ones)} open, {len(published)} reading pages")
