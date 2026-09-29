#!/usr/bin/env python3
"""Finish the public gateway using existing published material. Never sends email."""
from pathlib import Path
from html import escape
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen, Request
from datetime import datetime, timezone
import copy, json, re, runpy, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as Soup
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
BASE='https://www.myghostheart.com'
DAY='2026-09-29'
SOURCE=ROOT/'.github/content/site-library.json'
ORDER=['broken-man','ghostheart','ghosthearts-angel','fatherhood','human-after-all','love-is-love','the-ones-we-carry','uplifting','youre-not-god']

def read(path): return (ROOT/path).read_text(encoding='utf-8')
def write(path,text):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
def parse(text): return Soup(text,'html.parser')
def local(url, page):
 full=urljoin(BASE+'/'+page,url)
 return full.removeprefix(BASE) if full.startswith(BASE+'/') else full
def html_absolute(node,page):
 node=copy.deepcopy(node)
 for el in node.select('[href],[src],[poster]'):
  for a in ['href','src','poster']:
   if el.has_attr(a): el[a]=local(el[a],page)
 return str(node)
def txt(node): return node.get_text(' ',strip=True) if node else ''
def norm(value): return re.sub(r'[^a-z0-9]+','',value.lower())

# Snapshot only public source material. Later builds read this register, never re-scrape generated output.
if SOURCE.exists(): data=json.loads(SOURCE.read_text())
else:
 data={'schema':1,'source_commit':'988283c66051f75f08aba5fac0abbfe235b5ff89','collections':{},'legacy_ids':{},'quotes':[],'recordings':[]}
 for p in ROOT.rglob('*.html'):
  if '.git' not in p.parts:
   rel=p.relative_to(ROOT).as_posix();data['legacy_ids'][rel]=[n['id'] for n in parse(p.read_text()).select('[id]')]
 q=re.search(r'const quotes\s*=\s*(\[.*?\]);',read('GhostHeart_Quotes.html'),re.S)
 assert q,'Published quote source not found';data['quotes']=json.loads(q[1])
 records=parse(read('GhostHeart_Songs.html'))
 for card in records.select('.record-card'):
  data['recordings'].append({'id':card['id'],'title':txt(card.find('h3')),'html':html_absolute(card,'GhostHeart_Songs.html'),'tracks':int(card.get('data-track-count','1'))})
 for slug in ORDER:
  path=f'albums/{slug}/index.html';s=parse(read(path));tracks=[]
  for li in s.select('#tracks .track-list > li'):
   entry={'id':li['id'],'title':txt(li.find('h3')),'meta':txt(li.select_one('.track-meta')),'links':[],'video':None}
   for a in li.select('.track-actions a'):entry['links'].append({'url':local(a['href'],path),'label':txt(a)})
   block=s.find(id='watch-'+li['id']);player=block.select_one('[data-film-id]') if block else None
   if player:entry['video']=player['data-film-id']
   tracks.append(entry)
  data['collections'][slug]={'title':txt(s.find('h1')),'description':s.find('meta',attrs={'name':'description'})['content'],'paragraphs':[str(p) for p in s.select('#about .prose > p')],'tracks':tracks}
 assert len(data['quotes'])==17 and len(data['recordings'])>=13
 write('.github/content/site-library.json',json.dumps(data,ensure_ascii=False,indent=2)+'\n')

# The approved first-build generator remains the starting point; all legacy finishing is reproducible below.
g=runpy.run_path(str(ROOT/'.github/scripts/build_gateway.py'))
ART=g['ART'];ANGEL=g['ANGEL'];READ=g['READ'];L=g['link'];FOLLOW=g['follow_block'];HEAD=g['titleblock']

def page(path,title,description,body,image=ART):
 canonical='/' if path=='index.html' else '/'+path.removesuffix('index.html') if path.endswith('/index.html') else '/'+path
 write(path,g['page'](title,description,canonical,body,image))

