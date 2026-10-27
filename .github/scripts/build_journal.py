#!/usr/bin/env python3
"""Build public journal pages, homepage links, RSS, and sitemap from one source."""
import argparse
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://www.myghostheart.com'
SOURCE_PATH = ROOT / '.github/content/journal.json'


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--now',
        help='ISO 8601 build time used for deterministic checks. Defaults to current UTC time.',
    )
    return parser.parse_args()


def iso_datetime(value, field):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError(f'{field} must include a timezone')
    return parsed


def public_posts(now):
    posts = json.loads(SOURCE_PATH.read_text(encoding='utf-8'))
    assert len({post['slug'] for post in posts}) == len(posts), 'Duplicate journal slug'
    visible = []
    for post in posts:
        status = post.get('status', 'published')
        if status not in {'draft', 'approved', 'published'}:
            raise ValueError(f"Unsupported journal status for {post['slug']}: {status}")
        publish_at = iso_datetime(post['published'], f"{post['slug']}.published")
        if status == 'published' and publish_at <= now:
            visible.append(post)
    visible.sort(key=lambda item: iso_datetime(item['published'], 'published'), reverse=True)
    if not visible:
        raise ValueError('The public journal must contain at least one published entry')
    return visible


ARGS = arguments()
NOW = iso_datetime(ARGS.now, '--now') if ARGS.now else datetime.now(timezone.utc)
POSTS = public_posts(NOW)
HOME_PATH = ROOT / 'index.html'
HOME = HOME_PATH.read_text(encoding='utf-8')

def absolute_shell(text):
    text = text.replace(' aria-current="page"', '')
    text = re.sub(r'href="#([^"]+)"', r'href="/index.html#\1"', text)
    return re.sub(r'(href|src)="(?!https?:|/|#)([^"]+)"', r'\1="/\2"', text)

HEADER = absolute_shell(re.search(r'<header\b.*?</header>', HOME, re.S).group())
FOOTER = absolute_shell(re.search(r'<footer\b.*?</footer>', HOME, re.S).group())

def write(path, text):
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding='utf-8', newline='\n')

def post_path(post):
    return f"/journal/{post['slug']}.html"

def date(post):
    return iso_datetime(post['published'], f"{post['slug']}.published")

def meta(post):
    return f'<p class="journal-meta">{escape(post["category"])} · Journal entry <time datetime="{date(post).date()}">{date(post).strftime("%B %d, %Y")}</time></p>'

def art(post, linked=False):
    picture = f'<img alt="" src="{escape(post["image"])}" width="1280" height="720" loading="lazy"/>'
    if linked:
        return f'<a class="journal-art" href="{post_path(post)}" aria-label="Read {escape(post["title"], quote=True)}">{picture}</a>'
    return f'<figure class="journal-art">{picture}</figure>'

def journal_header(path):
    header = re.sub(r' aria-current="[^"]*"', '', HEADER)
    current = 'page' if path == '/journal/' else 'location'
    return header.replace('<a href="/journal/">Blog</a>', f'<a aria-current="{current}" href="/journal/">Blog</a>')

def shell(title, description, path, body, image, article=None):
    structured = ''
    if article:
        data = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': article['title'],
                'description': article['summary'], 'datePublished': article['published'],
                'dateModified': article['published'], 'mainEntityOfPage': BASE + path,
                'image': BASE + image, 'author': {'@type': 'Organization', 'name': 'GhostHeart', 'url': BASE + '/'}}
        structured = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    return f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{escape(title)} | GhostHeart</title><meta name="description" content="{escape(description, quote=True)}"/>
<link rel="canonical" href="{BASE}{path}"/><link rel="icon" href="/favicon.ico"/>
<link rel="alternate" type="application/rss+xml" title="GhostHeart Journal" href="/journal/feed.xml"/>
<link rel="stylesheet" href="/assets/shared/release-site.css"/>
<link rel="stylesheet" href="/assets/shared/ghostheart-world.css"/>
<link rel="stylesheet" href="/assets/shared/journal.css"/>
<script defer src="/assets/shared/ghostheart-world.js"></script>
<meta property="og:type" content="{'article' if article else 'website'}"/><meta property="og:site_name" content="GhostHeart"/>
<meta property="og:title" content="{escape(title, quote=True)}"/><meta property="og:description" content="{escape(description, quote=True)}"/>
<meta property="og:url" content="{BASE}{path}"/><meta property="og:image" content="{BASE}{image}"/>
<meta name="twitter:card" content="summary_large_image"/>{structured}
</head><body class="ghx-site">
<a class="skip-link" href="#main-content">Skip to content</a>{HEADER}
<main id="main-content">{body}</main>{FOOTER}
</body></html>
'''

first = POSTS[0]
public_article_names = {f"{post['slug']}.html" for post in POSTS}
for existing_article in (ROOT / 'journal').glob('*.html'):
    if existing_article.name != 'index.html' and existing_article.name not in public_article_names:
        existing_article.unlink()

feature = f'''<article class="journal-feature">{art(first, True)}<div><p class="ghx-kicker">From the blog</p>{meta(first)}
<h2><a href="{post_path(first)}">{escape(first['title'])}</a></h2><p>{escape(first['summary'])}</p>
<a class="journal-link" href="{post_path(first)}">Read the entry ↗</a></div></article>'''
entries = ''.join(f'''<article class="journal-entry"><span class="journal-number" aria-hidden="true">{i:02}</span><div>{meta(post)}
<h2><a href="{post_path(post)}">{escape(post['title'])}</a></h2><p>{escape(post['summary'])}</p>
<a class="journal-link" href="{post_path(post)}">Read the entry ↗</a></div>{art(post, True)}</article>''' for i, post in enumerate(POSTS[1:], 2))
body = f'''<div class="ghx-wrap"><header class="journal-hero"><p class="ghx-kicker">GhostHeart / Blog</p>
<h1>Words from<br/>the heart.</h1><p class="ghx-lead">Song stories, films, and notes from the world of GhostHeart. A place to stay with the words.</p>
<div class="ghx-actions"><a href="#entries">Read the blog ↓</a><a href="/journal/feed.xml">Follow via RSS ↗</a></div></header>
<section aria-label="Journal entries" id="entries">{feature}<div class="journal-list">{entries}</div></section>
<aside class="journal-follow"><p class="ghx-kicker">Keep a little light close</p><h2>Carry the next page with you.</h2>
<p>Follow the journal in your feed reader, or join the Heartbeat for GhostHeart updates by email.</p><div class="ghx-actions">
<a class="primary" href="/index.html#join-the-signal">Join the Heartbeat</a><a class="secondary" href="/journal/feed.xml">RSS feed</a></div></aside></div>'''
write('journal/index.html', shell('Blog', 'Song stories, films, and notes from the world of GhostHeart.', '/journal/', body, first['image']))

for post in POSTS:
    links = ''.join(f'<a class="{"secondary" if i else "primary"}" href="{escape(link["url"], quote=True)}">{escape(link["label"])}</a>' for i, link in enumerate(post['links']))
    paragraphs = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in post['paragraphs'])
    body = f'''<div class="ghx-wrap"><article class="journal-article"><a class="journal-back journal-link" href="/journal/">← GhostHeart Journal</a>
