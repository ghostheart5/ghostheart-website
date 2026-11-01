// "For how you feel": pick a feeling and how much time you have, get one piece with the
// reason it fits. Hand-curated rules over assets/data/for-you.js; no AI, no requests,
// nothing remembered except what you choose to Save (see check-back-in.js).
(function () {
  var box = document.getElementById('for-you');
  var cat = window.GHOSTHEART_FOR_YOU;
  if (!box || !cat) return;
  var form = box.querySelector('[data-for-you-form]');
  var out = box.querySelector('[data-for-you-result]');
  var shown = {};

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) node.setAttribute(k, attrs[k]);
    if (text != null) node.textContent = text;
    return node;
  }
  function choices(name, rows) {
    var set = el('fieldset', { 'class': 'fy-set' });
    set.appendChild(el('legend', null, name === 'mood' ? 'How are you feeling?' : 'How do you want it?'));
    rows.forEach(function (row, i) {
      var label = el('label', { 'class': 'fy-choice' });
      var input = el('input', { type: 'radio', name: name, value: row[0] });
      if (i === 0) input.checked = true;
      label.appendChild(input);
      label.appendChild(el('span', null, row[1]));
      if (row[2]) label.appendChild(el('small', null, row[2]));
      set.appendChild(label);
    });
    return set;
  }
  function picked(name) { var c = form.querySelector('input[name="' + name + '"]:checked'); return c ? c.value : ''; }
  function label(rows, key) { for (var i = 0; i < rows.length; i++) if (rows[i][0] === key) return rows[i][1]; return key; }

  form.insertBefore(choices('how', cat.how), form.firstChild);
  form.insertBefore(choices('mood', cat.moods), form.firstChild);

  function pick() {
    var mood = picked('mood'), how = picked('how');
    var fits = cat.picks.filter(function (p) { return p.moods.indexOf(mood) >= 0; });
    var exact = fits.filter(function (p) { return p.how === how; });
    var pool = exact.length ? exact : fits;
    var key = mood + '|' + (exact.length ? how : '*');
    var n = shown[key] = ((shown[key] == null ? -1 : shown[key]) + 1) % pool.length;
    var item = pool[n];

    out.textContent = '';
    if (!exact.length) out.appendChild(el('p', { 'class': 'fy-honest' }, 'Nothing to ' + label(cat.how, how).toLowerCase() + ' for that yet. This is the closest fit:'));
    out.appendChild(el('p', { 'class': 'fy-kind' }, item.kind + (pool.length > 1 ? ' · ' + (n + 1) + ' of ' + pool.length : '')));
    out.appendChild(el('h3', { 'class': 'fy-title' }, item.title));
    out.appendChild(el('p', { 'class': 'fy-why' }, item.why));
    var actions = el('div', { 'class': 'fy-actions' });
    var external = /^https?:/.test(item.href);
    var open = el('a', external ? { href: item.href, rel: 'noopener', target: '_blank' } : { href: item.href }, ({ watch: 'Watch', listen: 'Listen', read: 'Read', line: 'See it in the Quote Vault' })[item.how] + (external ? ' ↗' : ' →'));
    open.className = 'fy-open';
    actions.appendChild(open);
    if (pool.length > 1) {
      var again = el('button', { type: 'button', 'class': 'fy-again' }, 'Try another');
      again.addEventListener('click', function () { pick(); out.querySelector('.fy-title').focus(); });
      actions.appendChild(again);
    }
    if (window.GHCheckBackIn) actions.appendChild(window.GHCheckBackIn.saveButton({ id: 'for-you-' + item.id, title: item.title, kind: item.kind, href: item.href }));
    out.appendChild(actions);
    out.querySelector('.fy-title').setAttribute('tabindex', '-1');
    out.hidden = false;
  }

  form.addEventListener('submit', function (event) { event.preventDefault(); pick(); out.querySelector('.fy-title').focus(); });
  box.hidden = false;
})();
