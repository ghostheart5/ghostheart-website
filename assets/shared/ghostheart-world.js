// Apply the approved GhostHeart Awakening canon after the legacy shared layer.
(() => {
  if (document.querySelector('link[href$="ghostheart-awakening.css"]')) return;
  const canon = document.createElement('link');
  canon.rel = 'stylesheet';
  canon.href = new URL('ghostheart-awakening.css', document.currentScript.src).href;
  const reviewTheme = document.querySelector('link[href$="review-theme.css"]');
  if (reviewTheme) reviewTheme.before(canon);
  else document.head.appendChild(canon);
})();

// Load website analytics only on the public GhostHeart domain, not local previews.
(() => {
  if (!['www.myghostheart.com', 'myghostheart.com'].includes(location.hostname)) return;
  if (document.getElementById('ghostheart-metricool')) return;
  const tracker = document.createElement('script');
  tracker.id = 'ghostheart-metricool';
  tracker.async = true;
  tracker.src = 'https://tracker.metricool.com/resources/be.js';
  tracker.onload = () => {
    if (typeof window.beTracker?.t === 'function') {
      window.beTracker.t({ hash: '9e25430c6db07385d4e58579695b9e8b' });
    }
  };
  document.head.appendChild(tracker);
})();

// Keep the hand-curated Films archive intact while placing newly reconciled
// public releases from the official catalog at the front of the collection.
(() => {
  const library = document.querySelector('.ghx-film-library');
  const catalog = window.GHOSTHEART_VIDEO_CATALOG;
  if (!library || !Array.isArray(catalog)) return;

  const existingIds = new Set(
    [...library.querySelectorAll('[data-film-id]')].map(button => button.dataset.filmId)
  );
  const newReleases = catalog.filter(item =>
    item.provider === 'youtube' && item.youtubeId && !existingIds.has(item.youtubeId)
  ).slice(0, 8);
  if (!newReleases.length) return;

  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
  const cards = newReleases.map((item, index) => {
    const title = escapeHtml(item.title);
    const videoTitle = escapeHtml(item.videoTitle || item.title);
    const description = escapeHtml(item.description);
    const thumbnail = escapeHtml(item.thumbnail);
    const youtubeId = escapeHtml(item.youtubeId);
    const meta = escapeHtml(item.meta?.join(' · ') || (index < 3 ? 'New release' : 'New Short'));
    const songHref = escapeHtml(item.song?.href || 'start/index.html');
    const songLabel = escapeHtml(item.song?.label || 'Start here');
    const search = escapeHtml(`${item.title} ${item.videoTitle || ''} ${item.description} ${(item.meta || []).join(' ')}`.toLowerCase());
    return `<article class="ghx-film" data-film-card data-search="${search}" id="${escapeHtml(item.cardId || `film-${item.key}`)}">
      <div class="film-frame"><button type="button" aria-label="Load video: ${videoTitle}" data-film-id="${youtubeId}" data-film-title="${videoTitle}"><img src="${thumbnail}" alt="" width="1280" height="720" loading="lazy"><span class="film-play" aria-hidden="true">▶</span><span class="film-label">Play film</span></button></div>
      <div class="ghx-film-copy"><p class="ghx-kicker">${meta}</p><h3>${title}</h3><p>${description}</p><div class="ghx-actions"><a href="https://www.youtube.com/watch?v=${youtubeId}" target="_blank" rel="noopener noreferrer">YouTube ↗</a><a href="${songHref}">${songLabel} ↗</a></div></div>
    </article>`;
  }).join('');

  library.insertAdjacentHTML('afterbegin', cards);
  const status = document.getElementById('film-results');
  if (status) {
    const count = library.querySelectorAll('[data-film-card]').length;
    status.textContent = `${count} ${count === 1 ? 'film' : 'films'}`;
  }
})();

(() => {
  const header = document.querySelector('.ghx-header');
  const toggle = header?.querySelector('.ghx-menu-toggle');
  const menu = header?.querySelector('#gateway-menu');
  if (toggle && menu && header.dataset.navOwner === 'shared') {
    const setOpen = open => {
      toggle.setAttribute('aria-expanded', String(open));
      menu.hidden = !open;
    };
    toggle.addEventListener('click', () => setOpen(menu.hidden));
    menu.addEventListener('click', event => { if (event.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !menu.hidden) { setOpen(false); toggle.focus(); }
    });
    document.addEventListener('click', event => {
      if (!menu.hidden && !header.contains(event.target)) setOpen(false);
    });
  }
  const search = document.getElementById('film-search');
  const cards = [...document.querySelectorAll('[data-film-card]')];
  const status = document.getElementById('film-results');
  const empty = document.getElementById('film-empty');
  const normalize = value => value.normalize('NFKD').toLowerCase().replace(/[’']/g, '').trim();
  const filter = () => {
    const words = normalize(search.value).split(/\s+/).filter(Boolean);
    let count = 0;
    cards.forEach(card => {
      card.hidden = !words.every(word => normalize(card.dataset.search).includes(word));
      if (card.hidden) {
        card.querySelector('iframe')?.remove();
        const play = card.querySelector('[data-film-id]');
        if (play) play.hidden = false;
      }
      if (!card.hidden) count++;
    });
    status.textContent = `${count} ${count === 1 ? 'film' : 'films'}`;
    empty.hidden = count > 0;
  };
  search?.addEventListener('input', filter);
  const revealHash = () => {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target?.matches('[data-film-card]') && search?.value) {
      search.value = ''; filter(); target.scrollIntoView({block:'start'});
    }
  };
  window.addEventListener('hashchange', revealHash);
  document.querySelectorAll('.film-frame').forEach(frame => {
    const close = document.createElement('button');
    close.type = 'button'; close.className = 'ghx-close-film'; close.textContent = 'Close player'; close.hidden = true;
    frame.after(close);
    new MutationObserver(() => { close.hidden = !frame.querySelector('iframe'); }).observe(frame,{childList:true});
    close.addEventListener('click', () => {
      frame.querySelector('iframe')?.remove();
      const play = frame.querySelector('[data-film-id]');
      if (play) { play.hidden = false; play.focus(); }
    });
  });
})();
