#!/usr/bin/env bash

set -e

PROJECT_NAME="ghostheart-website"

echo ""
echo "=========================================="
echo "   GHOSTHEART WEBSITE BUILD SCRIPT"
echo "   Theme: Crimson Void"
echo "=========================================="
echo ""

if [ -d "$PROJECT_NAME" ]; then
  echo "Folder '$PROJECT_NAME' already exists."
  echo "Stopping so I do not overwrite your work."
  exit 1
fi

echo "Creating project folders..."

mkdir -p "$PROJECT_NAME"
mkdir -p "$PROJECT_NAME/css"
mkdir -p "$PROJECT_NAME/js"
mkdir -p "$PROJECT_NAME/assets"
mkdir -p "$PROJECT_NAME/assets/images"
mkdir -p "$PROJECT_NAME/assets/videos"
mkdir -p "$PROJECT_NAME/assets/music"

echo "Creating index.html..."

cat > "$PROJECT_NAME/index.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>GhostHeart | Crimson Void Universe</title>

  <meta
    name="description"
    content="GhostHeart is a dark-neon universe of music, quotes, stories, and tools for the broken, rebuilding, and becoming."
  />

  <link rel="stylesheet" href="css/ghostheart.css" />
</head>

<body>
  <div class="site-shell">

    <header class="topbar">
      <a class="brand" href="index.html">GHOSTHEART</a>

      <nav class="nav">
        <a href="index.html">Home</a>
        <a href="story.html">Story</a>
        <a href="music.html">Music</a>
        <a href="quotes.html">Quotes</a>
        <a href="projects.html">Projects</a>
        <a href="join.html">Join</a>
      </nav>
    </header>

    <main>
      <section class="hero">
        <div class="hero-glow"></div>

        <div class="hero-content">
          <p class="eyebrow">Crimson Void Transmission</p>

          <h1>GHOSTHEART</h1>

          <p class="hero-subtitle">
            For the broken. For the rebuilding. For the hearts that refused to go dark.
          </p>

          <p class="hero-copy">
            Music. Quotes. Stories. Tools. A dark-neon universe built from chaos,
            identity, time, fire, and survival.
          </p>

          <div class="hero-actions">
            <a class="button primary" href="story.html">Enter The Story</a>
            <a class="button secondary" href="music.html">Hear The Music</a>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-heading">
          <p class="eyebrow">Start Here</p>
          <h2>What is GhostHeart?</h2>
        </div>

        <div class="feature-grid">
          <article class="card">
            <h3>Music</h3>
            <p>
              Songs made from pain, power, identity, chaos, and rebuilding.
              Your YouTube songs live here as the official GhostHeart archive.
            </p>
            <a href="music.html">Open Music Vault</a>
          </article>

          <article class="card">
            <h3>Quotes</h3>
            <p>
              Original GhostHeart quotes signed with your name and turned into a living
              quote vault people can come back to.
            </p>
            <a href="quotes.html">Open Quote Vault</a>
          </article>

          <article class="card">
            <h3>Projects</h3>
            <p>
              ChronoSpark, Shadowfire, and future GhostHeart tools live here without
              taking over the whole brand.
            </p>
            <a href="projects.html">View Projects</a>
          </article>
        </div>
      </section>

      <section class="section split">
        <div>
          <p class="eyebrow">Featured Signal</p>
          <h2>The heart still glows.</h2>
          <p>
            GhostHeart is not just an app brand. It is the universe around the music,
            quotes, stories, and tools you are building.
          </p>
        </div>

        <div class="signal-box">
          <p class="quote-mark">"</p>
          <p class="featured-quote">
            The world told me to hide my heart, so I taught it how to glow.
          </p>
          <p class="quote-signature">- GhostHeart</p>
        </div>
      </section>

      <section class="section cta-panel">
        <p class="eyebrow">Join The Signal</p>
        <h2>Follow the universe before it becomes loud.</h2>
        <p>
          New songs, quotes, story drops, ChronoSpark updates, Shadowfire updates,
          and future GhostHeart releases.
        </p>
        <a class="button primary" href="join.html">Join GhostHeart Signal</a>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; <span id="year"></span> GhostHeart. Built in the Crimson Void.</p>
    </footer>

  </div>

  <script src="js/ghostheart.js"></script>
