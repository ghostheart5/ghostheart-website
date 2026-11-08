#!/usr/bin/env python3
"""Wake the Heart site (prototype v3, confirmed by Dom Nov 6 2026): static checks after the full build."""
from pathlib import Path
from urllib.parse import urlsplit
import re

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
MAILCHIMP = ('https://myghostheart.us22.list-manage.com/subscribe/post'
             '?u=a7ab330423f3b936c48b8d8ba&id=880e8056a6&f_id=00bec2e1f0')
PAGES = {
    'index.html': '/', 'wake-the-heart/index.html': '/wake-the-heart/', 'music/index.html': '/music/',
    'GhostHeart_Videos.html': '/GhostHeart_Videos.html', 'live/index.html': '/live/',
    'GhostHeart_Story.html': '/GhostHeart_Story.html', 'journal/index.html': '/journal/',
    'vault/index.html': '/vault/', 'here-to-help/index.html': '/here-to-help/',
    'GhostHeart_Projects.html': '/GhostHeart_Projects.html', 'follow/index.html': '/follow/',
    'GhostHeart_Resources.html': '/GhostHeart_Resources.html', 'GhostHeart_Privacy.html': '/GhostHeart_Privacy.html',
}
NAV = ['Home', 'Wake the Heart', 'Music', 'Enter My World', 'Lives', 'Work with GhostHeart', 'Projects',
       'Merch ↗', 'Stay Connected', 'Find Support']


def page(relative):
    return BeautifulSoup((ROOT / relative).read_text(encoding='utf-8'), 'html.parser')


site_js = (ROOT / 'assets/wake-v3/site.js').read_text(encoding='utf-8')
site_css = (ROOT / 'assets/wake-v3/site.css').read_text(encoding='utf-8')
for relative, path in PAGES.items():
    doc = page(relative)
    assert doc.select_one('link[href="/assets/wake-v3/site.css"]') and doc.select_one('script[src="/assets/wake-v3/site.js"]'), relative
    assert doc.select_one('link[rel=canonical]')['href'] == 'https://www.myghostheart.com' + path, relative
    assert len(doc.select('h1')) == 1, relative
    nav = doc.select('header.top nav#menu a')
    assert [a.get_text(' ', strip=True) for a in nav] == NAV, (relative, [a.get_text() for a in nav])
    current = [a['href'] for a in nav if a.get('aria-current') == 'page']
    in_menu = path in [a['href'] for a in nav]
    assert current == ([path] if in_menu else []), (relative, current)
    # Dom, Nov 6: no link may send people to the old site. Every local link stays on these pages or /assets/.
    for el in doc.select('[href], [src]'):
        url = el.get('href') or el.get('src')
        if url.startswith(('https://', 'mailto:', 'tel:', 'sms:', '#')):
            continue
        target = urlsplit(url).path
        assert target in PAGES.values() or target.startswith('/assets/') or target in ('/favicon.ico', '/site.webmanifest'), (relative, url)
        if target.startswith('/assets/'):
            assert (ROOT / target.lstrip('/')).is_file(), (relative, url)
    text = doc.get_text(' ', strip=True)
    # Dom's rules: no "signal" except his email, no prototype notes, Watch Me Anyway is never "bonus", no AI labels.
    assert 'signal' not in text.lower().replace('signal@myghostheart.com', ''), relative
    assert 'prototype' not in text.lower(), relative
    assert 'bonus' not in text.lower() and 'new idea' not in text.lower(), relative
    assert not re.search(r'\bAI[- ](generated|made)\b|made with AI', text, re.I), relative
    assert not doc.select('.alt-toggle, .alt-a, .proto'), relative
    # Every Silver Thread email box is the real Mailchimp signup (same list as the old homepage form).
    for form in doc.select('form.js-thread'):
        assert form['action'] == MAILCHIMP and form['method'] == 'post', relative
        assert form.select_one('input[type=email][name=EMAIL][required]'), relative
        assert form.select_one('input[name=b_a7ab330423f3b936c48b8d8ba_880e8056a6][tabindex="-1"]'), relative
    forms = doc.select('form')
    if relative == 'here-to-help/index.html':
        assert sorted(f.get('id') for f in forms) == ['help-form', 'story-form']
    elif relative == 'vault/index.html':
        assert not forms
    else:
        assert all('js-thread' in f.get('class', []) for f in forms), relative
for word in ('prototype', 'Prototype'):
    assert word not in site_js.split('\n', 1)[1], word

home = page('index.html')
assert [f.get('id') for f in home.select('form')] == [None] and home.select_one('#thread form.js-thread')
assert home.select_one('#featured-home') and home.select_one('[data-daily-quote]') and home.select_one('canvas#living')
assert home.select_one('#join-the-signal') and home.select_one('#home')  # old links still land on the home page

