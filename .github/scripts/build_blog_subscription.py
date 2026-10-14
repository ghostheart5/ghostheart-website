#!/usr/bin/env python3
"""Apply the owner-approved reading and optional email signup improvements."""
from pathlib import Path
import copy
import json
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
CONNECTION = json.loads((ROOT / '.github/content/connection.json').read_text(encoding='utf-8'))
EMAIL_VALUE = CONNECTION['benefits']
SIGNUP_NOTE = 'You’ll finish signup in a new Mailchimp tab. Confirm through the email it sends. Unsubscribe anytime. Read the <a href="/GhostHeart_Privacy.html">privacy notice</a>.'
follow_path = ROOT / "follow/index.html"
follow = BeautifulSoup(follow_path.read_text(encoding="utf-8"), "html.parser")
provider_form = follow.select_one("form.signal-signup-form")
assert provider_form and provider_form.get("method", "").lower() == "post"
posts = json.loads((ROOT / ".github/content/journal.json").read_text(encoding="utf-8"))
closed_threads = {post["slug"] for post in posts if post.get("comments_enabled") is False}


def signup(placement):
    ident = "blog-" + placement + "-signup"
    section = BeautifulSoup(
        f'<section class="journal-signup" aria-labelledby="{ident}-title">'
        f'<h2 id="{ident}-title">{CONNECTION["heading"]}</h2>'
        f'<p>{EMAIL_VALUE}</p><p class="connection-optional">{CONNECTION["optional"]}</p></section>', "html.parser").section
    form = copy.deepcopy(provider_form)
    field = form.select_one('input[name="EMAIL"]')
    previous = field["id"]
    field["id"] = ident + "-email"
    field["aria-describedby"] = ident + "-note"
    form.select_one(f'label[for="{previous}"]')["for"] = field["id"]
    note = form.select_one("#follow-note")
    note["id"] = ident + "-note"
    note.clear()
    note.append(BeautifulSoup(SIGNUP_NOTE, "html.parser"))
    form.select_one('button[type="submit"]').string = CONNECTION['button']
    form.select_one(".g-form-status").clear()
    section.append(form)
    section.append(BeautifulSoup(
        '<p class="journal-signup-fallback">You can also <a href="/follow/">sign up on the Stay Connected page</a>.</p>',
        "html.parser"))
    return section


for path in sorted((ROOT / "journal").glob("*.html")):
    doc = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    article = doc.select_one("article.journal-article")
    index = path.name == "index.html"
    if not article and not index:
        continue  # Preserve the historical redirect.
    for previous in doc.select(".journal-signup"):
        previous.decompose()
    if article:
        article.select_one(".journal-prose").insert_after(signup(path.stem))
        # Discussion remains pending its separate release review.
        slug = "how-we-got-here" if path.stem == "how-we-got-here-archive" else path.stem
        if slug in closed_threads:
            for closed in doc.select(".journal-comments"):
                closed.decompose()
            for script in doc.select('script[src*="/assets/journal/comments"]'):
                script.decompose()
    else:
        hero = doc.select_one(".journal-hero")
        hero.select_one("h1").string = "Behind the songs."
        hero.select_one(".ghx-lead").string = (
            "The songs don’t tell you everything. Here I write about the thoughts behind them "
            "and the questions they leave with me.")
        doc.select_one(".journal-feature").insert_after(signup("index"))
        highlights = doc.select_one(".journal-highlights")
        if highlights:
            doc.select_one("#entries").insert_after(highlights.extract())
        for meta in doc.select('meta[name="description"], meta[property="og:description"]'):
            meta["content"] = "Writing about the thoughts behind GhostHeart’s songs and the questions they leave."
    for link in doc.select("a[href]"):
        if link.get_text(" ", strip=True) in {"Stay Connected", "Follow by email", "Follow by email ↗"}:
            link["href"] = "/follow/"
    theme = doc.select_one('link[href="/assets/shared/review-theme.css"]')
    assert theme, path
    style = doc.select_one('link[href="/assets/shared/blog-subscription.css"]')
    style = style.extract() if style else doc.new_tag("link", attrs={"rel": "stylesheet", "href": "/assets/shared/blog-subscription.css"})
    theme.insert_before(style)
    if not doc.select_one('script[src="/assets/journal/subscription.js"]'):
        doc.head.append(doc.new_tag("script", attrs={"defer": "", "src": "/assets/journal/subscription.js"}))
    path.write_text(str(doc), encoding="utf-8", newline="\n")

heading = follow.select_one("#email-signup-title")
heading.string = CONNECTION['heading']
heading.find_next_sibling("p").string = EMAIL_VALUE
for previous in heading.parent.select('.connection-optional'):
    previous.decompose()
heading.find_next_sibling('p').insert_after(BeautifulSoup(
    f'<p class="connection-optional">{CONNECTION["optional"]}</p>', 'html.parser'))
provider_form.select_one('button[type="submit"]').string = CONNECTION['button']
note = provider_form.select_one("#follow-note")
note.clear()
note.append(BeautifulSoup(SIGNUP_NOTE, "html.parser"))
for meta in follow.select('meta[name="description"], meta[property="og:description"]'):
    meta["content"] = EMAIL_VALUE
follow_path.write_text(str(follow), encoding="utf-8", newline="\n")
legacy_path = ROOT / 'ghostheart-website/join.html'
legacy = BeautifulSoup(legacy_path.read_text(encoding='utf-8'), 'html.parser')
legacy.title.string = CONNECTION['heading']
legacy.select_one('meta[name="description"]')['content'] = EMAIL_VALUE
legacy.select_one('h1').string = CONNECTION['heading']
legacy.select_one('main a').string = CONNECTION['button']
legacy_path.write_text(str(legacy), encoding='utf-8', newline='\n')
print("Applied blog reading order, optional signup forms and direct email route; discussion remains closed.")