def filterbar(label,placeholder):
 return f'<div class="l-filter" data-filter-controls hidden><label for="library-search">{escape(label)}</label><div><input type="search" id="library-search" placeholder="{escape(placeholder,quote=True)}" autocomplete="off"/><button type="button" data-clear-search>Clear search</button></div><p id="library-results" role="status" aria-live="polite"></p></div><p data-library-empty hidden>No matching items. Try a different word.</p>'

def searchable(contents,kind='items'):
 return f'<div data-library data-item-name="{kind}">{contents}</div>'

# Keep film IDs in one source. This supplied Rebellion URL was read live and matched GhostHeart.
cattext=read('assets/data/ghostheart-video-catalog.js')
films=json.loads(re.search(r'Object\.freeze\((\[.*\])\);',cattext,re.S)[1])
if not any(f['key']=='rebellion' for f in films):
 films.append({'key':'rebellion','cardId':'film-rebellion','title':'Rebellion','videoTitle':'GhostHeart – Rebellion (Official Music Video) | Love Is Not Rebellion','youtubeId':'FaT_Ibrs9Y0','provider':'youtube','description':'Love doesn’t ask permission to exist.','meta':['Official music video'],'song':{'label':'Explore Love is Love','href':'albums/love-is-love/index.html#rebellion'},'related':[],'accessibility':'Use the YouTube player CC control for available captions.','thumbnail':'assets/videos/youtube/FaT_Ibrs9Y0.jpg','featured':False})
thumb=ROOT/'assets/videos/youtube/FaT_Ibrs9Y0.jpg'
if not thumb.exists():
 try:
  req=Request('https://i.ytimg.com/vi/FaT_Ibrs9Y0/maxresdefault.jpg',headers={'User-Agent':'GhostHeart website artwork synchronization'})
  with urlopen(req,timeout=20) as r: payload=r.read(3000000)
  from io import BytesIO
  im=Image.open(BytesIO(payload));im.verify();thumb.write_bytes(payload)
 except Exception:
  # An unavailable thumbnail does not mean an unavailable film. Reuse approved brand art.
  next(f for f in films if f['key']=='rebellion')['thumbnail']=ART.lstrip('/')
for f in films:
 f['meta']=[m for m in f.get('meta',[]) if 'Versions' not in m and 'spotlight' not in m.lower()]
 if f['key']=='the-man-beneath-the-moon':f['description']='A GhostHeart film about the life behind the name.'
 for rel in f.get('related',[]):
  if 'GhostHeart_Version' in rel.get('href',''):rel.update(href='GhostHeart_Story.html',label='Continue the story')
write('assets/data/ghostheart-video-catalog.js','// Current public film references. Rebuild pages through finish_gateway.py.\nwindow.GHOSTHEART_VIDEO_CATALOG = Object.freeze('+json.dumps(films,ensure_ascii=False,indent=2)+');\n')
byid={f['youtubeId']:f for f in films}
bykey={f['key']:f for f in films}

def film(f,card_id=None):
 vid=f['youtubeId'];assert re.fullmatch(r'[\w-]{11}',vid)
 title=f['title'];desc=f.get('description','');ident=card_id or f['cardId']
 links=[]
 if f.get('song',{}).get('href'):links.append(L(local(f['song']['href'],'index.html'),escape(f['song'].get('label','Continue the story'))+' ↗'))
 return f'<article class="g-film" id="{escape(ident)}" data-library-item data-search="{escape(title+" "+desc,quote=True)}"><div class="g-player"><button type="button" data-video-id="{vid}" data-video-title="{escape(title,quote=True)}" aria-label="Load film: {escape(title,quote=True)}"><img src="/{f["thumbnail"].lstrip("/")}" width="1280" height="720" loading="lazy" alt=""/><span class="g-play" aria-hidden="true">▶</span><span class="g-play-label">Load film</span></button></div><button class="g-close" type="button" hidden>Close player</button><h3>{escape(title)}</h3><p>{escape(desc)}</p><div class="g-actions"><a class="g-link" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a>{"".join(links)}</div></article>'

