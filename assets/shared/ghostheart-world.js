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
