#!/usr/bin/env python3
"""Wake the Heart site (prototype v3, confirmed by Dom on Nov 6, 2026 for Sunday night, Nov 8).

Source: .github/wake-v3/prototype.html, the one-file prototype Dom reviewed
(claude.ai artifact UtyTXyaM1XKxFpyF3qgGry, version 15). Each of its views becomes a real page
at the address the live site already uses, plus one new page, /wake-the-heart/.
Dom's picks (Nov 6): Blog = "The Notebook" (new idea), Vault = "The Heart Dial" (new idea).

The prototype's pretend forms are wired to the real ones:
  * Silver Thread signups post to the same Mailchimp list as the current homepage form.
  * "Tell me what you need" uses assets/help/help-form.js (Supabase office order).
  * "A song from your story" uses assets/help/order-form.js (Supabase free-preview song order).
This runs last in build_site.py, so it replaces what the older steps wrote at these addresses.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / '.github/wake-v3/prototype.html.src'
OUT_ASSETS = ROOT / 'assets/wake-v3'
SITE = 'https://www.myghostheart.com'
MAILCHIMP = ('https://myghostheart.us22.list-manage.com/subscribe/post'
             '?u=a7ab330423f3b936c48b8d8ba&id=880e8056a6&f_id=00bec2e1f0')
HONEYPOT = 'b_a7ab330423f3b936c48b8d8ba_880e8056a6'

# view -> (file, public path, title, description)
PAGES = {
    'home': ('index.html', '/', 'GhostHeart | The Heart Wakes',
             'GhostHeart: Wake the Heart, fourteen weeks of new songs from the album The Heart Wakes, Nov 9 to Feb 8. Music, films, Sunday Lives and stories.'),
    'wake': ('wake-the-heart/index.html', '/wake-the-heart/', 'Wake the Heart | GhostHeart',
             'Wake the Heart: fourteen weeks of songs about the things we carry, opening one Sunday night at a time, Nov 9 to Feb 8.'),
    'music': ('music/index.html', '/music/', 'Music | GhostHeart',
              'The Heart Wakes, the new GhostHeart album, opening one week at a time, plus GhostHeart’s Awakening and You’re Not God.'),
    'films': ('GhostHeart_Videos.html', '/GhostHeart_Videos.html', 'Films | GhostHeart',
              'GhostHeart music videos and Shorts.'),
    'lives': ('live/index.html', '/live/', 'Sunday Lives | GhostHeart',
              'GhostHeart goes Live every Sunday at 12:00 PM Central on TikTok, @ghosthearted1.'),
    'story': ('GhostHeart_Story.html', '/GhostHeart_Story.html', 'Enter My World | GhostHeart',
              'Enter GhostHeart’s world: the story behind the songs.'),
    'blog': ('journal/index.html', '/journal/', 'Behind the Songs | GhostHeart',
             'The GhostHeart Notebook: passages, song notes and announcements behind the songs.'),
    'vault': ('vault/index.html', '/vault/', 'How’s Your Heart? | GhostHeart Vault',
              'The Heart Dial: tell GhostHeart how you feel and get one song, film, line or reading from the Vault, and why it fits.'),
    'work': ('here-to-help/index.html', '/here-to-help/', 'How Can I Help? | GhostHeart',
             'Help with a document, some writing, a presentation or a spreadsheet, plus custom songs from your story.'),
    'projects': ('GhostHeart_Projects.html', '/GhostHeart_Projects.html', 'Projects | GhostHeart',
                 'GhostHeart Studios projects: a clearer choice, a private place to reflect, or a way to create.'),
    'connect': ('follow/index.html', '/follow/', 'Stay Connected | GhostHeart',
                'Every GhostHeart channel in one place, plus the Silver Thread email list.'),
    'support': ('GhostHeart_Resources.html', '/GhostHeart_Resources.html', 'Find Support | GhostHeart',
                'Free, confidential help: crisis lines, safety, mental health, housing, legal aid, LGBTQ+ and veterans support.'),
    'privacy': ('GhostHeart_Privacy.html', '/GhostHeart_Privacy.html', 'Privacy | GhostHeart',
                'How GhostHeart handles your email and the information you send.'),
}
EXTRA_CSS = '''
/* Real forms (added by apply_wake_v3.py) */
.help-fields{border:0;margin:0;padding:0;min-width:0;display:contents}
.err{color:#F4483C}
[data-help-status] strong,[data-order-status] strong{display:block}
'''
HREF = {view: path for view, (_, path, _, _) in PAGES.items()}


def media(text: str) -> str:
    text = re.sub(r'(["\'(])audio/old/', r'\1/assets/music/preview/', text)
    text = re.sub(r'(["\'(])audio/', r'\1/assets/wake-v3/audio/', text)
    return re.sub(r'(["\'(])img/', r'\1/assets/wake-v3/img/', text)


def link(href: str) -> str:
    if not href.startswith('#'):
        return href
    h = href[1:]
    if h == 'thread':
        return '/#thread'
    if h.startswith('blog/'):
        return '/journal/#e-' + h[5:]
    if h in HREF:
        return HREF[h]
    return href  # same-page anchor


def js_links(text: str) -> str:
    # Hash links inside the script data (For-you picks, locked weeks card).
    def sub(m):
        return m.group(1) + link(m.group(2)) + m.group(1)
    return re.sub(r'(["\'])(#(?:thread|blog/[\w-]+|' + '|'.join(HREF) + r'))\1', sub, text)


def main() -> None:
    raw = SRC.read_text(encoding='utf-8')
    css = re.search(r'<style>(.*?)</style>', raw, re.S).group(1)
    js = re.search(r'<script>(.*?)</script>', raw, re.S).group(1)
    OUT_ASSETS.mkdir(parents=True, exist_ok=True)
    # Inline SVG textures become files (the site check reads every url() in CSS as a file).
    textures = {}
    def texture(m):
        svg = m.group(1).replace('%23', '#')
        name = 'texture-%d.svg' % (len(textures) + 1) if svg not in textures else textures[svg]
        textures.setdefault(svg, name)
        (OUT_ASSETS / 'img' / textures[svg]).write_text(svg + '\n', encoding='utf-8')
        return 'url("/assets/wake-v3/img/%s")' % textures[svg]
    css = re.sub(r'url\("data:image/svg\+xml;utf8,([^"]*)"\)', texture, css)
    (OUT_ASSETS / 'site.css').write_text('/* Generated by .github/scripts/apply_wake_v3.py from .github/wake-v3/prototype.html */\n' + media(css).replace('.proto{', '.proto-unused{') + EXTRA_CSS, encoding='utf-8')
    (OUT_ASSETS / 'site.js').write_text(build_js(js), encoding='utf-8')

    soup = BeautifulSoup(raw, 'html.parser')
    header = soup.select_one('header.top')
    footer = soup.find('footer')
    views = {v['data-view']: v for v in soup.select('div.view')}
    assert set(views) == set(PAGES), sorted(views)
    for view, (file, path, title, desc) in PAGES.items():
        body = views[view]
        adjust_view(view, body)
        page = render(view, path, title, desc, header, body, footer)
        out = ROOT / file
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding='utf-8')
    sitemap()
    print('Wake the Heart site written: ' + ', '.join(p[0] for p in PAGES.values()))


def build_js(js: str) -> str:
    js = js_links(media(js))
    # Each page is its own address now: drop the one-file hash router, keep the menu button.
    start = js.index('  var NAMES=')
    end = js.index('  window.addEventListener("hashchange",route);route();')
    js = js[:start] + js[end + len('  window.addEventListener("hashchange",route);route();'):]
    # The Lives list only exists on /live/.
    js = js.replace('  L.forEach(function(x){if(x<T)return;', '  if(lv)L.forEach(function(x){if(x<T)return;')
    # Silver Thread forms really post to Mailchimp now; never fake a success.
    old_thread = 'document.querySelectorAll(".js-thread").forEach(function(form){form.addEventListener("submit",function(e){e.preventDefault();mine++;store("gh-threads",mine);var p=person(base+mine-1,true);p.born=performance.now()/1000;people.push(p);setCount();form.querySelector(".ok").hidden=false})});'
    assert old_thread in js
    js = js.replace(old_thread, '')
    js = js.replace('var mine=+(store("gh-threads")||0);', 'var mine=0;')
    old_order = 'document.querySelectorAll("form.js-order").forEach(function(f){f.addEventListener("submit",function(e){e.preventDefault();f.querySelector(".ok").hidden=false})});'
    assert old_order in js
    js = js.replace(old_order, '')
    extra = '''
  // Silver Thread: the browser posts straight to Mailchimp, which confirms the signup itself.
  document.querySelectorAll("form.js-thread").forEach(function(form){form.addEventListener("submit",function(){var s=form.querySelector(".ok");if(s){s.textContent="Opening Mailchimp to finish joining.";s.hidden=false}})});
  // Notebook deep links (/journal/#e-papa) open that entry.
  (function(){var id=(location.hash||"").slice(1);if(!/^e-[\\w-]+$/.test(id))return;var el=document.getElementById(id);if(!el)return;var dd=el.querySelector("details");if(dd)dd.open=true;el.scrollIntoView()})();
  var mb=document.getElementById("menu-btn"),menu=document.getElementById("menu");
  if(mb&&menu)mb.addEventListener("click",function(){var o=menu.classList.toggle("open");mb.setAttribute("aria-expanded",o)});
'''
    js = js.replace('  var mb=document.getElementById("menu-btn"),menu=document.getElementById("menu");\n  mb.addEventListener("click",function(){var o=menu.classList.toggle("open");mb.setAttribute("aria-expanded",o)});\n', extra)
    assert 'Notebook deep links' in js
    assert 'route()' not in js and 'hashchange' not in js
    return '// Generated by .github/scripts/apply_wake_v3.py from .github/wake-v3/prototype.html\n' + js.strip() + '\n'


def tag(soup, name, attrs=None, text=None):
    el = soup.new_tag(name, attrs=attrs or {})
    if text is not None:
        el.string = text
    return el


def thread_form(form) -> None:
    """Prototype Silver Thread form -> the real Mailchimp form (same list as today's homepage)."""
    soup = form
    while soup.parent is not None:
        soup = soup.parent
    form.attrs.pop('novalidate', None)
    form['action'] = MAILCHIMP
    form['method'] = 'post'
    inp = form.find('input', attrs={'type': 'email'})
    inp['name'] = 'EMAIL'
    inp['required'] = ''
    inp['maxlength'] = '254'
    inp['inputmode'] = 'email'
    form.find('button')['name'] = 'subscribe'
    trap = tag(soup, 'div', {'aria-hidden': 'true', 'class': 'mc-trap',
                             'style': 'position:absolute;left:-5000px'})
    trap.append(tag(soup, 'input', {'type': 'text', 'name': HONEYPOT, 'tabindex': '-1', 'autocomplete': 'off', 'value': ''}))
    inp.insert_after(trap)
    ok = form.find(class_='ok')
    if ok:
        ok.string = ''
        ok['role'] = 'status'
    note = form.find(class_='note')
    if note:
        note.append(' Mailchimp handles signup. ')
        a = tag(soup, 'a', {'href': '/GhostHeart_Privacy.html'}, 'Privacy')
        note.append(a)


def work_forms(view) -> None:
    soup = view
    while soup.parent is not None:
        soup = soup.parent
    wrap = view.find(id='help-form')
    wrap['id'] = 'ask'
    # --- "Tell me what you need" -> assets/help/help-form.js ---
    form = wrap.find('form')
    form['id'] = 'help-form'
    form['class'] = [c for c in form['class'] if c != 'js-order']
    form['aria-label'] = 'Tell me what you need'
    form.find(id='h-name')['name'] = 'name'
    form.find(id='h-email')['name'] = 'email'
    sel = form.find(id='h-kind')
    sel['name'] = 'service'
    sel['required'] = ''
    # The order database takes these job names (.github/orders/supabase/story-orders.review.sql);
    # the visitor's own choice is also written at the top of the request (help-form.js).
    values = {'Sort out a document': 'word', 'Find the right words': 'writing',
              'Put a presentation together': 'powerpoint', 'Organize the details': 'data_entry',
              'Something else': 'word'}
    for opt in sel.find_all('option'):
        if opt.get_text() in values:
            opt['value'] = values[opt.get_text()]
    form.find(id='h-about')['name'] = 'details'
    form.find(id='h-about')['required'] = ''
    form.find(id='h-when')['name'] = 'when'
    fields = tag(soup, 'fieldset', {'data-help-fields': '', 'disabled': '', 'class': 'help-fields'})
    for child in list(form.children):
        if getattr(child, 'name', None) in ('label', 'button'):
            fields.append(child.extract())
    head = form.find('p', class_='mono')
    head.insert_after(fields)
    btn = fields.find('button')
    btn['data-help-submit'] = ''
    hp = tag(soup, 'label', {'class': 'sr', 'aria-hidden': 'true'}, 'Leave this empty')
    hp.append(tag(soup, 'input', {'type': 'text', 'name': 'website', 'tabindex': '-1', 'autocomplete': 'off'}))
    fields.insert(0, hp)
    err = tag(soup, 'p', {'class': 'note err', 'data-help-error': '', 'hidden': '', 'role': 'alert'})
    btn.insert_before(err)
    ok = form.find(class_='ok')
    status = tag(soup, 'div', {'class': 'ok', 'data-help-status': '', 'hidden': '', 'role': 'status', 'aria-live': 'polite'})
    status.append(tag(soup, 'strong', {'data-help-status-title': ''}))
    status.append(tag(soup, 'span', {'data-help-status-text': ''}))
    ok.replace_with(status)
    # --- "A song from your story" -> assets/help/order-form.js (free preview) ---
    song = view.find(class_='song-opt')
    sform = song.find('form')
    sform['id'] = 'story-form'
    sform['class'] = [c for c in sform['class'] if c != 'js-order']
    sform['aria-label'] = 'Tell me your story for a free song preview'
    names = {'o-who': 'for_whom', 'o-occ': 'occasion', 'o-story': 'memories', 'o-email': 'email'}
    for i, n in names.items():
        sform.find(id=i)['name'] = n
    sform.find(id='o-who')['required'] = ''
    sform.find(id='o-story')['required'] = ''
    sform.find(id='o-email')['required'] = ''
    sfields = tag(soup, 'fieldset', {'data-order-fields': '', 'disabled': '', 'class': 'help-fields'})
    sfields.append(tag(soup, 'input', {'type': 'radio', 'name': 'kind', 'value': 'try', 'checked': '', 'hidden': ''}))
    hp2 = tag(soup, 'label', {'class': 'sr', 'aria-hidden': 'true'}, 'Leave this empty')
    hp2.append(tag(soup, 'input', {'type': 'text', 'name': 'website', 'tabindex': '-1', 'autocomplete': 'off'}))
    sfields.append(hp2)
    for child in list(sform.children):
        if getattr(child, 'name', None) in ('label', 'button'):
            sfields.append(child.extract())
    sform.insert(0, sfields)
    sbtn = sfields.find('button')
    sbtn['data-order-submit'] = ''
    sbtn.insert_before(tag(soup, 'p', {'class': 'note err', 'data-order-error': '', 'hidden': '', 'role': 'alert'}))
    sbtn.insert_after(tag(soup, 'p', {'class': 'note', 'data-order-fine': ''}, 'The free preview costs nothing and asks for no card.'))
    sform.find(class_='ok').decompose()
    # Status sits outside the folded section so a return from Stripe (?paid=1) is visible.
    st = tag(soup, 'div', {'class': 'ok', 'data-order-status': '', 'hidden': '', 'role': 'status', 'aria-live': 'polite'})
    st.append(tag(soup, 'strong', {'data-order-status-title': ''}))
    st.append(' ')
    st.append(tag(soup, 'span', {'data-order-status-text': ''}))
    song.find('details').insert_before(st)


def adjust_view(view: str, body) -> None:
    del body['hidden']
    for form in body.select('form.js-thread'):
        thread_form(form)
    if view == 'music':
        h = body.find('h2', class_='giant')
        h.name = 'h1'
    if view == 'work':
        work_forms(body)
    if view in ('blog', 'vault'):
        # Dom's pick, Nov 6: the new idea for both pages.
        body.select_one('.alt-toggle').decompose()
        body.select_one('.alt-a').decompose()
        b = body.select_one('.alt-b')
        del b['hidden']
        # The "New idea · ..." kicker was a review label for Dom; the live page names the place instead.
        kicker = next(p for p in b.select('p.mono') if p.get_text().startswith('New idea · '))
        kicker.string = {'blog': 'GhostHeart / Blog', 'vault': 'GhostHeart / The Vault'}[view]
    if view == 'blog':
        ids = [d['id'] for d in BeautifulSoup(SRC.read_text(encoding='utf-8'), 'html.parser').select('.view[data-view=blog] .alt-a details.entry')]
        items = body.select('.nb-item')
        assert len(ids) == len(items), (len(ids), len(items))
        for i, li in zip(ids, items):
            li['id'] = i
    anchors(view, body)
    for a in body.find_all('a', href=True):
        a['href'] = link(a['href'])
    assert len(body.find_all('h1')) == 1, (view, len(body.find_all('h1')))


def slug(text: str) -> str:
    text = text.lower().replace('’', '').replace("'", '')
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')


def anchors(view: str, body) -> None:
    """Keep the deep links that older pages (Awakening, passages, journal entries) still use."""
    if view == 'home':
        body.select_one('section.hero')['id'] = 'home'
        body.select_one('#featured-home').parent.parent['id'] = 'watch'
        body.select_one('#thread .thread-box')['id'] = 'join-the-signal'
    if view == 'music':
        body.select_one('.wrap.album').parent['id'] = 'listen'
        special = {'papa-didnt-raise-no-fool': 'papa-didnt-raise-a-fool'}
        for li in body.select('.tracks li'):
            s = slug(li.span.get_text())
            li['id'] = 'song-' + special.get(s, s)
    if view == 'films':
        special = {'human-too': 'human-too-remake', 'the-dad-i-never-had': 'the-dad'}
        for art in body.select('article.film'):
            s = slug(art.h3.get_text())
            art['id'] = 'film-' + special.get(s, s)
    if view == 'story':
        body.select_one('article.read')['id'] = 'behind-the-scars'
    if view == 'projects':
        h = body.find('h2', string='Axiomara.')
        h.find_parent(['article', 'div'])['id'] = 'axiomara'
    if view == 'connect':
        body.select_one('a[href="#thread"]').parent['id'] = 'email-signup-title'


def render(view, path, title, desc, header, body, footer) -> str:
    head_html = BeautifulSoup(str(header), 'html.parser')
    for a in head_html.find_all('a', href=True):
        orig = a['href']
        a['href'] = link(orig)
        if orig == '#' + view:
            a['aria-current'] = 'page'
    foot = BeautifulSoup(str(footer), 'html.parser')
    for a in foot.find_all('a', href=True):
        a['href'] = link(a['href'])
    scripts = ['/assets/wake-v3/site.js']
    if view == 'work':
        scripts = ['/assets/help/orders-config.js', '/assets/help/order-form.js', '/assets/help/help-form.js'] + scripts
    url = SITE + path
    esc = lambda t: t.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
    out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="GhostHeart">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/story/ghostheart-share-1200x630.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#050505">
<meta name="p:domain_verify" content="427845c023131887ec264df45999badc">
<link rel="icon" href="/favicon.ico">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Bebas+Neue&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=Space+Grotesk:wght@400;500;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/wake-v3/site.css">
</head>
<body data-page="{view}">
{head_html}
<main id="main">
{body}
</main>
{foot}
''' + ''.join(f'<script src="{s}"></script>\n' for s in scripts) + '</body>\n</html>\n'
    return media(out)


def sitemap() -> None:
    p = ROOT / 'sitemap.xml'
    s = p.read_text(encoding='utf-8')
    loc = f'{SITE}/wake-the-heart/'
    if loc not in s:
        s = s.replace('</urlset>', f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>2026-11-08</lastmod>\n  </url>\n</urlset>')
        p.write_text(s, encoding='utf-8')


main()