# Link missing existing work without asserting a new streaming-platform release.
collections=copy.deepcopy(data['collections'])
collections['fatherhood']['title']='Fatherhood';collections['ghosthearts-angel']['title']='GhostHeart’s Angel';collections['uplifting']['title']='Uplifting'
if not collections['fatherhood']['tracks']:
 dad=next(r for r in data['recordings'] if r['id']=='song-the-dad')
 card=parse(dad['html']);a=next(a for a in card.select('a[href]') if 'open.spotify.com/' in a['href'])
 collections['fatherhood']['tracks']=[{'id':'the-dad','title':'The Dad','meta':'Film: The Dad I Never Had','links':[{'url':a['href'],'label':'Listen on Spotify'}],'video':'cBNxq4y1ahU'}]
for slug,coll in collections.items():
 for t in coll['tracks']:
  if t['id']=='human-too':t['video']='ARCFOZSOC_o'
  if t['id']=='rebellion':t['video']='FaT_Ibrs9Y0'
  if 'Fixed Vocal Ending' in t.get('meta',''):t['meta']=''
  # Retain actual recording links and links into the recording archive, not redundant old watch fragments.
  t['links']=[a for a in t['links'] if 'youtube.com/watch' not in a['url'] and '#watch-' not in a['url']]
 cards='';items=''
 for t in coll['tracks']:
  action=''.join(L(a['url'],escape(a['label'])) for a in t['links'])
  if t['video']:
   f=byid[t['video']];action=L('#watch-'+t['id'],'Watch film ↓','g-button')+action;cards+=film(f,'watch-'+t['id'])
  items+=f'<li id="{t["id"]}"><div><p class="g-small">{escape(t.get("meta",""))}</p><h3>{escape(t["title"])}</h3></div><div class="g-actions">{action}</div></li>'
 idx=ORDER.index(slug);previous=ORDER[(idx-1)%len(ORDER)];nxt=ORDER[(idx+1)%len(ORDER)]
 image=ANGEL if slug=='ghosthearts-angel' else ART
 paragraphs=''.join(coll['paragraphs']).replace('this playlist','this collection')
 body=HEAD('Music / Thematic collection',escape(coll['title']),escape(coll['description']))
 body+=f'<section class="g-section"><div class="g-wrap l-collection-intro"><img src="{image}" width="1672" height="941" alt="GhostHeart artwork for {escape(coll["title"],quote=True)}"/><div><p class="g-status">{len(coll["tracks"])} linked {"song" if len(coll["tracks"])==1 else "songs"}</p><p>This website collection connects songs by their story. See Released recordings for their original release formats.</p><div class="g-actions">{L("#tracks","Explore the songs ↓","g-button")}{L("/GhostHeart_Songs.html","Released recordings ↗")}</div></div></div></section>'
 body+=f'<section class="g-section" id="about"><div class="g-wrap l-prose"><h2>Behind the music.</h2>{paragraphs}</div></section><section class="g-section" id="tracks"><div class="g-wrap"><h2>Stay with a song.</h2><ol class="l-track-list">{items}</ol></div></section>'
 if cards:body+=f'<section class="g-section g-dark" id="watch"><div class="g-wrap"><h2>The films.</h2><div class="g-films">{cards}</div></div></section>'
 body+=f'<nav class="g-wrap l-collection-nav" aria-label="More collections">{L("/albums/"+previous+"/index.html","← "+escape(collections[previous]["title"]))}{L("/albums/index.html","All collections")}{L("/albums/"+nxt+"/index.html",escape(collections[nxt]["title"])+" →")}</nav>'+FOLLOW('collection')
 page(f'albums/{slug}/index.html',coll['title']+' · Collection',coll['description'],body,image)

