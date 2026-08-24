(() => {
  const catalog = window.GHOSTHEART_VIDEO_CATALOG || [];
  const records = new Map(catalog.map((item) => [item.key, item]));
  const youtubePlayers = new Map();
  let youtubeReady;

  const youtubeThumbnail = (id) => `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
  const playerStatus = (card) => card.querySelector('.player-status');

  const pauseOthers = (activeKey) => {
    document.querySelectorAll('video[data-video-key]').forEach((video) => {
      if (video.dataset.videoKey !== activeKey && !video.paused) video.pause();
    });
    youtubePlayers.forEach((player, key) => {
      if (key !== activeKey && typeof player.pauseVideo === 'function') player.pauseVideo();
    });
  };

  const linkMarkup = (link, primary = false) => `<a class="button${primary ? ' primary' : ''}" href="${link.href}"${link.accessibleLabel ? ` aria-label="${link.accessibleLabel}"` : ''}>${link.label}</a>`;

  const shellMarkup = (item) => {
    if (item.provider === 'youtube') {
      return `<div class="media-player-shell" data-provider="youtube" data-video-key="${item.key}" data-started="false">
        <button class="youtube-preview" type="button" data-video-action="play" aria-label="Play ${item.videoTitle} here">
          <img src="${youtubeThumbnail(item.youtubeId)}" alt="Official YouTube thumbnail for ${item.videoTitle}" width="480" height="360" loading="lazy" decoding="async">
        </button>
        <span class="player-title-strip">${item.title}</span>
        <span class="player-launch" aria-hidden="true">Play here</span>
        <button class="player-replay" type="button" data-video-action="replay" hidden>Replay</button>
      </div>`;
    }
    return `<div class="media-player-shell" data-provider="native" data-video-key="${item.key}" data-started="false">
      <video controls preload="metadata" playsinline aria-label="GhostHeart video: ${item.videoTitle}" data-video-key="${item.key}"><source src="${item.src}" type="${item.mime}">Your browser does not support video playback.</video>
      <span class="player-title-strip">${item.title}</span>
      <button class="player-launch" type="button" data-video-action="play" aria-label="Play ${item.videoTitle} here">Play here</button>
      <button class="player-replay" type="button" data-video-action="replay" hidden>Replay</button>
    </div>`;
  };

  const copyMarkup = (item, featured) => {
    const related = item.related.map((link) => linkMarkup(link)).join('');
    const relationship = item.relationship ? `<aside class="relationship-card" aria-label="${item.relationship.kicker}"><p class="relationship-kicker">${item.relationship.kicker}</p><h4>${item.relationship.title}</h4><p>${item.relationship.copy}</p><div class="relationship-actions">${linkMarkup(item.relationship.link)}</div></aside>` : '';
    return `<div class="${featured ? 'featured-copy' : 'video-copy'}">
      <div class="video-meta">${item.meta.map((value) => `<span>${value}</span>`).join('')}</div>
      <h3>${item.title}</h3>
      <p>${item.description}</p>
      <div class="button-row"><button class="button${featured ? ' primary' : ''}" type="button" data-video-action="play">Play here</button>${linkMarkup(item.song)}${related}</div>
      <p class="player-status" role="status" aria-live="polite">Ready to play on this page.</p>
      <details class="media-access"><summary>Captions and transcript</summary><p>${item.accessibility}</p></details>
      ${relationship}
    </div>`;
  };

  const renderShell = (article) => {
    const item = records.get(article.dataset.mediaKey);
    if (!item) {
      article.textContent = 'This video record is unavailable.';
      return;
    }
    article.className = item.featured ? 'featured-film' : 'video-card';
    article.innerHTML = `${shellMarkup(item)}${copyMarkup(item, item.featured)}`;
    const video = article.querySelector('video');
    if (!video) return;
    video.addEventListener('loadedmetadata', () => {
      if (video.duration > .1 && video.currentTime === 0) video.currentTime = .05;
    }, { once: true });
    video.addEventListener('play', () => {
      pauseOthers(item.key);
      article.querySelector('.media-player-shell').dataset.started = 'true';
      article.querySelector('.player-replay').hidden = true;
      playerStatus(article).textContent = `Playing ${item.title}.`;
    });
    video.addEventListener('pause', () => {
      if (!video.ended && video.currentTime > .1) playerStatus(article).textContent = `${item.title} paused. The paused frame remains visible.`;
    });
    video.addEventListener('ended', () => {
      article.querySelector('.player-replay').hidden = false;
      playerStatus(article).textContent = `${item.title} ended. Replay starts the same video.`;
    });
    video.addEventListener('error', () => {
      playerStatus(article).textContent = `${item.title} could not be loaded from its website file.`;
    });
  };

  const loadYoutube = () => {
    if (window.YT?.Player) return Promise.resolve(window.YT);
    if (youtubeReady) return youtubeReady;
    youtubeReady = new Promise((resolve, reject) => {
      const previous = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = () => {
        if (typeof previous === 'function') previous();
        resolve(window.YT);
      };
      const script = document.createElement('script');
      script.src = 'https://www.youtube.com/iframe_api';
      script.async = true;
      script.onerror = () => reject(new Error('YouTube player API unavailable'));
      document.head.append(script);
    });
    return youtubeReady;
  };

  const showYoutubeError = (article, item, code) => {
    const shell = article.querySelector('.media-player-shell');
    shell.innerHTML = `<div class="player-error"><strong>${item.title} cannot play here.</strong><p>YouTube returned error ${code}. If the error is 101 or 150, embedding must be enabled for video ${item.youtubeId}, or an exact approved native file must be hosted by GhostHeart.</p></div>`;
    playerStatus(article).textContent = `${item.title} is unavailable inside the website.`;
  };

  const startYoutube = async (article, item) => {
    const existing = youtubePlayers.get(item.key);
    if (existing) {
      pauseOthers(item.key);
      existing.playVideo();
      return;
    }
    const shell = article.querySelector('.media-player-shell');
    const status = playerStatus(article);
    status.textContent = `Loading ${item.title} inside GhostHeart…`;
    shell.dataset.started = 'true';
    const preview = shell.querySelector('.youtube-preview');
    const host = document.createElement('div');
    host.className = 'youtube-host';
    host.id = `youtube-${item.key}`;
    preview.replaceWith(host);
    try {
      const YT = await loadYoutube();
      const player = new YT.Player(host.id, {
        host: 'https://www.youtube-nocookie.com',
        videoId: item.youtubeId,
        playerVars: { autoplay: 1, controls: 1, playsinline: 1, rel: 0, cc_load_policy: 1 },
        events: {
          onReady: (event) => { event.target.getIframe().title = `GhostHeart video: ${item.videoTitle}`; youtubePlayers.set(item.key, event.target); pauseOthers(item.key); event.target.playVideo(); },
          onStateChange: (event) => {
            if (event.data === YT.PlayerState.PLAYING) { shell.querySelector('.player-replay').hidden = true; status.textContent = `Playing ${item.title}.`; }
            if (event.data === YT.PlayerState.PAUSED) status.textContent = `${item.title} paused. The paused frame remains visible.`;
            if (event.data === YT.PlayerState.ENDED) { shell.querySelector('.player-replay').hidden = false; status.textContent = `${item.title} ended. Replay starts the same video.`; }
          },
          onError: (event) => showYoutubeError(article, item, event.data)
        }
      });
      youtubePlayers.set(item.key, player);
    } catch (error) {
      showYoutubeError(article, item, 'API');
    }
  };

  const playRecord = async (article, replay = false) => {
    const item = records.get(article.dataset.mediaKey);
    if (!item) return;
    if (item.provider === 'youtube') {
      const player = youtubePlayers.get(item.key);
      if (replay && player?.seekTo) { player.seekTo(0, true); player.playVideo(); article.querySelector('.player-replay').hidden = true; return; }
      await startYoutube(article, item);
      return;
    }
    const video = article.querySelector('video');
    if (replay) video.currentTime = 0;
    pauseOthers(item.key);
    video.focus({ preventScroll: true });
    try { await video.play(); } catch (error) { video.controls = true; playerStatus(article).textContent = `Use the ${item.title} player control to begin.`; }
  };

  document.querySelectorAll('[data-media-key]').forEach(renderShell);
  const films = [...document.querySelectorAll('.video-card')];
  const archiveToggle = document.getElementById('video-archive-toggle');
  const setArchiveOpen = (open) => {
    films.forEach((card, index) => { card.hidden = !open && index >= 6; });
    archiveToggle.setAttribute('aria-expanded', String(open));
    archiveToggle.textContent = open ? 'Show fewer films' : `View all ${films.length} films`;
  };
  const revealLinkedFilm = () => {
    const target = window.location.hash ? document.getElementById(window.location.hash.slice(1)) : null;
    const card = target?.closest('.video-card');
    setArchiveOpen(card ? films.indexOf(card) >= 6 : false);
  };
  revealLinkedFilm();
  window.addEventListener('hashchange', revealLinkedFilm);
  archiveToggle.addEventListener('click', () => setArchiveOpen(archiveToggle.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('click', (event) => {
    const action = event.target.closest('[data-video-action]');
    if (!action) return;
    const article = action.closest('[data-media-key]');
    playRecord(article, action.dataset.videoAction === 'replay');
  });
})();