<header>{meta(post)}<h1>{escape(post['title'])}</h1><p class="journal-deck">{escape(post['summary'])}</p></header>
{art(post)}<div class="journal-prose">{paragraphs}</div><section class="journal-continue" aria-label="Continue the story">
<h2>Stay with the story.</h2><div class="ghx-actions">{links}</div></section>
<nav class="journal-next ghx-actions" aria-label="More from GhostHeart"><a href="/journal/">All journal entries ↗</a><a href="/index.html#join-the-signal">Join the Heartbeat ↗</a></nav>
</article></div>'''
    write(post_path(post).lstrip('/'), shell(post['title'], post['summary'], post_path(post), body, post['image'], post))

ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
rss = ET.Element('rss', {'version': '2.0'})
channel = ET.SubElement(rss, 'channel')
for tag, value in [('title', 'GhostHeart Journal'), ('link', BASE + '/journal/'),
                   ('description', 'Song stories, films, and notes from the world of GhostHeart.'), ('language', 'en-us'),
                   ('lastBuildDate', format_datetime(date(POSTS[0]))), ('copyright', '2026 GhostHeart')]:
    ET.SubElement(channel, tag).text = value
ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {'href': BASE + '/journal/feed.xml', 'rel': 'self', 'type': 'application/rss+xml'})
for post in POSTS:
    item = ET.SubElement(channel, 'item')
    for tag, value in [('title', post['title']), ('link', BASE + post_path(post)), ('category', post['category']), ('pubDate', format_datetime(date(post)))]:
        ET.SubElement(item, tag).text = value
    ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = BASE + post_path(post)
    description = '<p>' + escape(post['summary']) + '</p>'
    description += ''.join('<p>' + escape(p) + '</p>' for p in post['paragraphs'])
    description += ''.join(f'<p><a href="{escape(urljoin(BASE, link["url"]), quote=True)}">{escape(link["label"])}</a></p>' for link in post['links'])
    ET.SubElement(item, 'description').text = description
ET.indent(rss)
write('journal/feed.xml', '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding='unicode') + '\n')

latest_link = f'<a href="{post_path(first)}">{escape(first["title"])} ↗</a>'
home_marker = re.compile(
    r'<!-- JOURNAL-LATEST:START -->.*?<!-- JOURNAL-LATEST:END -->',
    re.S,
)
if not home_marker.search(HOME):
    raise ValueError('Homepage is missing JOURNAL-LATEST markers')
HOME = home_marker.sub(
    f'<!-- JOURNAL-LATEST:START -->{latest_link}<!-- JOURNAL-LATEST:END -->',
    HOME,
)
write('index.html', HOME)

sitemap_path = ROOT / 'sitemap.xml'
sitemap = sitemap_path.read_text(encoding='utf-8')
sitemap_marker = re.compile(
    r'  <!-- JOURNAL-GENERATED:START -->.*?  <!-- JOURNAL-GENERATED:END -->',
    re.S,
)
latest_day = date(first).date().isoformat()
sitemap_urls = [('/journal/', latest_day)] + [
    (post_path(post), date(post).date().isoformat()) for post in POSTS
]
sitemap_block = '  <!-- JOURNAL-GENERATED:START -->\n' + '\n'.join(
    '  <url>\n'
    f'    <loc>{BASE}{path}</loc>\n'
    f'    <lastmod>{lastmod}</lastmod>\n'
    '  </url>'
    for path, lastmod in sitemap_urls
) + '\n  <!-- JOURNAL-GENERATED:END -->'
if not sitemap_marker.search(sitemap):
    raise ValueError('Sitemap is missing JOURNAL-GENERATED markers')
write('sitemap.xml', sitemap_marker.sub(sitemap_block, sitemap))

print(
    f'Built journal index, {len(POSTS)} public entries, homepage latest link, RSS feed, and sitemap.'
)