indexcards=''
for slug in ORDER:
 c=collections[slug];n=len(c['tracks']);indexcards+=f'<article class="l-collection-card" data-library-item data-search="{escape(c["title"]+" "+" ".join(t["title"] for t in c["tracks"]),quote=True)}"><p class="g-kicker">{n} linked {"song" if n==1 else "songs"}</p><h2>{L("/albums/"+slug+"/index.html",escape(c["title"]))}</h2><p>{escape(c["description"])}</p></article>'
page('albums/index.html','Explore the collections','GhostHeart music grouped by story: survival, identity, love, fatherhood, grief, and hope.',HEAD('Music / Collections','Different stories.<br/><em>The same heart.</em>','Nine thematic collections. Released recordings keep their original formats and listening links.')+'<section class="g-section"><div class="g-wrap">'+searchable(filterbar('Find a collection or song','Search titles…')+'<div class="l-collections">'+indexcards+'</div>','collections')+'</div></section>'+FOLLOW('collections'))

# Film and recording libraries are generated, searchable, and remain readable without JavaScript.
filmgrid='<div class="g-films">'+''.join(film(f) for f in films)+'</div>'
page('GhostHeart_Videos.html','Films','Watch GhostHeart films and follow their connections to the music and story.',HEAD('Music & films / Watch','Stay with<br/><em>the story.</em>','Choose a film. Players load only when you choose; direct YouTube links remain available.')+'<section class="g-section"><div class="g-wrap">'+searchable(filterbar('Find a film','Search film titles…')+filmgrid,'films')+'</div></section>'+FOLLOW('films'))
recordhtml=''
for r in data['recordings']:
 card=parse(r['html']).select_one('.record-card')
 card['data-library-item']='';card['data-search']=txt(card)
 for el in card.select('.record-meta span'):
  if re.fullmatch(r'Release\s+\d+',txt(el)):el.decompose()
 for el in card.select('.record-actions a'):
  el['class']=['g-button' if 'primary' in el.get('class',[]) else 'g-link']
 target={'song-rebellion':'rebellion','human-too':'human-too-remake','song-the-dad':'the-dad','this-is-ghostheart':'this-is-ghostheart'}.get(r['id'])
 if target and not any('GhostHeart_Videos.html#'+bykey[target]['cardId'] in a['href'] for a in card.select('a[href]')):
  actions=card.select_one('.record-actions')
  if actions:actions.append(parse(L('/GhostHeart_Videos.html#'+bykey[target]['cardId'],'Watch current film ↗')).a)
 recordhtml+=str(card)
page('GhostHeart_Songs.html','Released recordings','Original GhostHeart singles and multi-track releases, with their existing listening links and related films.',HEAD('Music & films / Listen','The recordings.<br/><em>The stories they carry.</em>','Original releases and listening links. Different recordings remain distinct; nothing has been re-released or merged.')+f'<section class="g-section"><div class="g-wrap"><p id="catalog-count">{len(data["recordings"])} release and recording entries · {sum(r["tracks"] for r in data["recordings"])} listed tracks</p>'+searchable(filterbar('Find a recording','Search titles…')+'<div class="l-recordings">'+recordhtml+'</div>','recordings')+'</div></section>'+FOLLOW('recordings'))
# Existing legacy music reveals are replaced by the accessible generic hash handler.
songs=read('GhostHeart_Songs.html');songs=songs.replace('</main>','<!-- hasArchiveTarget: library-v3.js reveals deep-linked recording entries. --></main>');write('GhostHeart_Songs.html',songs)

# Preserve each supplied quote exactly. JavaScript enhances content; it no longer creates it.
quotes=''
for i,q in enumerate(data['quotes'],1):
 ident=f'quote-{i:02}';quotes+=f'<article class="l-quote" id="{ident}" tabindex="-1" data-quote><blockquote class="q-text">{escape(q)}</blockquote><p class="g-small">GhostHeart · {i:02}</p><div data-quote-actions hidden><button type="button" data-copy-quote>Copy quote</button><button type="button" data-copy-link>Copy link</button></div></article>'
