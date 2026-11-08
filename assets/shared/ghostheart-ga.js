// Google Analytics: only on the public GhostHeart domain, not local previews (added by apply_google_analytics.py).
(() => {
  const id = document.currentScript && document.currentScript.dataset.gaId;
  if (!id || !/^G-[A-Z0-9]{4,16}$/.test(id)) return;
  if (!['www.myghostheart.com', 'myghostheart.com'].includes(location.hostname)) return;
  if (document.getElementById('ghostheart-ga')) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', id);
  const s = document.createElement('script');
  s.id = 'ghostheart-ga';
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
  document.head.appendChild(s);
})();
