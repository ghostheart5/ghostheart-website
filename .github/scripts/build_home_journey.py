#!/usr/bin/env python3
"""Refine only the approved homepage journey after the existing site build."""
from pathlib import Path
from html import escape
import json
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
INTRO = 'GhostHeart is the fictional reflection of one man’s real life—told through music, stories, and a mission to help people feel less alone.'
CONNECTION = json.loads((ROOT / '.github/content/connection.json').read_text(encoding='utf-8'))
EMAIL_PROMISE = CONNECTION['benefits']

def build():
    path = ROOT / 'index.html'
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    for label, media in [('mobile', '(max-width: 700px)'), ('desktop', '(min-width: 701px)')]:
        href = f'/assets/story/ghostheart-scars-rooftop-rain-{label}-v1.webp'
        if not soup.select_one(f'link[rel="preload"][href="{href}"]'):
            preload = soup.new_tag('link', attrs={
                'rel': 'preload', 'as': 'image', 'type': 'image/webp',
                'href': href, 'media': media, 'fetchpriority': 'high',
            })
            soup.head.append(preload)
    main = soup.select_one('main')
    hero = main.select_one('#home')
    hero.select_one('h1').clear()
    hero.select_one('h1').append(BeautifulSoup('Discover GhostHeart.<span>Become Part of the Change.</span>', 'html.parser'))
    hero.select_one('.canon-hero__line').string = INTRO
    note = hero.select_one('.canon-hero__note')
    note.string = 'Meet the man behind GhostHeart.'
    note['id'] = 'home-story-explanation'
    actions = hero.select_one('.ghx-actions')
    actions.clear()
    actions.append(BeautifulSoup('<a class="primary" href="/GhostHeart_Story.html" aria-describedby="home-story-explanation">Discover GhostHeart</a><a class="secondary" href="#join-the-signal">Follow the Story</a><a class="secondary" href="#mission-board">Be Part of the Mission</a>', 'html.parser'))
    manifest = json.loads((ROOT / '.github/content/music.json').read_text(encoding='utf-8'))
    cruel = manifest['groups'][0]['tracks'][0]
    assert cruel['title'] == 'Cruel' and cruel['youtube'] == 'https://www.youtube.com/watch?v=9sbFgjM_SDE'
    featured = BeautifulSoup(f'''<section class="home-feature ghx-wrap" id="latest" aria-labelledby="featured-title">
<p class="ghx-kicker">Featured song</p><h2 id="featured-title">Cruel.</h2><p>From GhostHeart’s Awakening.</p>
<p>Listen to the preview, or watch the full video.</p><audio controls preload="none" aria-label="Play Cruel preview"><source src="{escape(cruel['audio'], quote=True)}" type="audio/mpeg"/>Your browser does not support this audio player.</audio>
<div class="ghx-actions"><a class="primary" href="{escape(cruel['youtube'], quote=True)}" target="_blank" rel="noopener noreferrer">Watch full video</a><a class="secondary" href="/albums/#{cruel['id']}">Listen in Music</a><a class="secondary" href="#home-story">Read the life behind the music</a></div></section>''', 'html.parser').section
    story = BeautifulSoup('''<section class="home-story ghx-wrap" id="home-story" aria-labelledby="home-story-title"><p class="ghx-kicker">Enter My World</p><h2 id="home-story-title">Behind the Scars — The Awakening.</h2><p>The public beginning of the life behind GhostHeart.</p><div class="ghx-actions"><a class="primary" href="/GhostHeart_Story.html#behind-the-scars">Read Behind the Scars</a></div></section>''', 'html.parser').section
    signup = main.select_one('#join-the-signal')
    signup.select_one('h2').string = CONNECTION['heading']
    for previous in signup.select('.home-email-action, .connection-optional'):
        previous.decompose()
    signup.select_one('h2 + p').string = EMAIL_PROMISE
    signup.select_one('h2 + p').insert_after(BeautifulSoup(f'<p class="connection-optional">{escape(CONNECTION["optional"])}</p><div class="ghx-actions home-email-action"><a class="secondary" href="/follow/">{escape(CONNECTION["button"])}</a></div>', 'html.parser'))
    board = BeautifulSoup(f'''<section class="home-mission ghx-wrap" id="mission-board" aria-labelledby="mission-board-title">
<p class="ghx-kicker">Be Part of the Mission</p><h2 id="mission-board-title">One heart started the story. Yours can help change it.</h2>
<p>Music, stories, and the belief that nobody should feel invisible.</p>
<div class="mission-board-grid">
<article><h3>Latest chapter</h3><p>Behind the Scars — The Awakening.</p><a href="/GhostHeart_Story.html#behind-the-scars">Read the public beginning</a><a href="/journal/">Explore the stories behind the songs</a></article>
<article><h3>A small kindness</h3><p>A place to start: include someone in a conversation, listen without rushing, or offer a kind word.</p><a href="/GhostHeart_Resources.html">Find support resources</a></article>
<article><h3>Coming next</h3><p>{escape(CONNECTION['campaign'])}</p><p>Next Live: announcement pending.</p><a href="/live/">Lives &amp; Readings</a></article>
</div><p class="mission-participation">{escape(CONNECTION['participation'])}</p></section>''', 'html.parser').section
    discovery = main.select_one('.home-discovery')
    quote = main.select_one('[data-daily-quote]')
    if quote:
        quote_html = str(quote)
        for previous in discovery.select('.home-quote'):
            previous.decompose()
        discovery.select_one('#home-vault').append(BeautifulSoup('<aside class="home-quote" aria-label="From the Quote Vault">'+quote_html+'<a href="/GhostHeart_Quotes.html">Explore the Quote Vault</a></aside>', 'html.parser'))
    mission = main.select_one('.canon-oath')
    sections = [hero, featured, story, board, signup, discovery, mission]
    for section in sections:
        section.extract()
    main.clear()
    for section in sections:
        main.append(section)
    home_style = soup.select_one('link[href^="/assets/home/home-journey.css"]')
    if home_style:
        home_style['href'] = '/assets/home/home-journey.css?v=connection-v1'
    else:
        soup.select_one('link[href="/assets/shared/review-theme.css"]').insert_before(BeautifulSoup('<link rel="stylesheet" href="/assets/home/home-journey.css?v=connection-v1"/>', 'html.parser'))
    path.write_text(str(soup), encoding='utf-8', newline='\n')
    follow_path = ROOT / 'follow/index.html'
    follow = BeautifulSoup(follow_path.read_text(encoding='utf-8'), 'html.parser')
    heading = follow.select_one('#email-signup-title')
    heading.string = CONNECTION['heading']
    heading.find_next_sibling('p').string = EMAIL_PROMISE
    for description in follow.select('meta[name="description"], meta[property="og:description"]'):
        description['content'] = EMAIL_PROMISE
    follow_path.write_text(str(follow), encoding='utf-8', newline='\n')
    print('Applied approved homepage: introduction, Cruel, public story, optional connection; support and collection retained')

if __name__ == '__main__':
    build()