qbody=HEAD('Words to carry','Find the line<br/><em>that finds you.</em>','The existing words, kept as written. Search, carry a quote, or share its direct link.')+f'<section class="g-section" id="quote-archive"><div class="g-wrap"><div class="l-filter" data-quote-controls hidden><label for="quote-search">Search these quotes</label><div><input id="quote-search" type="search" placeholder="Try love, strength, fire…" autocomplete="off"/><button id="clear-search" type="button">Clear search</button></div><p id="result-count" role="status" aria-live="polite"></p></div><div class="l-quotes" id="quote-grid">{quotes}</div><button type="button" id="show-more" aria-controls="quote-grid" hidden>Show more quotes</button><p id="copy-status" role="status" aria-live="polite"></p></div></section>'+FOLLOW('quotes')
page('GhostHeart_Quotes.html','Words to carry','Read and share the original GhostHeart quotes. The words remain available without JavaScript.',qbody)

# The old poetic taxonomy is no longer the public entry point. Keep old URLs and reflect their status honestly.
hub=HEAD('The story continues','More than<br/><em>a label.</em>','The life behind GhostHeart is not a list of categories. Enter the unfolding story instead.')+f'<section class="g-section"><div class="g-wrap g-two"><div><h2>Begin with the heart.</h2><p>The name. The promise. The purpose behind the music.</p>{L(READ,"Read How We Got Here ↗","g-button")}</div><div class="g-paths">{L("/GhostHeart_Angel.html","GhostHeart and His Angel ↗")}{L("/music/index.html","Music &amp; films ↗")}{L("/GhostHeart_Resources.html","Find support ↗")}</div></div></section>'
page('GhostHeart_Versions.html','The story continues','Continue into the current GhostHeart story, music, relationship, and purpose.',hub)
mission=HEAD('The mission','What survived<br/><em>can help someone rise.</em>','Build. Serve. Change. Turn survival into work that leaves a door open for someone else.')+f'<section class="g-section"><div class="g-wrap g-two"><div><h2>Protect the light.</h2><p>GhostHeart turns survival into work that serves people who feel unseen.</p><p>Build the platforms. Tell the truth. Leave a door open behind him.</p><p>Music and stories are not a substitute for professional care or emergency support.</p></div><div class="g-paths">{L("/GhostHeart_Resources.html","Find practical support ↗")}{L("/GhostHeart_Projects.html#axiomara","Axiomara &amp; studio projects ↗")}{L("/GhostHeart_Quotes.html","Carry a line with you ↗")}</div></div></section><section class="g-section g-dark"><div class="g-wrap"><h2>The promise.</h2><div class="g-films">{film(bykey["ghosthearts-oath"])}</div></div></section>'+FOLLOW('mission')
page('GhostHeart_Version_Mission.html','The mission','GhostHeart’s purpose: protect the light, offer useful support, and build tools that meet the person.',mission)
for p in ROOT.glob('GhostHeart_Version_*.html'):
 if p.name=='GhostHeart_Version_Mission.html':continue
 s=parse(p.read_text());main=s.find('main');banner=s.find(id='earlier-reflection-note')
 if main and not banner:main.insert(0,parse('<aside id="earlier-reflection-note" class="l-archive-note"><p>Earlier reflection</p><a href="/GhostHeart_Story.html">The current GhostHeart story begins here ↗</a></aside>'))
 robots=s.find('meta',attrs={'name':'robots'})
 if not robots:robots=s.new_tag('meta',attrs={'name':'robots'});s.head.append(robots)
 robots['content']='noindex,follow';p.write_text(str(s),encoding='utf-8')

# Remove the obsolete app implementation label while retaining old inbound anchors.
p=ROOT/'GhostHeart_Projects.html';s=p.read_text().replace('chronospark','axiomara');s=s.replace('id="axiomara-title"','id="axiomara-title"',1);p.write_text(s,encoding='utf-8')
css=ROOT/'assets/projects/projects-page.css';css.write_text(css.read_text().replace('.chronospark','.axiomara'),encoding='utf-8')