</body>
</html>
EOF

echo "Creating story.html..."

cat > "$PROJECT_NAME/story.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>Story | GhostHeart</title>

  <link rel="stylesheet" href="css/ghostheart.css" />
</head>

<body>
  <div class="site-shell">

    <header class="topbar">
      <a class="brand" href="index.html">GHOSTHEART</a>

      <nav class="nav">
        <a href="index.html">Home</a>
        <a href="story.html">Story</a>
        <a href="music.html">Music</a>
        <a href="quotes.html">Quotes</a>
        <a href="projects.html">Projects</a>
        <a href="join.html">Join</a>
      </nav>
    </header>

    <main class="page">
      <section class="page-hero">
        <p class="eyebrow">Origin File</p>
        <h1>The Story of GhostHeart</h1>
        <p>
          A dark-neon myth about a heart that was judged, cracked, hidden,
          and still refused to stop glowing.
        </p>
      </section>

      <section class="timeline">
        <article class="timeline-card">
          <span>01</span>
          <h2>The Beginning</h2>
          <p>
            Before GhostHeart became a symbol, there was only a glowing heart
            the world did not understand.
          </p>
        </article>

        <article class="timeline-card">
          <span>02</span>
          <h2>The Glow</h2>
          <p>
            Every feeling made the light stronger. Every wound became a pulse.
            Every silence became a signal.
          </p>
        </article>

        <article class="timeline-card">
          <span>03</span>
          <h2>The Cracks</h2>
          <p>
            The world tried to make the heart smaller. Instead, the cracks
            became the places where the red light escaped.
          </p>
        </article>

        <article class="timeline-card">
          <span>04</span>
          <h2>The Silence</h2>
          <p>
            GhostHeart learned what it meant to disappear, to survive quietly,
            and to rebuild without applause.
          </p>
        </article>

        <article class="timeline-card">
          <span>05</span>
          <h2>The Rebuilding</h2>
          <p>
            The story became music. The music became quotes. The quotes became
            a universe. The universe became GhostHeart.
          </p>
        </article>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; <span id="year"></span> GhostHeart. Built in the Crimson Void.</p>
    </footer>

  </div>

  <script src="js/ghostheart.js"></script>
</body>
</html>
EOF

echo "Creating music.html..."

cat > "$PROJECT_NAME/music.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>Music | GhostHeart</title>

  <link rel="stylesheet" href="css/ghostheart.css" />
</head>

<body>
  <div class="site-shell">

    <header class="topbar">
      <a class="brand" href="index.html">GHOSTHEART</a>

      <nav class="nav">
        <a href="index.html">Home</a>
        <a href="story.html">Story</a>
        <a href="music.html">Music</a>
        <a href="quotes.html">Quotes</a>
        <a href="projects.html">Projects</a>
        <a href="join.html">Join</a>
      </nav>
    </header>

    <main class="page">
      <section class="page-hero">
        <p class="eyebrow">Audio Archive</p>
        <h1>GhostHeart Music</h1>
        <p>
          Add your YouTube songs here. Each song should have a video,
          meaning, quote, and emotional chapter.
        </p>
      </section>

      <section class="music-grid">

        <article class="song-card">
          <div class="video-frame">
            <iframe
              src="https://www.youtube.com/embed/REPLACE_WITH_VIDEO_ID"
              title="GhostHeart Song"
              loading="lazy"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen
            ></iframe>
          </div>

          <div class="song-content">
            <h2>Song Title</h2>
            <p class="tag">Pain / Rebuilding / Crimson Void</p>
            <p>
              Replace this with what the song means, what inspired it,
              and what part of the GhostHeart story it belongs to.
            </p>
          </div>
        </article>

        <article class="song-card">
          <div class="video-frame empty-video">
            <p>Add Next YouTube Embed</p>
          </div>

          <div class="song-content">
            <h2>Next Song</h2>
            <p class="tag">Identity / Fire / Survival</p>
            <p>
              Duplicate this card for every song you already uploaded.
            </p>
          </div>
        </article>

      </section>
    </main>

    <footer class="footer">
      <p>&copy; <span id="year"></span> GhostHeart. Built in the Crimson Void.</p>
    </footer>

  </div>

  <script src="js/ghostheart.js"></script>
</body>
</html>
EOF

