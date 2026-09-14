(() => {
  const menuButton = document.querySelector('[data-menu-toggle]');
  const menu = document.getElementById('site-menu');
  const closeMenu = () => {
    if (!menuButton || !menu) return;
    menuButton.setAttribute('aria-expanded', 'false');
    menu.hidden = true;
  };
  menuButton?.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
    menu.hidden = !open;
  });
  menu?.addEventListener('click', (event) => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu && !menu.hidden) {
      closeMenu();
      menuButton.focus();
    }
  });
  document.querySelectorAll('[data-film-id]').forEach((button) => {
    button.addEventListener('click', () => {
      const id = button.dataset.filmId;
      if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return;
      document.querySelectorAll('.film-frame iframe').forEach((player) => {
        const frame = player.closest('.film-frame');
        player.remove();
        const previousButton = frame.querySelector('[data-film-id]');
        if (previousButton) previousButton.hidden = false;
      });
      const iframe = document.createElement('iframe');
      iframe.src = 'https://www.youtube-nocookie.com/embed/' + id + '?rel=0&playsinline=1';
      iframe.title = button.dataset.filmTitle || 'GhostHeart music video';
      iframe.allow = 'encrypted-media; picture-in-picture; fullscreen';
      iframe.allowFullscreen = true;
      iframe.referrerPolicy = 'strict-origin-when-cross-origin';
      button.hidden = true;
      button.closest('.film-frame').append(iframe);
      iframe.focus();
    });
  });
  const search = document.querySelector('[data-album-search]');
  const resultStatus = document.querySelector('[data-search-status]');
  search?.addEventListener('input', () => {
    const query = search.value.normalize('NFKD').toLowerCase().replace(/[’']/g, '').trim();
    let count = 0;
    document.querySelectorAll('[data-album-entry]').forEach((entry) => {
      const text = entry.dataset.searchText.normalize('NFKD').toLowerCase().replace(/[’']/g, '');
      entry.hidden = query !== '' && !text.includes(query);
      if (!entry.hidden) count += 1;
    });
    if (resultStatus) resultStatus.textContent = count ? count + (count === 1 ? ' album found' : ' albums found') : 'No albums found. Try a song title or another word.';
  });
})();