# Confirmation pages give useful next steps without mistaking a public page load for proof of a subscription.
for path,title,lead,detail in [
 ('signup/check-your-inbox.html','Check your inbox.','Complete the signup instructions from Mailchimp.','When confirmation is requested, use the link in that email. Check spam or promotions if it does not arrive. This page cannot check your subscription status.'),
 ('signup/confirmed.html','Welcome to GhostHeart.','The next page is waiting.','Mailchimp manages your subscription status. Opening this public page alone does not subscribe you. Follow its confirmation instructions if you have not finished signup.')]:
 body=HEAD('Follow GhostHeart',title,lead)+f'<section class="g-section"><div class="g-wrap l-prose"><p>{detail}</p><div class="g-actions">{L(READ,"Begin the story ↗","g-button")}{L("/follow/index.html","Return to signup ↗")}</div></div></section>'
 page(path,title,'GhostHeart email signup guidance and the public story.',body)

# A usable provider-template package, not an activated automation. Merge tags preserve the provider's required footer.
emailbody='<h1 style="font-size:34px;line-height:1.15;margin:0 0 22px;color:#f4eee6">You found the heart.</h1><p>Welcome to GhostHeart. One lived story, told through music, film, and words.</p><p>Begin with <strong>How We Got Here</strong>: the name, the promise, and why the story reaches beyond the music.</p><p><a style="display:inline-block;padding:15px 22px;background:#bd3028;color:#fff;text-decoration:none" href="'+BASE+READ+'?utm_source=ghostheart_signal&amp;utm_medium=email&amp;utm_campaign=welcome">Begin the story ↗</a></p><p>Stay for the words that mean something to you. Story pages, selected films, and reading details will follow as they become available.</p><p>— GhostHeart</p>'
footer='<hr style="border:0;border-top:1px solid #56443b;margin:30px 0"><p style="font-size:12px">*|LIST:DESCRIPTION|*</p><p style="font-size:12px">*|LIST:ADDRESS|*</p><p style="font-size:12px"><a href="*|UPDATE_PROFILE|*" style="color:#ffad95">Update preferences</a> · <a href="*|UNSUB|*" style="color:#ffad95">Unsubscribe</a></p>'
email='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Welcome to GhostHeart</title></head><body style="margin:0;background:#090909;color:#d7ccc3;font:17px/1.7 Arial,sans-serif"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center" style="padding:30px 18px"><table role="presentation" width="600" style="max-width:600px;width:100%" cellspacing="0" cellpadding="0"><tr><td style="padding:32px;background:#171110;border-top:3px solid #dd4635"><p style="font-weight:bold;letter-spacing:2px;color:#f4eee6">GHOST<span style="color:#fa7865">HEART</span></p>'+emailbody+footer+'</td></tr></table></td></tr></table></body></html>'
write('.github/email/welcome-mailchimp.html.txt',email)
write('.github/email/welcome-plain.txt','You found the heart.\n\nWelcome to GhostHeart. Begin with How We Got Here: the name, the promise, and why the story reaches beyond the music.\n\n'+BASE+READ+'?utm_source=ghostheart_signal&utm_medium=email&utm_campaign=welcome\n\nStory pages, selected films, and reading details as they become available.\n\n— GhostHeart\n\n*|LIST:DESCRIPTION|*\n*|LIST:ADDRESS|*\nUpdate preferences: *|UPDATE_PROFILE|*\nUnsubscribe: *|UNSUB|*\n')
write('.github/email/ACTIVATION.md','''# Mailchimp activation — not completed\n\nExisting account u: a7ab330423f3b936c48b8d8ba. Existing audience id: 880e8056a6. No new audience is needed.\n\nThe browser session available on September 29, 2026 stopped at the Mailchimp login page. No authenticated account access, settings change, activation, subscriber import or email send occurred. No confirmation/delivery/unsubscribe test has been completed.\n\n## Prepared welcome\nSubject: You found the heart. Welcome to GhostHeart.\nPreview: Begin with the name, the promise, and the story behind the music.\nPublic sender name: GhostHeart. Use the existing verified sender address only; do not invent an address or expose the legal identity.\nFiles: welcome-mailchimp.html.txt and welcome-plain.txt. These are provider-ready template sources, not campaigns. Required Mailchimp merge tags must be resolved and tested in the account. Never remove the required footer to hide it.\n\n## Required verification before activation\nConfirm the account/audience, existing subscriber status, opt-in configuration, sender verification/authentication, account sending limits and whether a welcome automation already exists. Avoid duplicate welcome sends. Confirm that any required footer address is an approved public business address; do not invent it. Enable the final welcome only after verifying the selected flow. No backfill or bulk send to existing contacts is authorized by this template.\n\nEnd-to-end evidence must distinguish: form submitted, pending contact, confirmation received, subscription confirmed, welcome received, link opened, unsubscribe recorded. A visit to signup/confirmed.html is not a verified subscriber. Use only an owner-approved test address.\n\n## Story updates\nUse the live RSS /journal/feed.xml only for approved published entries. Preserve slugs and original publication dates to avoid duplicate sends. No campaign schedule or recurring send is activated by this build. Confirm actual account capability and cadence before enabling. Do not add a paid plan or service.\n\nOfficial instructions: https://mailchimp.com/help/enable-or-disable-final-welcome-email/ ; https://mailchimp.com/help/set-signup-preferences/ ; https://mailchimp.com/help/set-up-email-domain-authentication/\n''')