echo "Creating quotes.html..."

cat > "$PROJECT_NAME/quotes.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>Quotes | GhostHeart</title>

  <link rel="stylesheet" href="css/ghostheart.css" />
</head>

<body>
  <div class="site-shell">

    <header class="topbar">
      <a class="brand" href="index.html">GHOSTHEART</a>

      <nav class="nav">
        <a href="index.html">Home</a>
        <a href="story.html">Story</a>
        <a href="music.html">Music</a>
        <a href="quotes.html">Quotes</a>
        <a href="projects.html">Projects</a>
        <a href="join.html">Join</a>
      </nav>
    </header>

    <main class="page">
      <section class="page-hero">
        <p class="eyebrow">Quote Vault</p>
        <h1>GhostHeart Quotes</h1>
        <p>
          Put every quote you already posted here so the website becomes
          the permanent archive.
        </p>
      </section>

      <section class="quote-grid">

        <article class="quote-card">
          <p>
            The world told me to hide my heart, so I taught it how to glow.
          </p>
          <span>- GhostHeart</span>
        </article>

        <article class="quote-card">
          <p>
            Broken does not mean finished.
          </p>
          <span>- GhostHeart</span>
        </article>

        <article class="quote-card">
          <p>
            Chaos is not the end. Sometimes it is the raw material.
          </p>
          <span>- GhostHeart</span>
        </article>

        <article class="quote-card">
          <p>
            If they only saw your cracks, they missed where the light escaped.
          </p>
          <span>- GhostHeart</span>
        </article>

      </section>
    </main>

    <footer class="footer">
      <p>&copy; <span id="year"></span> GhostHeart. Built in the Crimson Void.</p>
    </footer>

  </div>

  <script src="js/ghostheart.js"></script>
</body>
</html>
EOF

echo "Creating projects.html..."

cat > "$PROJECT_NAME/projects.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>Projects | GhostHeart</title>

  <link rel="stylesheet" href="css/ghostheart.css" />
</head>

<body>
  <div class="site-shell">

    <header class="topbar">
      <a class="brand" href="index.html">GHOSTHEART</a>

      <nav class="nav">
        <a href="index.html">Home</a>
        <a href="story.html">Story</a>
        <a href="music.html">Music</a>
        <a href="quotes.html">Quotes</a>
        <a href="projects.html">Projects</a>
        <a href="join.html">Join</a>
      </nav>
    </header>

    <main class="page">
      <section class="page-hero">
        <p class="eyebrow">Connected Tools</p>
        <h1>GhostHeart Projects</h1>
        <p>
          The apps belong here, but they do not take over the whole website.
          GhostHeart stays the umbrella.
        </p>
      </section>

      <section class="project-list">

        <article class="project-card active">
          <div>
            <p class="status">In Testing</p>
            <h2>ChronoSpark</h2>
            <p>
              A planning and decision-support tool for turning chaos into clarity.
            </p>
          </div>
          <a class="button secondary" href="#">Add Link Later</a>
        </article>

        <article class="project-card">
          <div>
            <p class="status">In Development</p>
            <h2>Shadowfire</h2>
            <p>
              A dark-neon journal and reflection tool for turning emotion into meaning.
            </p>
          </div>
          <a class="button secondary" href="#">Coming Soon</a>
        </article>

        <article class="project-card future">
          <div>
            <p class="status">Future Parking Lot</p>
            <h2>Chaos / Pattern Games</h2>
            <p>
              Future experimental tools and games. Not the main focus yet.
            </p>
          </div>
        </article>

      </section>
    </main>

    <footer class="footer">
      <p>&copy; <span id="year"></span> GhostHeart. Built in the Crimson Void.</p>
    </footer>

  </div>

  <script src="js/ghostheart.js"></script>
</body>
</html>
EOF

echo "Creating join.html..."

cat > "$PROJECT_NAME/join.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>Join | GhostHeart</title>

  <link rel="stylesheet" href="css/ghostheart.css" />
</head>

