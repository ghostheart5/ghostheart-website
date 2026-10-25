// A different welcome for each place a visitor comes from, so the homepage continues
// what they just saw instead of repeating it. Reads only the page's own URL
// (utm_source or ?from=) and a visit counter kept in this browser. No network requests.
(function () {
  var box = document.querySelector('[data-arrival]');
  if (!box) return;
  var ROUTES = {
    tiktok: ['From TikTok', 'You caught the moment. Here’s the whole song and the film it came from.', '#latest', 'Watch the full story'],
    instagram: ['From Instagram', 'You saw the art. Now meet the man it came from.', '#home-story', 'Meet the man'],
    youtube: ['From YouTube', 'You watched the film. Read the life behind it.', '/GhostHeart_Story.html#behind-the-scars', 'Read Behind the Scars'],
    x: ['From X', 'You read the studio notes. Here’s what’s finished and playing now.', '#latest', 'Play what’s new'],
    bluesky: ['From Bluesky', 'Thanks for the conversation. Here are the stories behind the work.', '/journal/', 'Open the Journal'],
    pinterest: ['From Pinterest', 'You saved the line. Hear the song it came from.', '/music/', 'Hear the music'],
    reddit: ['From Reddit', 'Welcome—no pitch. Here’s what GhostHeart is, in one minute.', '#home-story', 'See what this is'],
    discord: ['Welcome back', 'Good to see you. Today’s line is waiting.', '#home-vault', 'Today’s line'],
    spotify: ['From Spotify', 'You heard it. Now see the story the song is telling.', '#home-story', 'The story behind it'],
    email: ['From your inbox', 'Thanks for opening. Here’s today’s line.', '#home-vault', 'Today’s line']
  };
  var ALIASES = { twitter: 'x', 't.co': 'x', ig: 'instagram', yt: 'youtube', mailchimp: 'email', newsletter: 'email', bsky: 'bluesky' };

  function safe(fn, fallback) { try { return fn(); } catch (e) { return fallback; } }
  var params = safe(function () { return new URLSearchParams(location.search); }, null);
  var source = params ? (params.get('utm_source') || params.get('from') || '') : '';
  source = source.toLowerCase().replace(/[^a-z0-9.]/g, '');
  source = ALIASES[source] || source;

  var visits = safe(function () {
    var n = (parseInt(localStorage.getItem('gh-visits') || '0', 10) || 0) + 1;
    localStorage.setItem('gh-visits', String(n));
    return n;
  }, 1);
  var dismissed = safe(function () { return sessionStorage.getItem('gh-arrival-closed') === '1'; }, false);
  if (dismissed) return;

  var route = ROUTES[source];
  if (!route && visits > 1) route = ['Welcome back', 'You came back. Today’s line is new.', '#home-vault', 'Today’s line'];
  if (!route) return;

  box.querySelector('[data-arrival-from]').textContent = route[0];
  box.querySelector('[data-arrival-text]').textContent = route[1];
  var link = box.querySelector('[data-arrival-link]');
  link.setAttribute('href', route[2]);
  link.textContent = route[3] + ' →';
  box.hidden = false;
  box.querySelector('[data-arrival-close]').addEventListener('click', function () {
    box.hidden = true;
    safe(function () { sessionStorage.setItem('gh-arrival-closed', '1'); });
  });
})();