runpy.run_path(str(ROOT/'.github/scripts/build_journal.py'))
# A final pass makes active navigation accurate, retains legacy anchors, and supplies non-JavaScript navigation.
archived=[]
for path in ROOT.rglob('*.html'):
 if '.git' in path.parts:continue
 rel=path.relative_to(ROOT).as_posix();s=parse(path.read_text())
 if not s.find('main') or not s.head:continue
 if not s.find('link',href='/assets/shared/library-v3.css'):s.head.append(s.new_tag('link',attrs={'rel':'stylesheet','href':'/assets/shared/library-v3.css'}))
 if not s.find('script',src='/assets/shared/library-v3.js'):s.head.append(s.new_tag('script',attrs={'defer':'','src':'/assets/shared/library-v3.js'}))
 header=s.select_one('header.gateway-header')
 if header:
  for a in header.select('[aria-current]'):del a['aria-current']
  section='/music/index.html' if rel.startswith('albums/') or rel in ['GhostHeart_Songs.html','GhostHeart_Videos.html','music/index.html'] else '/GhostHeart_Story.html' if rel.startswith('journal/') or rel in ['GhostHeart_Story.html','GhostHeart_Angel.html','start/index.html'] else '/live/index.html' if rel.startswith('live/') else '/GhostHeart_Version_Mission.html' if rel in ['GhostHeart_Projects.html','GhostHeart_Resources.html','GhostHeart_Version_Mission.html'] else '/follow/index.html' if rel.startswith(('follow/','signup/')) else '/index.html'
  active=header.select_one('a[href="'+section+'"]')
  if active:active['aria-current']='page' if active['href']=='/'+rel or rel=='index.html' else 'location'
 if not s.find(id='no-script-navigation'):
  fallback=parse('<noscript id="no-script-navigation"><nav class="l-nojs-nav" aria-label="Navigation without JavaScript"><a href="/GhostHeart_Story.html">Story</a><a href="/music/index.html">Music &amp; films</a><a href="/follow/index.html">Follow by email</a><a href="/GhostHeart_Resources.html">Find support</a></nav></noscript>')
  s.find('main').insert_before(fallback)
 if not rel.startswith('GhostHeart_Version_'):
  for a in s.select('a[href]'):
   if 'GhostHeart_Versions.html' in a['href']:
    a['href']='/GhostHeart_Story.html';a.clear();a.append('Continue the story ↗')
 existing={n['id'] for n in s.select('[id]')}
 for ident in data['legacy_ids'].get(rel,[]):
  if ident not in existing:
   alias=s.new_tag('span',attrs={'id':ident,'class':'l-anchor-alias','aria-hidden':'true'});s.find('main').insert(0,alias);existing.add(ident)
 # Keep legacy signup destinations private to search engines, not as conversion evidence.
 if rel.startswith('signup/') or rel=='GhostHeart_Versions.html':
  robots=s.find('meta',attrs={'name':'robots'})
  if not robots:robots=s.new_tag('meta',attrs={'name':'robots'});s.head.append(robots)
  robots['content']='noindex,follow'
 # Reading controls belong before the text, not only after the visitor has reached the end.
 if rel=='journal/how-we-got-here.html':
  bookmark=s.select_one('.g-bookmark');prose=s.select_one('.journal-prose')
  if bookmark and prose:prose.insert_before(bookmark.extract())
  button=s.select_one('[data-save-reading]')
  if button:button.string='Remember my place on this device'
 if rel=='GhostHeart_Resources.html' and not s.find(id='resource-review-scope'):
  s.find('main').append(parse('<aside class="l-archive-note" id="resource-review-scope"><p>These are starting points, not guaranteed service availability. Check the linked organization for its current hours and eligibility. GhostHeart does not provide crisis response.</p></aside>'))
 path.write_text(str(s),encoding='utf-8',newline='\n')