<body>
  <div class="site-shell">

    <header class="topbar">
      <a class="brand" href="index.html">GHOSTHEART</a>

      <nav class="nav">
        <a href="index.html">Home</a>
        <a href="story.html">Story</a>
        <a href="music.html">Music</a>
        <a href="quotes.html">Quotes</a>
        <a href="projects.html">Projects</a>
        <a href="join.html">Join</a>
      </nav>
    </header>

    <main class="page">
      <section class="join-hero">
        <p class="eyebrow">GhostHeart Signal</p>

        <h1>Join Before The Signal Gets Loud</h1>

        <p>
          Get songs, quotes, story drops, ChronoSpark updates,
          Shadowfire updates, and future GhostHeart releases.
        </p>

        <form class="signup-form" action="#" method="post">
          <label for="email">Email Address</label>
          <input id="email" type="email" name="email" placeholder="you@example.com" required />
          <button type="submit">Join The Signal</button>
        </form>

        <p class="small-note">
          This form is visual for now. Connect it later to Mailchimp, ConvertKit,
          Buttondown, Beehiiv, Supabase, or another email service.
        </p>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; <span id="year"></span> GhostHeart. Built in the Crimson Void.</p>
    </footer>

  </div>

  <script src="js/ghostheart.js"></script>
</body>
</html>
EOF

echo "Creating css/ghostheart.css..."

cat > "$PROJECT_NAME/css/ghostheart.css" <<'EOF'
:root {
  --gh-black: #030303;
  --gh-black-2: #090909;
  --gh-red: #ff173d;
  --gh-red-2: #b80024;
  --gh-red-dark: #650014;
  --gh-white: #f7f7f7;
  --gh-muted: #a8a8a8;
  --gh-card: rgba(18, 18, 18, 0.88);
  --gh-border: rgba(255, 23, 61, 0.35);
  --gh-glow: 0 0 18px rgba(255, 23, 61, 0.75);
  --gh-glow-soft: 0 0 42px rgba(255, 23, 61, 0.35);
  --gh-max: 1180px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  color: var(--gh-white);
  background:
    radial-gradient(circle at 20% 20%, rgba(255, 23, 61, 0.16), transparent 30%),
    radial-gradient(circle at 80% 0%, rgba(184, 0, 36, 0.18), transparent 32%),
    linear-gradient(180deg, #030303 0%, #080008 50%, #030303 100%);
  font-family: "Segoe UI", Arial, sans-serif;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.8), transparent 85%);
  z-index: 0;
}

a {
  color: inherit;
}

.site-shell {
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

.topbar {
  width: min(var(--gh-max), calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.brand {
  color: var(--gh-white);
  font-weight: 900;
  letter-spacing: 0.22em;
  text-decoration: none;
  text-shadow: var(--gh-glow);
}

.nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 14px;
}

.nav a {
  color: var(--gh-muted);
  text-decoration: none;
  font-size: 0.95rem;
  transition: 0.2s ease;
}

.nav a:hover {
  color: var(--gh-red);
  text-shadow: var(--gh-glow);
}

.hero {
  min-height: calc(100vh - 86px);
  width: min(var(--gh-max), calc(100% - 32px));
  margin: 0 auto;
  display: grid;
  place-items: center;
  position: relative;
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  width: 520px;
  height: 520px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(255, 23, 61, 0.32), transparent 68%);
  filter: blur(8px);
  animation: pulseGlow 4s ease-in-out infinite;
}

.hero-content {
  position: relative;
  max-width: 900px;
  text-align: center;
  padding: 80px 0;
}

.eyebrow {
  margin: 0 0 14px;
  color: var(--gh-red);
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 0.82rem;
  font-weight: 800;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

.hero h1 {
  margin-bottom: 20px;
  font-size: clamp(3.6rem, 13vw, 9rem);
  line-height: 0.9;
  letter-spacing: 0.08em;
  color: var(--gh-red);
  text-shadow:
    0 0 8px rgba(255, 23, 61, 0.9),
    0 0 30px rgba(255, 23, 61, 0.65),
    0 0 80px rgba(255, 23, 61, 0.4);
}

.hero-subtitle {
  max-width: 780px;
  margin: 0 auto 18px;
  font-size: clamp(1.35rem, 3vw, 2.3rem);
  line-height: 1.25;
  font-weight: 800;
}

.hero-copy {
  max-width: 680px;
  margin: 0 auto;
  color: var(--gh-muted);
  font-size: 1.08rem;
  line-height: 1.8;
}

.hero-actions {
  margin-top: 34px;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 22px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 800;
  letter-spacing: 0.04em;
  border: 1px solid var(--gh-border);
  transition: 0.22s ease;
}

.button.primary {
  color: #120004;
  background: var(--gh-red);
  box-shadow: var(--gh-glow-soft);
}

.button.primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--gh-glow);
}

