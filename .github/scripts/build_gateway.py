#!/usr/bin/env python3
"""Build the approved GhostHeart public gateway. No email or social sends."""
from pathlib import Path
from html import escape
import json, re
import xml.etree.ElementTree as ET
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://www.myghostheart.com'
STAMP = '2026-09-28T20:25:00-05:00'
READ = '/journal/how-we-got-here.html'
CSS = '/assets/shared/gateway-v2.css'
JS = '/assets/shared/gateway-v2.js'
FORM = 'https://myghostheart.us22.list-manage.com/subscribe/post?u=a7ab330423f3b936c48b8d8ba&id=880e8056a6&f_id=00bec2e1f0'

def write(path, value):
    p = ROOT/path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(value, encoding='utf-8', newline='\n')

def link(url, text, cls='g-link'):
    return f'<a class="{cls}" href="{escape(url, quote=True)}">{text}</a>'

def header(owner='shared'):
    return f'''<header class="nav ghx-header gateway-header" data-nav-owner="{owner}"><div class="gateway-bar"><a class="ghx-brand" href="/index.html" aria-label="GhostHeart home">GHOST<span>HEART</span><i aria-hidden="true">✦</i></a><nav class="gateway-primary" aria-label="Main navigation"><a href="/GhostHeart_Story.html">Story</a><a href="/music/index.html">Music &amp; films</a><a href="/live/index.html">Sunday Live</a><a href="/GhostHeart_Version_Mission.html">Mission</a></nav><a class="gateway-follow" href="/follow/index.html">Follow GhostHeart</a><button class="menu-toggle ghx-menu-toggle" type="button" aria-expanded="false" aria-controls="gateway-menu">Explore <span aria-hidden="true">+</span></button></div><nav class="ghx-menu" id="gateway-menu" aria-label="Explore GhostHeart" hidden><div class="gateway-menu-grid"><div><h2>Enter the story</h2><a href="{READ}">Begin here</a><a href="/GhostHeart_Story.html">The story</a><a href="/GhostHeart_Angel.html">GhostHeart and His Angel</a><a href="/journal/index.html">From the journal</a></div><div><h2>Watch. Listen. Carry it.</h2><a href="/music/index.html">Music &amp; films</a><a href="/GhostHeart_Videos.html">All films</a><a href="/GhostHeart_Songs.html">Released recordings</a><a href="/GhostHeart_Quotes.html">Words to carry</a></div><div><h2>Stay connected</h2><a href="/live/index.html">Sunday readings</a><a href="/follow/index.html">Follow by email</a><a href="/GhostHeart_Projects.html#axiomara">Axiomara &amp; projects</a><a href="/GhostHeart_Resources.html">Find support</a></div></div></nav></header>'''

FOOTER = '''<footer class="ghx-footer gateway-footer"><div class="gateway-bar"><a class="ghx-brand" href="/index.html">GHOST<span>HEART</span></a><p>One story. Still unfolding.</p></div><nav aria-label="Official GhostHeart profiles"><a href="https://www.youtube.com/@GhostHeart-M95RTK" target="_blank" rel="noopener noreferrer">YouTube ↗</a><a href="https://www.tiktok.com/@ghosthearted1" target="_blank" rel="noopener noreferrer">TikTok ↗</a><a href="https://open.spotify.com/artist/68OskMXP10WmzJPexLzRc7" target="_blank" rel="noopener noreferrer">Spotify ↗</a><a href="https://www.instagram.com/ghostheart131517/" target="_blank" rel="noopener noreferrer">Instagram ↗</a></nav><div class="gateway-footnote"><span>© 2026 GhostHeart</span><a href="/GhostHeart_Privacy.html">Privacy</a><a href="/GhostHeart_Resources.html">Find support</a><a href="/follow/index.html">Follow by email</a></div></footer>'''

# Web derivatives only; retain the approved original artworks untouched.
artdir = ROOT/'assets/images/web-v2'; artdir.mkdir(parents=True, exist_ok=True)
source = ROOT/'assets/images/brand/ghostheart-world-wide.png'
SIZES = {}
with Image.open(source) as original:
    original = original.convert('RGB'); W,H = original.size
    for width in (640, 960, 1440):
        image = original.copy(); image.thumbnail((width, round(width*H/W)), Image.Resampling.LANCZOS)
        image.save(artdir/f'ghostheart-{width}.webp', 'WEBP', quality=80, method=6)
        SIZES[width] = image.width
