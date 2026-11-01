// "Check back in" (site audit 2026-11-01, owner yes): save songs, films and lines,
// pick a song up where you stopped, keep your place in a reading, and see what's new
// since your last visit. Everything stays in this browser (localStorage); nothing is
// sent anywhere. The only request is the site's own /journal/feed.xml, on the home page.
(function () {
  var KEY = 'gh-check-back-in';
  var MAX_SAVED = 30;

  function safe(fn, fallback) { try { return fn(); } catch (e) { return fallback; } }
  function load() {
    var d = safe(function () { return JSON.parse(localStorage.getItem(KEY) || 'null'); }, null);
    if (!d || d.v !== 1) d = { v: 1, saved: [], song: null, read: null, last: 0, prev: 0 };
    return d;
  }
  // Storage can be blocked (private windows, site data cleared): then the feature stays hidden.
  var works = safe(function () { localStorage.setItem(KEY + '-test', '1'); localStorage.removeItem(KEY + '-test'); return true; }, false);
  if (!works) return;
  var data = load();
  function store() { safe(function () { localStorage.setItem(KEY, JSON.stringify(data)); }); }

  // A visit starts after 30 minutes away; "new since" compares with the visit before this one.
  var now = Date.now();
  if (now - (data.last || 0) > 30 * 60 * 1000) data.prev = data.last || 0;
  data.last = now;
  store();

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) node.setAttribute(k, attrs[k]);
    if (text != null) node.textContent = text;
    return node;
  }
  function isSaved(id) { return data.saved.some(function (s) { return s.id === id; }); }
  function toggle(item) {
    if (isSaved(item.id)) data.saved = data.saved.filter(function (s) { return s.id !== item.id; });
    else data.saved.unshift({ id: item.id, title: item.title, kind: item.kind, href: item.href, at: Date.now() });
    data.saved = data.saved.slice(0, MAX_SAVED);
    store();
    refreshButtons();
  }
  function clock(seconds) { var s = Math.floor(seconds); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }

  // ---- Save buttons ---------------------------------------------------------------
  var buttons = [];
  function saveButton(item) {
    var b = el('button', { type: 'button', 'class': 'gh-save' });
    b._item = item;
    b.addEventListener('click', function () { toggle(item); });
    buttons.push(b);
    paint(b);
    return b;
  }
  function paint(b) {
    var on = isSaved(b._item.id);
    b.setAttribute('aria-pressed', String(on));
    b.setAttribute('aria-label', (on ? 'Saved: ' : 'Save ') + b._item.title);
    b.textContent = on ? '♥ Saved' : '♡ Save';
  }
  function refreshButtons() { buttons.forEach(paint); }
  window.GHCheckBackIn = { saveButton: saveButton, isSaved: isSaved };

  // Music page: a Save button on every song; remember where a song stopped.
  var audio = document.getElementById('aud');
  Array.prototype.forEach.call(document.querySelectorAll('.tracks li[id^="song-"]'), function (li) {
    var play = li.querySelector('button[data-title]');
    if (!play) return;
    li.appendChild(saveButton({ id: li.id, title: play.getAttribute('data-title'), kind: 'Song', href: '/music/#' + li.id }));
  });
  if (audio) {
    var lastWrite = 0;
    audio.addEventListener('timeupdate', function () {
      var on = document.querySelector('.tracks button.on');
      var li = on && on.closest('li[id^="song-"]');
      if (!li || Date.now() - lastWrite < 3000) return;
      lastWrite = Date.now();
      data.song = { id: li.id, title: on.getAttribute('data-title'), time: audio.currentTime, at: Date.now() };
      store();
    });
    audio.addEventListener('ended', function () { data.song = null; store(); });
    if (data.song && data.song.time > 5) {
      var song = data.song;
      var target = document.getElementById(song.id);
      var trackButton = target && target.querySelector('button[data-title]');
      if (trackButton) {
        var bar = el('div', { 'class': 'gh-resume', role: 'region', 'aria-label': 'Pick up where you left off' });
        bar.appendChild(el('p', null, 'Pick up where you left off: ' + song.title + ' at ' + clock(song.time) + '.'));
        var resume = el('button', { type: 'button', 'class': 'gh-resume-go' }, '▶ Resume');
        var close = el('button', { type: 'button', 'class': 'gh-resume-close', 'aria-label': 'Dismiss' }, '✕');
        resume.addEventListener('click', function () {
          audio.addEventListener('loadedmetadata', function seek() {
            audio.removeEventListener('loadedmetadata', seek);
            safe(function () { audio.currentTime = song.time; });
          });
          trackButton.click();
          bar.remove();
        });
        close.addEventListener('click', function () { bar.remove(); });
        bar.appendChild(resume); bar.appendChild(close);
        var list = target.closest('.tracks');
        list.parentNode.insertBefore(bar, list);
        // Coming from the home panel's "Pick up" link: focus Resume (after the song link's own focus).
        if (/[?&]resume=1\b/.test(location.search)) addEventListener('load', function () { setTimeout(function () { resume.focus(); }); });
      }
    }
  }

  // Vault: a Save button on every item.
  Array.prototype.forEach.call(document.querySelectorAll('article.vault-item'), function (card) {
    var link = card.querySelector('a[href]');
    var heading = card.querySelector('h2, h3');
    if (!link || !heading) return;
    var quote = card.querySelector('blockquote');
    card.appendChild(saveButton({
      id: 'vault-' + link.getAttribute('href'),
      kind: ((card.querySelector('.vault-type') || {}).textContent || '').trim(),
      title: (quote || heading).textContent.trim(),
      href: link.getAttribute('href')
    }));
  });

  // Readings (blog posts, Passages, story chapters): keep your place.
  var reading = /^\/(journal|passages|story)\/(?!index\.html$)[^/]+\.html$/.test(location.pathname);
  if (reading) {
    var title = (document.querySelector('main h1') || {}).textContent || document.title;
    title = title.replace(/\s+/g, ' ').trim();
    var depth = function () { var room = document.documentElement.scrollHeight - innerHeight; return room > 0 ? Math.min(1, scrollY / room) : 1; };
    if (data.read && data.read.href === location.pathname && data.read.pct > 0.1 && data.read.pct < 0.95 && !location.hash) {
      var saved = data.read.pct;
      var note = el('div', { 'class': 'gh-resume gh-resume-read', role: 'region', 'aria-label': 'Continue reading' });
      note.appendChild(el('p', null, 'You stopped about ' + Math.round(saved * 100) + '% of the way through.'));
      var go = el('button', { type: 'button', 'class': 'gh-resume-go' }, 'Continue reading');
      var x = el('button', { type: 'button', 'class': 'gh-resume-close', 'aria-label': 'Dismiss' }, '✕');
      go.addEventListener('click', function () { note.remove(); scrollTo(0, saved * (document.documentElement.scrollHeight - innerHeight)); });
      x.addEventListener('click', function () { note.remove(); });
      note.appendChild(go); note.appendChild(x);
      var main = document.querySelector('main');
      if (main) main.insertBefore(note, main.firstChild);
    }
    var ticking = false;
    addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      setTimeout(function () {
        ticking = false;
        var pct = depth();
        data.read = pct >= 0.95 ? null : { href: location.pathname, title: title, pct: pct, at: Date.now() };
        store();
      }, 1000);
    }, { passive: true });
  }

  // Home page: the "Check back in" panel, shown only when there is something to come back to.
  var panel = document.getElementById('check-back-in');
  if (!panel) return;
  var list = panel.querySelector('[data-checkin-list]');
  function render(fresh) {
    list.textContent = '';
    function row(label, title, href, removeFn) {
      var li = el('li');
      li.appendChild(el('small', null, label));
      li.appendChild(el('a', { href: href }, title));
      if (removeFn) {
        var rm = el('button', { type: 'button', 'class': 'gh-remove', 'aria-label': 'Remove ' + title }, '✕');
        rm.addEventListener('click', removeFn);
        li.appendChild(rm);
      }
      list.appendChild(li);
    }
    if (data.song) row('Pick up at ' + clock(data.song.time), data.song.title, '/music/?resume=1#' + data.song.id, function () { data.song = null; store(); render(fresh); });
    if (data.read) row('Continue reading', data.read.title, data.read.href, function () { data.read = null; store(); render(fresh); });
    (fresh || []).forEach(function (item) { row('New since your last visit', item.title, item.href); });
    data.saved.slice(0, 6).forEach(function (s) {
      row('Saved ' + (s.kind || '').toLowerCase(), s.title, s.href, function () { data.saved = data.saved.filter(function (x) { return x.id !== s.id; }); store(); render(fresh); });
    });
    panel.hidden = !list.children.length;
  }
  panel.querySelector('[data-checkin-forget]').addEventListener('click', function () {
    safe(function () { localStorage.removeItem(KEY); });
    data = { v: 1, saved: [], song: null, read: null, last: Date.now(), prev: 0 };
    store();
    render([]);
  });
  render([]);
  if (data.prev && window.fetch && window.DOMParser) {
    fetch('/journal/feed.xml').then(function (r) { return r.ok ? r.text() : ''; }).then(function (xml) {
      var doc = new DOMParser().parseFromString(xml, 'application/xml');
      var fresh = Array.prototype.slice.call(doc.querySelectorAll('item')).map(function (item) {
        var link = (item.querySelector('link') || {}).textContent || '';
        return { title: ((item.querySelector('title') || {}).textContent || '').trim(), href: link.replace(/^https:\/\/www\.myghostheart\.com/, ''), at: Date.parse((item.querySelector('pubDate') || {}).textContent || '') };
      }).filter(function (item) { return item.title && item.href && item.at > data.prev; }).slice(0, 3);
      if (fresh.length) render(fresh);
    }).catch(function () {});
  }
})();