# Dom, Nov 8 2026 (later): "release the entire site and 1st weeks songs ... no other song should be listed".
# The confirmed prototype's campaign pieces are on; only The Heart Wakes songs are listed (apply_week1_songs_only.py).
wake = page('wake-the-heart/index.html')
assert not wake.select_one('meta[http-equiv=refresh]') and wake.select_one('h1'), 'wake-the-heart page is live'
assert 'href="/wake-the-heart/"' in (ROOT / 'index.html').read_text(encoding='utf-8')
assert '/wake-the-heart/' in (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
moved = page('journal/wake-the-heart-week.html')  # old post about the retired album
assert moved.select_one('meta[http-equiv=refresh]')['content'] == '0; url=/journal/'
assert moved.select_one('meta[name=robots]')['content'] == 'noindex'
assert 'wake-the-heart-week' not in (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
music_raw = (ROOT / 'music/index.html').read_text(encoding='utf-8')
assert 'Where it started' not in music_raw and 'class="tplay"' not in music_raw and 'id="album-songs"' in music_raw
for relative in PAGES:
    raw = (ROOT / relative).read_text(encoding='utf-8')
    assert 'Awakening' not in raw, relative
weeks = re.findall(r'\{nm:"([^"]+)",up:"(\d{4}-\d\d-\d\d)"', site_js)
assert len(weeks) == 14 and weeks[0] == ('To Those Who Served', '2026-11-08') and weeks[-1][0] == 'Watch Me Anyway', weeks
for mp3 in re.findall(r'"/assets/wake-v3/audio/([^"]+\.mp3)"', site_js):
    assert (ROOT / 'assets/wake-v3/audio' / mp3).stat().st_size > 1_000_000, mp3

music = page('music/index.html')
# Dom, Nov 8 2026: only The Heart Wakes songs are listed on Music (filled in by site.js as each week opens).
assert not music.select('.tracks li[id^="song-"]') and music.select_one('ul#album-songs')

films = page('GhostHeart_Videos.html')
assert len(films.select('article.film[id^="film-"]')) == 12

live = page('live/index.html')
assert live.select_one('#lives') and live.select_one('form.js-thread')
assert live.select_one('a[href="https://www.tiktok.com/@ghosthearted1"]')

blog = page('journal/index.html')
items = blog.select('ol.nb > li.nb-item[id^="e-"]')
assert len(items) == 7 and all(i.select_one('details .entry-body p') for i in items)
assert {i['data-typ'] for i in items} <= {'passage', 'song', 'news'}

vault = page('vault/index.html')
assert len(vault.select('.dial-ring button.dial-m[data-m]')) == 6 and vault.select_one('.dial-out[aria-live]')
picks = re.findall(r'"href": "([^"]+)"', site_js)
assert picks and all(h.startswith('https://') or urlsplit(h).path in PAGES.values() for h in picks), picks

work = page('here-to-help/index.html')
for src in ('/assets/help/orders-config.js', '/assets/help/order-form.js', '/assets/help/help-form.js'):
    assert work.select_one(f'script[src="{src}"]'), src
help_form = work.select_one('form#help-form')
assert help_form.select_one('fieldset[data-help-fields][disabled]') and help_form.select_one('[data-help-submit]')
for name in ('name', 'email', 'service', 'details', 'when', 'website'):
    assert help_form.select_one(f'[name={name}]'), name
allowed = {'data_entry', 'word', 'resume', 'powerpoint', 'excel', 'writing', 'proofreading'}  # story-orders.review.sql
assert {o['value'] for o in help_form.select('select[name=service] option') if o['value']} <= allowed
story = work.select_one('form#story-form')
assert story.select_one('fieldset[data-order-fields][disabled] input[name=kind][value=try][checked]')
for name in ('for_whom', 'occasion', 'memories', 'email', 'website'):
    assert story.select_one(f'[name={name}]'), name
assert work.select_one('[data-order-status] [data-order-status-title]') and not work.select_one('details [data-order-status]')
assert work.select_one('a[href="mailto:signal@myghostheart.com"]')
# Same limits as the order database (story-orders.review.sql), so a long story is never silently refused.
limits = {'#h-name': 100, '#h-email': 254, '#h-about': 3600, '#h-when': 100, '#o-who': 200, '#o-occ': 200, '#o-story': 4000, '#o-email': 254}
for sel, n in limits.items():
    assert work.select_one(sel)['maxlength'] == str(n), sel
assert len('Help with: Put a presentation together\nName: \nNeeded by: \n\n') + 100 + 100 + 3600 <= 4000

support = page('GhostHeart_Resources.html')
assert len(support.select('.res-grid .resource')) == 16
assert support.select_one('a[href="tel:988"]')
assert 'url("data:' not in site_css
print('PASS site: 12 pages, campaign page on, one menu, no old-site links, real Mailchimp and order forms, '
      '14 album weeks, only The Heart Wakes songs listed, 12 films, 7 Notebook entries, Heart Dial, 16 resources')
