/* LOUD redesign: keep in-page links clear of the fixed site header. */
(() => {
  const header = document.querySelector('header.ghx-header');
  if (!header) return;
  const set = () => document.documentElement.style.setProperty('--hdr', Math.ceil(header.getBoundingClientRect().height) + 8 + 'px');
  set();
  addEventListener('resize', set, { passive: true });
  if ('ResizeObserver' in window) new ResizeObserver(set).observe(header);
})();
