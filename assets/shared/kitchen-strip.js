/* When It Isn't Your Kitchen: site-wide headline strip (Dom, Nov 19, 2026: "be the feature and main attraction across all my platforms").
   Settings come from the script tag's data- attributes, set in .github/scripts/apply_kitchen_headline.py.
   Times are compared in Central time. No outside requests. */
(function () {
  var tag = document.getElementById('kitchen-strip-js');
  if (!tag || document.getElementById('kitchen-strip')) return;
  var d = tag.dataset;
  function centralNow() {
    try {
      var p = {};
      new Intl.DateTimeFormat('en-US', { timeZone: 'America/Chicago', year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
      return p.year + '-' + p.month + '-' + p.day + ' ' + p.hour + ':' + p.minute;
    } catch (e) { return ''; }
  }
  var now = centralNow();
  if (!now || now >= d.until) return;
  var out = now >= d.outAt;
  var href = out ? (d.listen || d.video || d.channel) : (d.presave || d.channel);
  var css = document.createElement('style');
  css.textContent = '#kitchen-strip{background:#0b0b0d;border-bottom:1px solid #F4483C;color:#f0f0f2;font:600 14px/1.35 Inter,system-ui,sans-serif;' +
    'text-align:center;padding:9px 16px;position:relative;z-index:60}#kitchen-strip a{color:inherit;text-decoration:none;display:inline-flex;' +
    'flex-wrap:wrap;gap:4px 10px;justify-content:center;align-items:center}#kitchen-strip .k-new{color:#F4483C;letter-spacing:.14em;font-size:12px}' +
    '#kitchen-strip .k-go{text-decoration:underline;text-underline-offset:3px}#kitchen-strip a:focus-visible{outline:2px solid #F4483C;outline-offset:3px}';
  document.head.appendChild(css);
  var bar = document.createElement('div');
  bar.id = 'kitchen-strip';
  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', 'New single');
  var a = document.createElement('a');
  a.href = href;
  if (/^https?:/.test(href)) { a.target = '_blank'; a.rel = 'noopener'; }
  function span(cls, text) { var s = document.createElement('span'); s.className = cls; s.textContent = text; a.appendChild(s); }
  span('k-new', 'NEW SINGLE');
  span('k-title', 'When It Isn’t Your Kitchen');
  span('k-when', out ? 'Out now' : d.when);
  span('k-go', out ? (d.listen ? 'Listen ↗' : 'Watch the music video ↗') : (d.presave ? 'Pre-save ↗' : 'GhostHeart on YouTube ↗'));
  bar.appendChild(a);
  document.body.insertBefore(bar, document.body.firstChild);
})();