ART = '/assets/images/web-v2/ghostheart-1440.webp'
ANGEL = '/assets/angel/gh-1829-approved-wingless.webp'
HAS_ANGEL = (ROOT/ANGEL.lstrip('/')).is_file()

def picture(cls='g-art', priority=False):
    return f'<img class="{cls}" src="{ART}" srcset="/assets/images/web-v2/ghostheart-640.webp {SIZES[640]}w, /assets/images/web-v2/ghostheart-960.webp {SIZES[960]}w, {ART} {SIZES[1440]}w" sizes="(max-width: 760px) 100vw, 58vw" width="{W}" height="{H}" alt="The GhostHeart world: shadowed figures with glowing crimson hearts beneath a red moon" {"fetchpriority=high" if priority else "loading=lazy"}/>'

def film(vid, title, copy):
    return f'''<article class="g-film" id="film-{vid}"><div class="g-player"><button type="button" data-video-id="{vid}" data-video-title="{escape(title, quote=True)}" aria-label="Load film: {escape(title, quote=True)}"><img src="/assets/videos/youtube/{vid}.jpg" width="1280" height="720" loading="lazy" alt=""/><span class="g-play" aria-hidden="true">▶</span><span class="g-play-label">Load film</span></button></div><button class="g-close" type="button" hidden>Close player</button><h3>{escape(title)}</h3><p>{escape(copy)}</p><a class="g-link" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></article>'''
FILMS = '<div class="g-films">'+film('AOCRvtz92JM','This Is GhostHeart','The name, the scars, and the reason a hidden heart chose to be seen.')+film('mBAsUNX3vHQ',"GhostHeart’s Oath",'The promise to protect the light in others.')+'</div>'

def signup(prefix='signal'):
    return f'''<form class="g-form signal-signup-form" action="{escape(FORM, quote=True)}" method="post" target="_blank" rel="noopener noreferrer"><label for="{prefix}-email">Email address</label><div class="g-form-row"><input id="{prefix}-email" type="email" name="EMAIL" required autocomplete="email" inputmode="email" placeholder="you@example.com" maxlength="254" aria-describedby="{prefix}-note"/><button type="submit" name="subscribe">Follow by email <span aria-hidden="true">↗</span></button></div><div class="g-honeypot" aria-hidden="true"><input type="text" name="b_a7ab330423f3b936c48b8d8ba_880e8056a6" tabindex="-1" autocomplete="off"/></div><p class="g-small" id="{prefix}-note">Opens Mailchimp to complete your signup. Follow its confirmation instructions. Read the <a href="/GhostHeart_Privacy.html">privacy notice</a>.</p><p class="g-form-status" role="status" aria-live="polite"></p></form>'''

def follow_block(prefix='signal'):
    return f'''<section class="g-section g-follow" id="join-the-signal"><div class="g-wrap g-two"><div><p class="g-kicker">Keep the story close</p><h2>Don't lose<br/>the next page.</h2><p>New story pages, selected films, and Sunday reading details as they become available. No need to catch every post.</p></div><div>{signup(prefix)}<p class="g-small">No account required to read. Unsubscribe from any update.</p></div></div></section>'''

