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
LIVE = json.loads((ROOT / '.github/content/live.json').read_text(encoding='utf-8'))
assert LIVE['starts_at'] == '2026-10-11T10:00:00-05:00' and LIVE['time_zone'] == 'America/Chicago'
assert LIVE['platform'] is None and LIVE['view_url'] is None
quote_source = (ROOT / 'GhostHeart_Quotes.html').read_text(encoding='utf-8')
quote_match = re.search(r'const quotes = (\[.*?\]);', quote_source, re.S)
QUOTES = (json.loads(quote_match.group(1)) if quote_match else
          json.loads((ROOT / '.github/content/site-library.json').read_text(encoding='utf-8'))['quotes'])
assert len(QUOTES) == 17
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
    if post['slug'] == 'how-we-got-here':
        return '/journal/how-we-got-here-archive.html'
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
    header = HEADER
    if path.startswith('/journal/'):
        header = header.replace('<a href="/journal/">Blog</a>', '<a aria-current="page" href="/journal/">Blog</a>')
    if path == '/GhostHeart_Story.html':
        header = header.replace('<a href="/GhostHeart_Story.html">Awakening</a>', '<a aria-current="page" href="/GhostHeart_Story.html">Awakening</a>')
        header = header.replace('<a href="/GhostHeart_Story.html">GhostHeart\'s Awakening</a>', '<a aria-current="page" href="/GhostHeart_Story.html">GhostHeart\'s Awakening</a>')
        header = header.replace('<a href="/GhostHeart_Videos.html">Films</a>', '')
        header = header.replace('<h2>Listen &amp; watch</h2>', '<h2>Music</h2>')
        header = header.replace('<a href="/GhostHeart_Videos.html">Films &amp; Shorts</a>', '')
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
<link rel="stylesheet" href="/assets/shared/journal.css"/>{'<link rel="stylesheet" href="/assets/story/story-reading.css"/>' if path == '/GhostHeart_Story.html' else ''}
{'<link rel="stylesheet" href="/assets/journal/highlights.css"/>' if path.startswith('/journal/') else ''}
<script defer src="/assets/shared/ghostheart-world.js"></script>
{'<script defer src="/assets/journal/daily-quote.js"></script>' if path == '/journal/' else ''}
{'<script defer src="/assets/journal/comments-config.js"></script><script defer src="/assets/journal/comments.js"></script>' if article else ''}
<meta property="og:type" content="{'article' if article else 'website'}"/><meta property="og:site_name" content="GhostHeart"/>
<meta property="og:title" content="{escape(title, quote=True)}"/><meta property="og:description" content="{escape(description, quote=True)}"/>
<meta property="og:url" content="{BASE}{path}"/><meta property="og:image" content="{BASE}{image}"/>
<meta name="twitter:card" content="summary_large_image"/>{structured}
</head><body class="ghx-site">
<a class="skip-link" href="#main-content">Skip to content</a>{header}
<main id="main-content">{body}</main>{FOOTER}
</body></html>
'''

story_body = '''<div class="ghx-wrap story-reading">
<header class="story-reading-hero"><p class="ghx-kicker">The Story</p>
<h1>GhostHeart&rsquo;s Awakening.</h1>
<p class="ghx-lead">Survival matters. So does what a person chooses to carry forward.</p>
<figure class="story-reading-banner"><img src="/assets/story/ghostheart-awakening-banner.png" width="2560" height="1440" alt="GhostHeart sits beneath storm clouds beside the GhostHeart Studios mark, with crimson light over a city horizon"/></figure>
</header>
<div class="story-reading-copy" aria-label="The heart behind GhostHeart">
<p>Survival matters. So does what a person chooses to carry forward. GhostHeart turns toward people who have been reduced to a label, judged from a distance, or written off before their story was heard. Seeing their humanity does not mean looking away from the truth or excusing harm. It means refusing to let one word tell the whole story.</p>
<p>That is where the name meets the promise. This Is GhostHeart introduces the heart behind the music. GhostHeart&rsquo;s Oath gives that heart a direction: protect the light in others. These songs are ways into the story, and you can begin with either one.</p>
<p>Love belongs here too. GhostHeart and His Angel is the relationship story within this world&mdash;the person who saw the heart beneath the scars and never asked it to hide. It has its own place alongside the music and the life behind it.</p>
<p>You do not have to share this past to find something in these words. Stay with a song. Carry a line that means something to you. Find support when you need more than a story can offer. No one has to disclose their own pain to belong here.</p>
</div>
<nav class="story-reading-next" aria-label="Continue the story">
<a href="/journal/">Read the Blog</a>
<a href="/GhostHeart_Angel.html">GhostHeart and His Angel</a>
</nav>
<aside class="story-reading-help" aria-labelledby="story-help-title"><h2 id="story-help-title">Help &amp; Resources</h2><p>Find U.S. organizations offering help with mental health, safety, housing and other practical needs.</p><a class="story-reading-help-link" href="/GhostHeart_Resources.html">Find support resources</a><p class="story-reading-boundary">GhostHeart shares resources; it does not provide crisis or professional services.</p></aside>
<p class="story-reading-live"><strong>Next Sunday Live:</strong> <a href="/live/index.html">The Awakening Welcome</a> (working title), <time datetime="2026-10-11T10:00:00-05:00">October 11 at 10:00 a.m. Central</time>. Viewing link and platform are pending.</p>
<aside class="story-reading-follow" aria-labelledby="story-follow-title"><div><h2 id="story-follow-title">Stay Connected</h2><p>New music, stories and updates from GhostHeart.</p></div><a class="story-reading-follow-link" href="/index.html#join-the-signal">Keep Me Updated</a></aside>
</div>'''
write('GhostHeart_Story.html', shell('GhostHeart’s Awakening', 'Survival matters. So does what a person chooses to carry forward.', '/GhostHeart_Story.html', story_body, '/assets/story/ghostheart-awakening-banner.png'))

first = POSTS[0]
public_article_names = {f"{post['slug']}.html" for post in POSTS} | {'how-we-got-here-archive.html'}
for existing_article in (ROOT / 'journal').glob('*.html'):
    if existing_article.name != 'index.html' and existing_article.name not in public_article_names:
        existing_article.unlink()

blog_posts = [post for post in POSTS if post['slug'] != 'how-we-got-here']
blog_first = blog_posts[0]
feature = f'''<article class="journal-feature">{art(blog_first, True)}<div><p class="ghx-kicker">From the blog</p>{meta(blog_first)}
<h2><a href="{post_path(blog_first)}">{escape(blog_first['title'])}</a></h2><p>{escape(blog_first['summary'])}</p>
<a class="journal-link" href="{post_path(blog_first)}">Read the entry</a></div></article>'''
entries = ''.join(f'''<article class="journal-entry"><span class="journal-number" aria-hidden="true">{i:02}</span><div>{meta(post)}
<h2><a href="{post_path(post)}">{escape(post['title'])}</a></h2><p>{escape(post['summary'])}</p>
<a class="journal-link" href="{post_path(post)}">Read the entry</a></div>{art(post, True)}</article>''' for i, post in enumerate(blog_posts[1:], 2))
body = f'''<div class="ghx-wrap"><header class="journal-hero"><p class="ghx-kicker">GhostHeart / Blog</p>
<h1>Words from<br/>the heart.</h1><p class="ghx-lead">Dated reflections on approved songs, films, and the work around them. New writing will appear here when it is ready.</p>
<div class="ghx-actions"><a href="#entries">Read the blog</a><a href="/GhostHeart_Story.html">Enter My World</a></div></header>
<div class="journal-highlights"><section class="journal-highlight" aria-labelledby="quote-title"><p class="ghx-kicker">Quote of the day</p><h2 id="quote-title">A line to carry.</h2>
<blockquote data-daily-quote>{escape(QUOTES[0])}</blockquote><p class="highlight-source">GhostHeart | <a href="/GhostHeart_Quotes.html">Quote Vault</a></p></section>
<section class="journal-highlight journal-live" aria-labelledby="live-title"><p class="ghx-kicker">Next Sunday Live</p><h2 id="live-title">{escape(LIVE['title'])}</h2>
<p class="highlight-working">Planned Live; platform and viewing link pending</p><p><time datetime="{LIVE['starts_at']}">Sunday, October 11, 2026 at 10:00 a.m. Central</time></p>
<p>Viewing link and platform will be added when confirmed.</p><a href="/live/index.html">Readings &amp; Live details</a></section></div>
<section aria-label="Dated blog entries" id="entries">{feature}<div class="journal-list">{entries}</div></section>
<aside class="journal-follow" aria-labelledby="archive-title"><p class="ghx-kicker">Earlier public introduction</p><h2 id="archive-title">How We Got Here</h2><p>The original introduction remains available in the archive. The current reading path begins at Enter My World.</p><div class="ghx-actions"><a class="primary" href="/GhostHeart_Story.html">Enter My World</a><a class="secondary" href="/journal/how-we-got-here-archive.html">Read the archived introduction</a></div></aside></div>'''
write('journal/index.html', shell('Blog', 'Dated reflections on approved GhostHeart songs, films, and creative work.', '/journal/', body, blog_first['image']))
daily_js = '''(() => {
  const target = document.querySelector('[data-daily-quote]');
  if (!target) return;
  const quotes = __QUOTES__;
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Chicago', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(new Date()).filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
  const day = Math.floor(Date.UTC(parts.year, parts.month - 1, parts.day) / 86400000);
  target.textContent = quotes[((day % quotes.length) + quotes.length) % quotes.length];
})();
'''.replace('__QUOTES__', json.dumps(QUOTES, ensure_ascii=False))
write('assets/journal/daily-quote.js', daily_js)

for post in POSTS:
    if post['slug'] == 'how-we-got-here':
        # Preserve the public introduction URL while the Story page becomes its reading destination.
        write('journal/how-we-got-here.html', '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Enter My World | GhostHeart</title><meta name="description" content="Continue to the current public Story reading, Enter My World."/>
<link rel="canonical" href="https://www.myghostheart.com/GhostHeart_Story.html"/>
<meta http-equiv="refresh" content="0; url=/GhostHeart_Story.html"/></head>
<body><main><h1>Enter My World</h1><p>Continue to <a href="/GhostHeart_Story.html">the current Story reading</a>. The <a href="/journal/how-we-got-here-archive.html">earlier introduction</a> is preserved in the Journal archive.</p></main></body></html>
''')
    links = ''.join(f'<a class="{"secondary" if i else "primary"}" href="{escape(link["url"], quote=True)}">{escape(link["label"])}</a>' for i, link in enumerate(post['links']))
    related = ('/albums/index.html#youre-not-god' if post['slug'] == 'youre-not-god' else '/albums/index.html#awakening')
    related_links = f'<a class="secondary" href="/GhostHeart_Story.html">Enter My World</a><a class="secondary" href="{related}">Listen to related songs</a>'
    paragraphs = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in post['paragraphs'])
    body = f'''<div class="ghx-wrap"><article class="journal-article"><a class="journal-back journal-link" href="/journal/">GhostHeart Blog</a>
<header>{meta(post)}<h1>{escape(post['title'])}</h1><p class="journal-deck">{escape(post['summary'])}</p></header>
{art(post)}<div class="journal-prose">{paragraphs}</div><section class="journal-continue" aria-label="Related reading and music">
<h2>Continue with the story and music.</h2><div class="ghx-actions">{links}{related_links}</div></section>
<nav class="journal-next ghx-actions" aria-label="More from GhostHeart"><a href="/journal/">All blog entries</a><a href="/GhostHeart_Resources.html">Help &amp; Resources</a></nav>
<section class="journal-comments" aria-labelledby="comments-title" data-comment-thread="journal:{escape(post['slug'], quote=True)}"><h2 id="comments-title">Conversation</h2><p>Comments are not open yet. Please keep personal details out of public comments; for urgent support, use <a href="/GhostHeart_Resources.html">Help &amp; Resources</a>.</p></section>
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

latest_link = ''  # The archived introduction is not featured on home.
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
namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', namespace)
root = ET.fromstring(sitemap)
for url in list(root):
    loc = url.find(f'{{{namespace}}}loc')
    if loc is not None and (loc.text or '').startswith(BASE + '/journal/'):
        root.remove(url)
ET.indent(root, space='  ')
sitemap = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding='unicode')
assert '</urlset>' in sitemap
sitemap = sitemap.replace('</urlset>', sitemap_block + '\n</urlset>')
write('sitemap.xml', sitemap)

print(
    f'Built journal index, {len(POSTS)} public entries, homepage Journal markers, RSS feed, and sitemap.'
)