# Keep the sitemap honest: no retired taxonomy pages or public confirmation pages in discovery.
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'};ET.register_namespace('',ns['s']);sm=ROOT/'sitemap.xml';tree=ET.parse(sm);root=tree.getroot()
for entry in list(root):
 address=entry.find('s:loc',ns).text;tail=urlsplit(address).path.lstrip('/')
 if tail=='GhostHeart_Versions.html' or (tail.startswith('GhostHeart_Version_') and tail!='GhostHeart_Version_Mission.html') or tail.startswith('signup/'):root.remove(entry);continue
 last=entry.find('s:lastmod',ns)
 if last is None:last=ET.SubElement(entry,'{'+ns['s']+'}lastmod')
 last.text=DAY
ET.indent(tree);tree.write(sm,encoding='utf-8',xml_declaration=True)
write('.github/GATEWAY_STATUS.md','''# GhostHeart website finishing pass\n\nPublic website scope: searchable film and recording libraries; current Rebellion link; Human Too film connection; The Dad in Fatherhood; nine consistently presented thematic collections with Angel before Fatherhood; original 17 quotes server-rendered with copy/search/deep links; current story replaces taxonomy hub; older reflection URLs preserved and excluded from search discovery; mission has practical next steps; signup guidance and accessible navigation are consistent. No original releases, audio, lyrics or manuscript chapters were deleted, combined or newly published.\n\nMailchimp: authentication blocker persists. Existing audience and form destination retained. Prepared welcome templates include provider footer/unsubscribe merge tags. Welcome activation, sending-domain verification, subscriber confirmation, delivered email, unsubscribes, newsletter scheduling and social scheduling are NOT verified or activated. No real signup or email send occurs in browser tests.\n\nBuild command: python3 .github/scripts/finish_gateway.py. This runs the existing gateway and journal generators plus final legacy reconciliation. Rebuilds use .github/content/site-library.json, preserving the exact public quotes, recording cards and collection inputs.\n''')
write('.github/evidence/site-finish/content-inventory.json',json.dumps({'collections':len(collections),'collectionOrder':ORDER,'quotes':len(data['quotes']),'recordingEntries':len(data['recordings']),'films':len(films),'emailDeliveryVerified':False,'newsletterActivated':False,'signupUsesExistingAudience':True},indent=2)+'\n')
print('Finished public-site generation. Mailchimp activation and delivery remain blocked by authentication.')