def page(title, desc, path, body, image=ART):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{escape(title)} | GhostHeart</title><meta name="description" content="{escape(desc, quote=True)}"/><meta name="theme-color" content="#090909"/><link rel="icon" href="/favicon.ico"/><link rel="canonical" href="{BASE}{path}"/><meta property="og:type" content="website"/><meta property="og:site_name" content="GhostHeart"/><meta property="og:title" content="{escape(title, quote=True)}"/><meta property="og:description" content="{escape(desc, quote=True)}"/><meta property="og:url" content="{BASE}{path}"/><meta property="og:image" content="{BASE}{image}"/><meta name="twitter:card" content="summary_large_image"/><link rel="alternate" type="application/rss+xml" title="GhostHeart Journal" href="/journal/feed.xml"/><link rel="stylesheet" href="/assets/shared/ghostheart-world.css"/><link rel="stylesheet" href="{CSS}"/><script defer src="/assets/shared/ghostheart-world.js"></script><script defer src="{JS}"></script></head><body class="ghx-site gateway-v2"><a class="skip-link" href="#main-content">Skip to content</a>{header()}<main id="main-content">{body}</main>{FOOTER}</body></html>'''

def titleblock(kicker, title, desc):
    return f'<section class="g-section g-page-top"><div class="g-wrap"><p class="g-kicker">{kicker}</p><h1>{title}</h1><p class="g-lead">{desc}</p></div></section>'

home = f'''<section class="g-hero" id="home"><div class="g-wrap g-hero-grid"><div class="g-hero-copy"><p class="g-kicker">Music. Story. Purpose.</p><h1>The world<br/>can be cruel.<br/><em>We don't<br/>have to be.</em></h1><p class="g-lead">One lived story. Told through music, film, and the words that refuse to stay silent.</p><div class="g-actions">{link(READ,'Begin the story <span aria-hidden="true">↗</span>','g-button')}{link('#films','Meet GhostHeart on film ↓')}</div><div class="g-resume" hidden><a data-resume-link href="{READ}">Continue where you stopped ↗</a><button type="button" data-forget-reading>Clear saved place</button></div></div><figure class="g-hero-image">{picture(priority=True)}<figcaption>The heart survived. Then it chose a purpose.</figcaption></figure></div></section><div class="g-ribbon"><div class="g-wrap"><span>STILL HERE</span><b aria-hidden="true">✦</b><span>STILL BECOMING</span><b aria-hidden="true">✦</b><span>STILL HUMAN</span></div></div><section class="g-section"><div class="g-wrap g-feature"><div><p class="g-kicker">Now unfolding · Begin here</p><p class="g-number" aria-hidden="true">01</p></div><div><p class="g-small">Public introduction · Before the book's first chapter</p><h2>How We Got Here.</h2><p class="g-lead">Not the whole life. Not every scar. Begin with the name, the promise, and why the story reaches beyond the music.</p>{link(READ,'Read the introduction ↗','g-button')}</div></div></section><section class="g-section g-dark" id="films"><div class="g-wrap"><div class="g-section-head"><div><p class="g-kicker">The name &amp; the promise</p><h2>Meet the heart.<br/>Hear the oath.</h2></div><p>Two ways into the same story. Players load only when you choose.</p></div>{FILMS}<div class="g-actions">{link('/music/index.html','Explore music &amp; films ↗')}</div></div></section><section class="g-section"><div class="g-wrap g-angel-teaser">{f'<img src="{ANGEL}" width="600" height="338" loading="lazy" alt="The approved wingless Angel in a dark hooded gown, with a glowing crimson heart"/>' if HAS_ANGEL else '<div class="g-word-art" aria-hidden="true">LOVE<br/>STAYED.</div>'}<div><p class="g-kicker">A story within the story</p><h2>GhostHeart<br/>and His Angel.</h2><p>The love story behind GhostHeart. The person who saw the heart beneath the scars and never asked it to hide.</p>{link('/GhostHeart_Angel.html','Step into their story ↗')}</div></div></section><section class="g-section g-live"><div class="g-wrap g-two"><div><p class="g-kicker">Sunday readings</p><h2>A few pages.<br/>A deeper part<br/>of the story.</h2></div><div><p class="g-status">Reading details to be announced</p><p>Selected pages from the story, in GhostHeart's voice. A place to stay with the words—not rush through them.</p>{link('/live/index.html','Visit the reading room ↗')}</div></div></section><section class="g-section"><div class="g-wrap g-two"><div><p class="g-kicker">Purpose, beyond the screen</p><h2>Leave a door<br/>open behind you.</h2><p>The music is a way in. Compassion, useful support, and what comes next are part of the reason it exists.</p></div><div class="g-paths">{link('/GhostHeart_Resources.html','Find support <span>↗</span>')}{link('/GhostHeart_Quotes.html','Find words to carry <span>↗</span>')}{link('/GhostHeart_Projects.html#axiomara','Axiomara &amp; studio projects <span>↗</span>')}</div></div></section>{follow_block()}'''
write('index.html',page('One story. Still unfolding.','Enter the GhostHeart story through music, films, words, and purpose. Begin with How We Got Here.', '/', home))

