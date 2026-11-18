// Metricool website counter for pages that do not load ghostheart-world.js or wake-v3/site.js
// (the Protected by GhostHeart home page, Nov 11, 2026). Same loader, same brand hash.
// Loads only on the public GhostHeart domain, not local previews.
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
