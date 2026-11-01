// PICK THE DOOR 2026-11-01: Sunday Live vote.
// Votes are counted in Supabase by .github/vote/supabase/door-vote.review.sql.
// Until that file has been run once, the doors still open, and the page says
// "Voting opens soon" and offers the email reminder. It never shows made-up numbers.
(function () {
  var box = document.querySelector('[data-door-vote]');
  if (!box) return;
  var URL = 'https://pgqaqqliefpofsktjhjq.supabase.co/rest/v1/rpc/';
  var KEY = 'sb_publishable_P7GsZrSsz839xa3xhJ3bbA_JKcTZNXp';
  var poll = box.getAttribute('data-poll');
  var doors = [].slice.call(box.querySelectorAll('[data-pick]'));
  var status = box.querySelector('[data-dv-status]');
  var count = box.querySelector('[data-dv-count]');
  var mode = 'loading';
  var busy = false;
  var mine = store('dv-pick-' + poll);

  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) {}
    return v === undefined ? null : v;
  }
  function voter() {
    var id = store('dv-voter');
    if (!id || !/^[a-z0-9-]{16,64}$/.test(id)) {
      id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() :
        'v' + Date.now().toString(36) + Math.random().toString(36).slice(2, 12);
      store('dv-voter', id);
    }
    return id;
  }
  function call(fn, body) {
    return fetch(URL + fn, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: KEY },
      body: JSON.stringify(body)
    }).then(function (r) { if (!r.ok) throw new Error(String(r.status)); return r.json(); });
  }
  function name(p) { return p === 'a' ? 'Door I' : 'Door II'; }
  function press(p) { doors.forEach(function (d) { d.setAttribute('aria-pressed', String(d.getAttribute('data-pick') === p)); }); }
  function show(t) {
    var a = +t.a || 0, b = +t.b || 0, total = a + b;
    var pa = total ? Math.round(a * 100 / total) : 0, pb = total ? 100 - pa : 0;
    doors.forEach(function (d) {
      var p = d.getAttribute('data-pick') === 'a' ? pa : pb;
      d.querySelector('.dv-pct').textContent = p + '%';
      d.querySelector('.dv-bar i').style.width = p + '%';
    });
    if (count) count.textContent = total + (total === 1 ? ' vote' : ' votes');
    return { a: a, b: b, pa: pa, pb: pb, total: total };
  }
  function lead(r) {
    if (r.a === r.b) return 'It&rsquo;s dead even.';
    return '<em>' + (r.a > r.b ? 'Door I' : 'Door II') + '</em> leads with ' + (r.a > r.b ? r.pa : r.pb) + '%.';
  }

  call('door_vote_totals', { p_poll: poll }).then(function (t) {
    if (!t || typeof t.a !== 'number') throw new Error('bad');
    if (!t.open) {
      mode = 'closed';
      box.classList.add('voted');
      var r = show(t);
      if (r.a === r.b) {
        press('');
        status.innerHTML = 'Voting is closed. ' + (r.total ? 'It ended in a tie.' : '');
      } else {
        press(r.a > r.b ? 'a' : 'b');
        status.innerHTML = 'Voting is closed. <em>' + (r.a > r.b ? 'Door I' : 'Door II') + '</em> won with ' + (r.a > r.b ? r.pa : r.pb) + '%.';
      }
      doors.forEach(function (d) { d.setAttribute('aria-disabled', 'true'); });
      return;
    }
    mode = 'open';
    if (mine === 'a' || mine === 'b') {
      box.classList.add('voted'); press(mine);
      status.innerHTML = 'You picked <em>' + name(mine) + '</em>. ' + lead(show(t));
    } else {
      status.textContent = 'Tap a door to vote.';
    }
  }).catch(function () {
    mode = 'soon';
    status.textContent = 'Tap a door to look inside.';
  });

  doors.forEach(function (d) {
    d.addEventListener('click', function () {
      var p = d.getAttribute('data-pick');
      if (mode === 'closed' || mode === 'loading' || busy) return;
      press(p);
      if (mode === 'soon') {
        box.classList.add('soon');
        status.innerHTML = 'You picked <em>' + name(p) + '</em>. Voting opens soon. Get a reminder when it does.';
        return;
      }
      busy = true;
      box.setAttribute('aria-busy', 'true');
      status.textContent = 'Counting your vote…';
      call('cast_door_vote', { p_poll: poll, p_pick: p, p_voter: voter() }).then(function (t) {
        store('dv-pick-' + poll, p); mine = p;
        box.classList.add('voted');
        status.innerHTML = 'Your vote is in for <em>' + name(p) + '</em>. ' + lead(show(t)) + ' Changed your mind? Tap the other door.';
      }).catch(function () {
        status.textContent = 'That didn’t go through. Please try again in a minute.';
        press(mine === 'a' || mine === 'b' ? mine : '');
      }).then(function () {
        busy = false;
        box.removeAttribute('aria-busy');
      });
    });
  });
})();