.button.secondary {
  color: var(--gh-white);
  background: rgba(255, 23, 61, 0.08);
}

.button.secondary:hover {
  color: var(--gh-red);
  border-color: var(--gh-red);
  box-shadow: var(--gh-glow-soft);
}

.section,
.page {
  width: min(var(--gh-max), calc(100% - 32px));
  margin: 0 auto;
}

.section {
  padding: 74px 0;
}

.section-heading {
  max-width: 700px;
  margin-bottom: 28px;
}

.section h2,
.page-hero h1,
.join-hero h1 {
  font-size: clamp(2rem, 5vw, 4.2rem);
  line-height: 1;
}

.section p,
.page-hero p,
.timeline-card p,
.card p,
.song-content p,
.project-card p,
.join-hero p {
  color: var(--gh-muted);
  line-height: 1.75;
}

.feature-grid,
.quote-grid,
.music-grid {
  display: grid;
  gap: 22px;
}

.feature-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.card,
.timeline-card,
.quote-card,
.song-card,
.project-card,
.signal-box,
.cta-panel,
.join-hero {
  background:
    linear-gradient(145deg, rgba(255, 23, 61, 0.09), rgba(255, 255, 255, 0.025)),
    var(--gh-card);
  border: 1px solid var(--gh-border);
  border-radius: 24px;
  box-shadow: 0 20px 70px rgba(0, 0, 0, 0.35);
}

.card {
  padding: 26px;
}

.card h3 {
  color: var(--gh-red);
  font-size: 1.4rem;
}

.card a {
  display: inline-block;
  margin-top: 12px;
  color: var(--gh-red);
  text-decoration: none;
  font-weight: 800;
}

.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
  align-items: center;
}

.signal-box {
  padding: 32px;
  position: relative;
  overflow: hidden;
}

.quote-mark {
  color: var(--gh-red);
  font-size: 6rem;
  line-height: 0.6;
  margin-bottom: 6px;
  text-shadow: var(--gh-glow);
}

.featured-quote {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--gh-white);
}

.quote-signature {
  color: var(--gh-red);
  font-weight: 800;
}

.cta-panel {
  padding: 42px;
  text-align: center;
}

.cta-panel p {
  max-width: 680px;
  margin-left: auto;
  margin-right: auto;
}

.page {
  padding: 60px 0 90px;
}

.page-hero {
  max-width: 860px;
  margin-bottom: 40px;
}

.timeline {
  display: grid;
  gap: 18px;
}

.timeline-card {
  padding: 28px;
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 18px;
}

.timeline-card span {
  color: var(--gh-red);
  font-size: 2.3rem;
  font-weight: 900;
  text-shadow: var(--gh-glow);
}

.quote-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.quote-card {
  padding: 30px;
}

.quote-card p {
  color: var(--gh-white);
  font-size: 1.35rem;
  font-weight: 800;
}

.quote-card span {
  color: var(--gh-red);
  font-weight: 800;
}

.music-grid {
  grid-template-columns: 1fr;
}

.song-card {
  overflow: hidden;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
}

.video-frame {
  min-height: 300px;
  background: #090909;
}

.video-frame iframe {
  width: 100%;
  height: 100%;
  min-height: 300px;
  border: 0;
  display: block;
}

.empty-video {
  display: grid;
  place-items: center;
  color: var(--gh-red);
  border-right: 1px solid var(--gh-border);
}

.song-content {
  padding: 28px;
}

.tag,
.status {
  color: var(--gh-red) !important;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.78rem;
}

.project-list {
  display: grid;
  gap: 18px;
}

.project-card {
  padding: 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 22px;
}

.project-card.active {
  border-color: rgba(255, 23, 61, 0.75);
  box-shadow: var(--gh-glow-soft);
}

.project-card.future {
  opacity: 0.75;
}

.join-hero {
  max-width: 780px;
  margin: 50px auto;
  padding: 38px;
  text-align: center;
}

.signup-form {
  margin: 32px auto 16px;
  display: grid;
  gap: 12px;
  max-width: 520px;
  text-align: left;
}