intro = {
 'slug':'how-we-got-here', 'title':'How We Got Here', 'category':'Public introduction', 'published':STAMP,
 'summary':'Before the first chapter: the name, the promise, and a reason to keep the door open for someone else.',
 'image':ART,
 'paragraphs':[
  'This is an introduction to GhostHeart, not an excerpt from the book. The deeper life story will unfold through selected pages. Begin here with the purpose behind it.',
  'GhostHeart is one lived story told through music, film, words, and visual storytelling. But the music is not the whole story. It opens a door into the experiences, questions, relationships, and choices behind it.',
  'The heart survived. Then it chose a purpose.',
  'Survival matters. So does what a person chooses to carry forward. GhostHeart turns toward people who have been reduced to a label, judged from a distance, or written off before their story was heard. Seeing their humanity does not mean looking away from the truth or excusing harm. It means refusing to let one word tell the whole story.',
  'That is where the name meets the promise. This Is GhostHeart introduces the heart behind the work. GhostHeart’s Oath gives that heart a direction: protect the light in others. The films below belong together, but you can begin with either one.',
  'Love belongs here too. GhostHeart and His Angel is the relationship story within this larger world—the person who saw the heart beneath the scars and never asked it to hide. It has its own place, alongside the music and the life behind it.',
  'You do not have to share this past to find something in these words. Stay with a song. Carry a line that means something to you. Find support when you need more than a story can offer. No one has to disclose their own pain to belong here.',
  'The first chapter of the written book is How We Got Here. This public beginning stops before those private chapters. Sunday readings will connect selected pages to the work unfolding around them; reading details will be announced when they are confirmed.',
  'For now, meet the name. Hear the promise. Then choose what you want to carry forward.'
 ],
 'links':[{'label':'Follow the next page by email','url':'/follow/index.html'},{'label':'Find support','url':'/GhostHeart_Resources.html'}],
 'sources':['index.html','GhostHeart_Version_Mission.html','albums/human-after-all/index.html','albums/ghosthearts-angel/index.html'],
 'gateway_films':True
}
jp=ROOT/'.github/content/journal.json'; posts=json.loads(jp.read_text()); posts=[p for p in posts if p['slug']!=intro['slug']]; posts.append(intro); write('.github/content/journal.json',json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
# Add optional connected films and a deliberate on-device reading bookmark to the journal renderer.
bp=ROOT/'.github/scripts/build_journal.py'; build=bp.read_text()
if 'def gateway_extra(post):' not in build:
    helper='\n\ndef gateway_extra(post):\n    if not post.get("gateway_films"): return ""\n    return '+repr('<section class="g-reading-extra" aria-label="Films connected to this introduction"><p class="g-kicker">The name and the promise</p>'+FILMS+'</section><div class="g-bookmark"><button type="button" data-save-reading>Save my place on this device</button><button type="button" data-forget-reading>Clear saved place</button><p role="status" data-reading-status></p></div>')+'\n'
    build=build.replace("first = POSTS[0]",helper+'\nfirst = POSTS[0]')
    assert '{paragraphs}</div><section' in build
    build=build.replace('{paragraphs}</div><section','{paragraphs}</div>{gateway_extra(post)}<section')
    build=build.replace('<script defer src="/assets/shared/ghostheart-world.js"></script>','<script defer src="/assets/shared/ghostheart-world.js"></script>\n<link rel="stylesheet" href="/assets/shared/gateway-v2.css"/>\n<script defer src="/assets/shared/gateway-v2.js"></script>')
    write('.github/scripts/build_journal.py',build)

story=titleblock('The story / One life','Not every scar.<br/><em>The whole heart.</em>','The story is more than a catalog of songs. Begin with what is available now, then follow it as it unfolds.')+f'<section class="g-section"><div class="g-wrap g-two"><div><p class="g-kicker">Start reading</p><h2>How We Got Here.</h2><p>The public introduction to the name and the promise. The private book chapters are not released here.</p>{link(READ,"Read the introduction ↗","g-button")}</div><div class="g-paths">{link("/GhostHeart_Angel.html","GhostHeart and His Angel <span>↗</span>")}{link("/journal/index.html","From the journal <span>↗</span>")}{link("/live/index.html","Sunday readings <span>↗</span>")}</div></div></section>'+follow_block('story')
write('GhostHeart_Story.html',page('The story','The life and purpose behind GhostHeart. Read the public introduction, meet His Angel, and follow the story.', '/GhostHeart_Story.html',story))
# Retain Start Here as a useful direct entry, not another copy of the homepage.
start=titleblock('Start here','Begin with<br/><em>the heart.</em>','One public introduction. Two films. A clear way into the story.')+f'<section class="g-section"><div class="g-wrap">{link(READ,"Read How We Got Here ↗","g-button")}<p>Begin with the name and the promise, before the deeper book chapters.</p>{FILMS}</div></section>'+follow_block('start')
write('start/index.html',page('Start here','Begin GhostHeart with How We Got Here, the identity film, and the Oath.', '/start/',start))
angel=titleblock('GhostHeart and His Angel','Love stayed.<br/><em>The story changed.</em>','The love story behind GhostHeart.')+f'<section class="g-section"><div class="g-wrap g-two">'+(f'<img class="g-angel-full" src="{ANGEL}" width="600" height="338" alt="The approved wingless Angel, her face shadowed beneath a hood and her heart glowing crimson"/>' if HAS_ANGEL else '<div class="g-word-art" aria-hidden="true">I GOT YOU<br/>FOR LIFE.</div>')+f'<div><h2>She saw the heart.</h2><p>GhostHeart’s Angel is the love story behind GhostHeart—the story of the person who saw the heart beneath the scars and never asked it to hide.</p><p>These songs are about finding love in the ashes, choosing each other through every battle, and building something real when the world gives you every reason to break.</p><blockquote>I got you for life.</blockquote><p>GhostHeart may have been shaped by pain, but GhostHeart’s Angel helped turn that pain into purpose.</p>{link("/albums/ghosthearts-angel/index.html","Explore the relationship songs ↗","g-button")}</div></div></section>'+follow_block('angel')
write('GhostHeart_Angel.html',page('GhostHeart and His Angel','The love story behind GhostHeart. The person who saw the heart beneath the scars.', '/GhostHeart_Angel.html',angel,ANGEL if HAS_ANGEL else ART))
live=titleblock('The reading room','A few pages.<br/><em>A little closer.</em>','Selected pages from the story, in GhostHeart’s voice.')+f'<section class="g-section"><div class="g-wrap g-two"><div><p class="g-status">Reading details to be announced</p><h2>Sunday Live.</h2><p>The next reading’s date, time, and viewing link will appear here when confirmed. There is no scheduled live event or replay announced on this page yet.</p><p>Readings connect relevant pages to the music and questions being explored—not a promise to reveal the entire book in order.</p></div><div><p class="g-kicker">While you are here</p><h2>Meet the name.<br/>Hear the promise.</h2>{link(READ,"Begin the story ↗","g-button")}</div></div></section>'+follow_block('live')
write('live/index.html',page('Sunday Live','GhostHeart Sunday readings: selected pages and confirmed viewing details when announced.', '/live/',live))
music=titleblock('Music & films','Feel the story.<br/><em>Choose your way in.</em>','Watch the films. Hear the recordings. Stay with the words behind them.')+f'<section class="g-section"><div class="g-wrap">{FILMS}<div class="g-paths g-music-paths">{link("/GhostHeart_Videos.html","Browse all films <span>↗</span>")}{link("/GhostHeart_Songs.html","Hear released recordings <span>↗</span>")}{link("/albums/index.html","Explore thematic collections <span>↗</span>")}</div><p class="g-small">Recordings are releases. Collections group songs by their stories; availability varies.</p></div></section>'
write('music/index.html',page('Music & films','GhostHeart films, released recordings, and thematic music collections, connected to the story.', '/music/',music))
follow=titleblock('Follow GhostHeart','Keep the next<br/><em>page close.</em>','New story pages, selected films, and Sunday reading details as they become available.')+f'<section class="g-section"><div class="g-wrap g-two"><div>{signup("follow")}<p>No account is needed to read. Joining is optional, and you can unsubscribe from any update.</p></div><aside class="g-side-note"><h2>Start now.<br/>Stay when it matters.</h2><p>You do not have to wait for an email to begin.</p>{link(READ,"Read How We Got Here ↗")}{link("/journal/feed.xml","Follow the journal via RSS ↗")}</aside></div></section>'
write('follow/index.html',page('Follow GhostHeart','Follow the unfolding GhostHeart story by email. Optional signup, public reading, and RSS.', '/follow/',follow))

# Update shared navigation statically; do not delete archive URLs or recordings.
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts: continue
    text=path.read_text(encoding='utf-8')
    if '<header class="nav ghx-header' not in text: continue
    owner='legacy' if 'data-nav-owner="legacy"' in text else 'shared'
    text=re.sub(r'<header class="nav ghx-header\b.*?</header>',lambda m:header(owner),text,count=1,flags=re.S)
    text=re.sub(r'<footer class="ghx-footer\b.*?</footer>',lambda m:FOOTER,text,count=1,flags=re.S)
    if f'href="{CSS}"' not in text: text=text.replace('</head>',f'<link rel="stylesheet" href="{CSS}"/></head>')
    path.write_text(text,encoding='utf-8',newline='\n')

# Explain the only new browser storage, and avoid asserting unverified email settings.
privacy=ROOT/'GhostHeart_Privacy.html'; text=privacy.read_text()
marker='<h2>Optional reading bookmark</h2>'
if marker not in text:
    text=text.replace('<h2>What is collected</h2>',marker+'<p>If you choose Save my place, this browser stores the page path and reading position on this device. It is not an account, is not sent to GhostHeart, and can be removed with Clear saved place. Email addresses are never stored by this bookmark.</p><h2>What is collected</h2>')
text=text.replace('You must confirm the subscription before messages are sent.','Follow the confirmation instructions shown by Mailchimp after signup.')
text=text.replace('<li>You can ignore the confirmation message and remain unsubscribed.</li>','<li>Submitting the website form alone is not a confirmation of delivery. Mailchimp manages your signup status and any confirmation step.</li>')
privacy.write_text(text,encoding='utf-8',newline='\n')
# Do not leave obsolete Angel image previews on the separate music collection.
if HAS_ANGEL:
    ap=ROOT/'albums/ghosthearts-angel/index.html'; at=ap.read_text();at=at.replace('https://www.myghostheart.com/assets/videos/the-angel-who-made-ghostheart-jvHS5j00FL4.jpg',BASE+ANGEL).replace('../../assets/videos/the-angel-who-made-ghostheart-jvHS5j00FL4.jpg',ANGEL);ap.write_text(at,encoding='utf-8',newline='\n')
# Only changed/new canonical URLs get a new lastmod. Existing URLs stay reachable.
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}; ET.register_namespace('',ns['s']); sm=ROOT/'sitemap.xml'; doc=ET.parse(sm); root=doc.getroot(); updated=['/','/start/','/GhostHeart_Story.html','/GhostHeart_Angel.html','/GhostHeart_Privacy.html','/music/','/live/','/follow/','/journal/',READ]
for suffix in updated:
    address=BASE+suffix; found=next((x for x in root if x.find('s:loc',ns).text==address),None)
    if found is None: found=ET.SubElement(root,'{'+ns['s']+'}url');ET.SubElement(found,'{'+ns['s']+'}loc').text=address
    last=found.find('s:lastmod',ns)
    if last is None:last=ET.SubElement(found,'{'+ns['s']+'}lastmod')
    last.text='2026-09-28'
