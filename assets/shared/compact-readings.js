/* Progressive enhancement: complete prose remains available without JavaScript. */
(() => {
  const continuation = document.querySelector('#behind-the-scars .reading-continuation');
  if (continuation) {
    continuation.id = 'scars-full-reading';
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'reading-toggle';
    toggle.setAttribute('aria-controls', continuation.id);
    const setExpanded = expanded => {
      continuation.hidden = !expanded;
      toggle.setAttribute('aria-expanded', String(expanded));
      toggle.textContent = expanded ? 'Read less' : 'Read more';
    };
    continuation.before(toggle);
    setExpanded(false);
    toggle.addEventListener('click', () => setExpanded(continuation.hidden));
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'reading-toggle';
    close.textContent = 'Read less';
    close.setAttribute('aria-controls', continuation.id);
    close.addEventListener('click', () => { setExpanded(false); toggle.focus(); });
    continuation.append(close);
    // Preserve links to any anchor within the full reading.
    const reveal = () => {
      let id;
      try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
      const target = document.getElementById(id);
      if (target && continuation.contains(target)) {
        setExpanded(true);
        target.scrollIntoView();
      }
    };
    addEventListener('hashchange', reveal);
    reveal();
  }
  const rows = [...document.querySelectorAll('details.p')];
  const revealPassage = () => {
    const row = rows.find(item => '#' + item.id === location.hash);
    if (row) { row.open = true; row.scrollIntoView(); }
  };
  addEventListener('hashchange', revealPassage);
  revealPassage();
})();
