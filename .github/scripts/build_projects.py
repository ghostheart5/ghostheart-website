#!/usr/bin/env python3
"""Build the approved GhostHeart Studios projects overview."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HOME = (ROOT / 'index.html').read_text(encoding='utf-8')

def shell_piece(value):
    value = re.sub(r' aria-current="[^"]*"', '', value)
    value = re.sub(r'href="#([^"]+)"', r'href="/index.html#\1"', value)
    return re.sub(r'(href|src)="(?!https?:|/|#)([^"]+)"', r'\1="/\2"', value)

header = shell_piece(re.search(r'<header\b.*?</header>', HOME, re.S).group())
header = header.replace('<a href="/GhostHeart_Projects.html">Projects</a>', '<a aria-current="page" href="/GhostHeart_Projects.html">Projects</a>')
footer = shell_piece(re.search(r'<footer\b.*?</footer>', HOME, re.S).group())

body = '''<div class="projects-page">
<section class="projects-intro ghx-wrap" aria-labelledby="projects-title"><p class="ghx-kicker">GhostHeart Studios / Projects</p>
<h1 id="projects-title">Build something<br/><em>that helps.</em></h1>
<p class="projects-lead">The songs make room for a feeling. These projects ask what a person might need next: a clearer choice, a private place to reflect, or a way to create.</p>
<p class="projects-principle">Real people. Their own words. Their own next step.</p></section>

<section class="projects-axiomara" id="axiomara" aria-labelledby="axiomara-title"><div class="ghx-wrap projects-feature-grid">
<div class="projects-feature-main"><p class="projects-status projects-status-live">Available on Google Play</p><p class="projects-index">01 / A tool for the next move</p>
<h2 id="axiomara-title">AXIOMARA<span aria-hidden="true">.</span></h2>
<p class="projects-feature-lead">When everything feels urgent, find one move you can actually make.</p>
<p>Axiomara brings goals, tasks, time, energy, notes, and the context you choose into planning you can inspect. Ask what to do next, make the step smaller, or compare paths before you decide.</p>
<p>It is designed to help a crowded day feel more manageable and to leave the choice in your hands.</p>
<a class="projects-button" href="https://play.google.com/store/apps/details?id=com.ghostheart5.chronospark" target="_blank" rel="noopener noreferrer">Explore Axiomara on Google Play <span aria-hidden="true">↗</span></a>
<p class="projects-boundary">A planning and decision tool for adults; it does not replace professional or emergency support.</p></div>
<div class="projects-signal" aria-label="Axiomara approach"><p>BRING THE REALITY</p><strong>Goals. Time. Energy.</strong>
<p>SEE THE REASON</p><strong>A move you can inspect.</strong>
<p>KEEP THE CONTROL</p><strong>Accept it. Change it. Choose again.</strong></div>
</div></section>

<section class="projects-shadow ghx-wrap" aria-labelledby="shadow-title"><div class="projects-shadow-frame"><div>
<p class="projects-status projects-status-work">In progress</p><p class="projects-index">02 / A space for your own words</p>
<h2 id="shadow-title">SHADOW FIRE<span aria-hidden="true">.</span></h2>
<p class="projects-feature-lead">A private place to notice what you carry and decide what belongs in your story.</p>
<p>Shadow Fire is being built around writing and guided reflection, a Life Book for the pages someone chooses to keep, and Vault controls for reviewing their own records. The aim is to help people see patterns and move at their own pace, with their words and choices under their control.</p>
<p class="projects-work-note">In development. There is no public download or live service here yet.</p></div>
<div class="projects-shadow-mark" aria-hidden="true"><span>WRITE</span><span>REFLECT</span><span>CHOOSE</span></div></div></section>

<section class="projects-future ghx-wrap" aria-labelledby="future-title"><p class="ghx-kicker">What could come next</p>
<h2 id="future-title">Under construction<span aria-hidden="true">.</span></h2>
<p>GhostHeart Studios is exploring more ways to make, play, and carry a story. These are directions, not announced products or launch dates.</p>
<div class="projects-future-grid"><article><span>01 / SOUND</span><h3>Music Studio</h3><p>Room to shape sounds and make something that feels like your own.</p></article>
<article><span>02 / PLAY</span><h3>Games</h3><p>Stories and choices you might one day step inside.</p></article>
<article><span>03 / IDENTITY</span><h3>Brands</h3><p>Visual worlds and identities built with intention.</p></article></div></section>

<aside class="projects-close ghx-wrap"><p class="ghx-kicker">The measure</p><h2>Make it human.<br/>Make it useful.</h2>
<p>Ambition matters here. So do privacy, clarity, and the freedom to choose what comes next.</p>
<div class="projects-close-links"><a href="/GhostHeart_Version_Mission.html">Read the mission</a><a href="/GhostHeart_Resources.html">Help &amp; Resources</a><a href="/index.html#join-the-signal">Stay Connected</a></div></aside>
</div>'''

html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Projects | GhostHeart Studios</title><meta name="description" content="Meet Axiomara, explore Shadow Fire in development, and see what GhostHeart Studios is building next."/>
<link rel="canonical" href="https://www.myghostheart.com/GhostHeart_Projects.html"/><link rel="icon" href="/favicon.ico"/>
<link rel="stylesheet" href="/assets/shared/release-site.css"/><link rel="stylesheet" href="/assets/shared/ghostheart-world.css"/>
<link rel="stylesheet" href="/assets/projects/projects.css"/><script defer src="/assets/shared/ghostheart-world.js"></script>
</head><body class="ghx-site"><a class="skip-link" href="#main-content">Skip to content</a>{header}
<main id="main-content">{body}</main>{footer}</body></html>\n'''
(ROOT / 'GhostHeart_Projects.html').write_text(html, encoding='utf-8', newline='\n')
print('Built Projects: Axiomara, Shadow Fire, and three under-construction directions')