ET.indent(doc);doc.write(sm,encoding='utf-8',xml_declaration=True)
# A build receipt is not evidence of email delivery or public event scheduling.
write('.github/GATEWAY_STATUS.md','''# GhostHeart gateway build\n\nApproved scope: new cinematic homepage, public introduction, connected films, email signup path, current wingless Angel presentation, removal of Versions-led navigation, honest Sunday status. Existing recordings and archived URLs retained.\n\nEmail provider: existing Mailchimp audience endpoint retained. No authenticated Mailchimp session was available for settings or send verification. Final welcome activation, sender authentication, a real confirmation/delivery/unsubscribe test, and newsletter scheduling are NOT COMPLETE. No bulk send, new subscriber, social post, or live event is created by this build.\n\nThe public introduction is new website copy based on already-public brand/mission material, not a private manuscript excerpt. Publication of later chapters requires separate approval.\n\nRun build_gateway.py then build_journal.py, validate_site.py, JavaScript syntax tests and test_gateway.cjs. Only generated website content should be committed by the build workflow.\n''')
write('.github/email/welcome-draft.html.txt','''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Welcome to GhostHeart — DRAFT, NOT ACTIVATED</title></head><body><h1>You found the heart.</h1><p>Welcome to GhostHeart. One lived story, told through music, film, and words.</p><p>Begin with How We Got Here: the name, the promise, and why the story reaches beyond the music.</p><p><a href="https://www.myghostheart.com/journal/how-we-got-here.html">Begin the story</a></p><p>— GhostHeart</p><!-- DRAFT ONLY. Configure and verify Mailchimp sender, audience, required provider footer, confirmation trigger and unsubscribe before activation. Never send this draft as a standalone campaign. --></body></html>''')
print('Built gateway pages, public introduction, static navigation, web artwork and honest signup path. Email delivery NOT verified.')
