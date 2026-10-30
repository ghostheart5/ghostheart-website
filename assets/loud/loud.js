/* LOUD redesign: keep in-page links clear of the fixed site header. */
(() => {
  const header = document.querySelector('header.ghx-header');
  if (!header) return;
  const set = () => document.documentElement.style.setProperty('--hdr', Math.ceil(header.getBoundingClientRect().height) + 8 + 'px');
  set();
  addEventListener('resize', set, { passive: true });
  if ('ResizeObserver' in window) new ResizeObserver(set).observe(header);
})();

/* TIGHT PASS 2026-10-30: on phones the header slides away while scrolling down and comes back on any scroll up. */
(() => {
  const header = document.querySelector('header.ghx-header');
  if (!header) return;
  const phone = matchMedia('(max-width: 820px)');
  let last = scrollY, ticking = false;
  const update = () => {
    ticking = false;
    const y = scrollY;
    const menuOpen = header.querySelector('[aria-expanded="true"]') || header.contains(document.activeElement);
    const hide = phone.matches && !menuOpen && y > 160 && y > last + 4;
    if (hide) header.classList.add('ghx-tucked');
    else if (y < last - 4 || y <= 160 || menuOpen || !phone.matches) header.classList.remove('ghx-tucked');
    last = y;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
})();
