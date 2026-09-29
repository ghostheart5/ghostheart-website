#!/usr/bin/env python3
"""Canonical complete build, including preservation of the previous featured recording."""
from pathlib import Path
import json, runpy
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'.github/content/site-library.json'
if not source.exists():runpy.run_path(str(ROOT/'.github/scripts/finish_gateway.py'))
data=json.loads(source.read_text(encoding='utf-8'))
# This published recording lived outside .record-card in the old release spotlight.
ident='i-wont-pretend-to-speak-for-you'
if not any(r['id']==ident for r in data['recordings']):
 record='''<article class="record-card" data-track-count="1" id="i-wont-pretend-to-speak-for-you"><div class="cover"><a aria-label="Watch I Won’t Pretend to Speak for You" href="/GhostHeart_Videos.html#film-i-wont-pretend-to-speak-for-you"><img alt="I Won’t Pretend to Speak for You — GhostHeart release artwork" height="1080" src="/assets/releases/i-wont-pretend-cover.jpg" width="1920" loading="lazy"/></a></div><div class="record-copy"><div class="record-meta"><span>Recording</span><span>You’re Not God</span></div><h3 id="new-release-title">I Won’t Pretend to Speak for You</h3><p>One marriage began beneath a church-house light, surrounded by every blessing people could give. Two women began with trembling hands and borrowed flowers.</p><p>Fifty years later, this song asks what a lifetime of love can tell us that appearances cannot.</p><div class="record-actions"><a class="g-link" href="/GhostHeart_Videos.html#film-i-wont-pretend-to-speak-for-you">Watch the music video</a><a class="g-link" href="/albums/youre-not-god/lyrics.html">Read the lyrics</a></div><p>From <a href="/albums/youre-not-god/index.html">You’re Not God →</a></p></div></article>'''
 data['recordings'].insert(0,{'id':ident,'title':'I Won’t Pretend to Speak for You','tracks':1,'html':record,'source':'GhostHeart_Songs.html release-spotlight at 988283c66051f75f08aba5fac0abbfe235b5ff89'})
 source.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Regenerate old-name compatibility anchors after the app-label migration, not during it.
projects=ROOT/'GhostHeart_Projects.html'
doc=BeautifulSoup(projects.read_text(),'html.parser')
for alias in doc.select('.l-anchor-alias'):alias.decompose()
projects.write_text(str(doc),encoding='utf-8')
runpy.run_path(str(ROOT/'.github/scripts/finish_gateway.py'))
soup=BeautifulSoup((ROOT/'GhostHeart_Songs.html').read_text(),'html.parser')
assert soup.select_one('#i-wont-pretend-to-speak-for-you.record-card h3'),'Featured recording must remain accessible'
assert {r['id'] for r in data['recordings']} <= {r['id'] for r in soup.select('.record-card')}
status=ROOT/'.github/GATEWAY_STATUS.md'
status.write_text(status.read_text().replace('Build command: python3 .github/scripts/finish_gateway.py.','Build command: python3 .github/scripts/build_site.py.'),encoding='utf-8')
print('Complete build preserved the earlier featured recording as well as the archive.')
