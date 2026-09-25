#!/usr/bin/env python3
"""Build static journal pages and RSS from one source. Run from any directory."""
from datetime import datetime
from email.utils import format_datetime
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://www.myghostheart.com'
POSTS = json.loads((ROOT / '.github/content/journal.json').read_text(encoding='utf-8'))
POSTS.sort(key=lambda item: item['published'], reverse=True)
assert len({post['slug'] for post in POSTS}) == len(POSTS), 'Duplicate journal slug'
HOME = (ROOT / 'index.html').read_text(encoding='utf-8')

def absolute_shell(text):
    text = text.replace(' aria-current="page"', '')
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
    return datetime.fromisoformat(post['published'])

def meta(post):
    return f'<p class="journal-meta">{escape(post["category"])} · Journal entry <time datetime="{date(post).date()}">{date(post).strftime("%B %d, %Y")}</time></p>'

def art(post, linked=False):
    picture = f'<img alt="" src="{escape(post["image"])}" width="1280" height="720" loading="lazy"/>'
    if linked:
        return f'<a class="journal-art" href="{post_path(post)}" aria-label="Read {escape(post["title"], quote=True)}">{picture}</a>'
    return f'<figure class="journal-art">{picture}</figure>'

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
feature = f'''<article class="journal-feature">{art(first, True)}<div><p class="ghx-kicker">From the journal</p>{meta(first)}
<h2><a href="{post_path(first)}">{escape(first['title'])}</a></h2><p>{escape(first['summary'])}</p>
<a class="journal-link" href="{post_path(first)}">Read the entry ↗</a></div></article>'''
entries = ''.join(f'''<article class="journal-entry"><span class="journal-number" aria-hidden="true">{i:02}</span><div>{meta(post)}
<h2><a href="{post_path(post)}">{escape(post['title'])}</a></h2><p>{escape(post['summary'])}</p>
<a class="journal-link" href="{post_path(post)}">Read the entry ↗</a></div>{art(post, True)}</article>''' for i, post in enumerate(POSTS[1:], 2))
body = f'''<div class="ghx-wrap"><header class="journal-hero"><p class="ghx-kicker">GhostHeart / Journal</p>
<h1>Words from<br/>the heart.</h1><p class="ghx-lead">Song stories, films, and notes from the world of GhostHeart. A place to stay with the words.</p>
<div class="ghx-actions"><a href="#entries">Read the journal ↓</a><a href="/journal/feed.xml">Follow via RSS ↗</a></div></header>
<section aria-label="Journal entries" id="entries">{feature}<div class="journal-list">{entries}</div></section>
<aside class="journal-follow"><p class="ghx-kicker">Keep a little light close</p><h2>Carry the next page with you.</h2>
<p>Follow the journal in your feed reader, or join the Signal for GhostHeart updates by email.</p><div class="ghx-actions">
<a class="primary" href="/index.html#join-the-signal">Join the Signal</a><a class="secondary" href="/journal/feed.xml">RSS feed</a></div></aside></div>'''
write('journal/index.html', shell('Journal', 'Song stories, films, and notes from the world of GhostHeart.', '/journal/', body, first['image']))

for post in POSTS:
    links = ''.join(f'<a class="{"secondary" if i else "primary"}" href="{escape(link["url"], quote=True)}">{escape(link["label"])}</a>' for i, link in enumerate(post['links']))
    paragraphs = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in post['paragraphs'])
    body = f'''<div class="ghx-wrap"><article class="journal-article"><a class="journal-back journal-link" href="/journal/">← GhostHeart Journal</a>
<header>{meta(post)}<h1>{escape(post['title'])}</h1><p class="journal-deck">{escape(post['summary'])}</p></header>
{art(post)}<div class="journal-prose">{paragraphs}</div><section class="journal-continue" aria-label="Continue the story">
<h2>Stay with the story.</h2><div class="ghx-actions">{links}</div></section>
<nav class="journal-next ghx-actions" aria-label="More from GhostHeart"><a href="/journal/">All journal entries ↗</a><a href="/index.html#join-the-signal">Join the Signal ↗</a></nav>
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
print(f'Built journal index, {len(POSTS)} entries, and RSS feed.')