.signup-form label {
  color: var(--gh-red);
  font-weight: 800;
}

.signup-form input {
  width: 100%;
  min-height: 52px;
  padding: 0 16px;
  color: var(--gh-white);
  background: rgba(0, 0, 0, 0.42);
  border: 1px solid var(--gh-border);
  border-radius: 14px;
  outline: none;
}

.signup-form input:focus {
  border-color: var(--gh-red);
  box-shadow: var(--gh-glow-soft);
}

.signup-form button {
  min-height: 52px;
  border: 0;
  border-radius: 14px;
  color: #120004;
  background: var(--gh-red);
  font-weight: 900;
  cursor: pointer;
  box-shadow: var(--gh-glow-soft);
}

.signup-form button:hover {
  box-shadow: var(--gh-glow);
}

.small-note {
  font-size: 0.9rem;
}

.footer {
  width: min(var(--gh-max), calc(100% - 32px));
  margin: 0 auto;
  padding: 38px 0;
  color: var(--gh-muted);
  border-top: 1px solid rgba(255, 23, 61, 0.18);
}

@keyframes pulseGlow {
  0%,
  100% {
    transform: scale(0.94);
    opacity: 0.72;
  }

  50% {
    transform: scale(1.08);
    opacity: 1;
  }
}

@media (max-width: 860px) {
  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .nav {
    justify-content: flex-start;
  }

  .feature-grid,
  .split,
  .quote-grid,
  .song-card {
    grid-template-columns: 1fr;
  }

  .timeline-card {
    grid-template-columns: 1fr;
  }

  .project-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
EOF

echo "Creating js/ghostheart.js..."

cat > "$PROJECT_NAME/js/ghostheart.js" <<'EOF'
const yearTargets = document.querySelectorAll("#year");

yearTargets.forEach((target) => {
  target.textContent = new Date().getFullYear();
});

const signupForm = document.querySelector(".signup-form");

if (signupForm) {
  signupForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const emailInput = signupForm.querySelector("input[type='email']");
    const email = emailInput ? emailInput.value.trim() : "";

    if (!email) {
      alert("Enter your email first.");
      return;
    }

    alert("GhostHeart Signal placeholder is working. Connect this form to your email service later.");
    signupForm.reset();
  });
}
EOF

echo "Creating README.md..."

cat > "$PROJECT_NAME/README.md" <<'EOF'
# GhostHeart Website

Theme: GhostHeart Crimson Void

This is the official GhostHeart website scaffold.

## Pages

- Home
- Story
- Music
- Quotes
- Projects
- Join

## What to edit first

1. Replace the YouTube video ID in `music.html`.
2. Add your real GhostHeart quotes in `quotes.html`.
3. Add your real GhostHeart origin story in `story.html`.
4. Add real ChronoSpark and Shadowfire links in `projects.html`.
5. Connect the Join form to an email service later.

## Run locally

Open `index.html` in your browser.

Or use VS Code Live Server.

## Deploy

Use GitHub Pages after pushing this project to GitHub.
EOF

echo "Creating deploy-gh-pages.sh..."

cat > "$PROJECT_NAME/deploy-gh-pages.sh" <<'EOF'
#!/usr/bin/env bash

set -e

echo ""
echo "=========================================="
echo "   GHOSTHEART DEPLOY HELPER"
echo "=========================================="
echo ""

if [ ! -d ".git" ]; then
  echo "This folder is not a Git repo yet."
  echo "Run these first:"
  echo ""
  echo "git init"
  echo "git branch -M main"
  echo "git remote add origin YOUR_GITHUB_REPO_URL"
  echo ""
  exit 1
fi

git add .
git commit -m "Update GhostHeart website"
git push origin main

echo ""
echo "Deploy push complete."
echo "Now enable GitHub Pages in your repo settings."
echo ""
EOF

chmod +x "$PROJECT_NAME/deploy-gh-pages.sh"

echo ""
echo "=========================================="
echo "   GHOSTHEART WEBSITE CREATED"
echo "=========================================="
echo ""
echo "Folder created: $PROJECT_NAME"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Open index.html in browser OR use VS Code Live Server"
echo "3. Replace YouTube VIDEO_ID in music.html"
echo "4. Add your real quotes and story"
echo ""