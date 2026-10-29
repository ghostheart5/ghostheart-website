// "I'm here to help" order form. Sends nothing until orders-config.js is complete.
(function () {
  'use strict';
  var form = document.getElementById('story-form');
  if (!form) return;
  var cfg = window.GHOSTHEART_ORDERS || {};
  var fields = form.querySelector('[data-order-fields]');
  var errorBox = form.querySelector('[data-order-error]');
  var submit = form.querySelector('[data-order-submit]');
  var statusBox = document.querySelector('[data-order-status]');
  var statusTitle = document.querySelector('[data-order-status-title]');
  var statusText = document.querySelector('[data-order-status-text]');

  function setStatus(title, text, ok) {
    if (!statusBox) return;
    statusTitle.textContent = title;
    statusText.textContent = text;
    statusBox.classList.toggle('ok', Boolean(ok));
  }

  var params = new URLSearchParams(window.location.search);
  if (params.get('paid') === '1') {
    setStatus('Thank you. Your song is on its way.', 'Your payment went through. I’ll write your song and email it to you within 7 days.', true);
  }

  var ready = /^https:\/\/[a-z0-9]+\.supabase\.co$/.test(cfg.supabaseUrl || '') &&
    typeof cfg.supabaseKey === 'string' && cfg.supabaseKey.length > 20 &&
    /^https:\/\/buy\.stripe\.com\/[A-Za-z0-9_]+$/.test(cfg.songPayLink || '');
  if (!ready) return;

  fields.disabled = false;
  if (params.get('paid') !== '1') {
    setStatus('5 founding spots open', 'Tell me your story below. Custom songs are $50 at the founding price.', true);
  }

  function kind() { var k = form.querySelector('input[name="kind"]:checked'); return k ? k.value : 'song'; }
  function showKind() {
    var k = kind();
    form.querySelectorAll('[data-kind]').forEach(function (el) { el.hidden = el.getAttribute('data-kind') !== k; });
    submit.textContent = k === 'song' ? 'Continue to payment · $50' : 'Send my request';
  }
  form.querySelectorAll('input[name="kind"]').forEach(function (el) { el.addEventListener('change', showKind); });
  showKind();

  function value(name) { var el = form.elements[name]; return el ? String(el.value || '').trim() : ''; }
  function fail(message) { errorBox.textContent = message; errorBox.hidden = false; }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    errorBox.hidden = true;
    var k = kind();
    var email = value('email');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return fail('Please add an email address so I can reach you.');
    var payload = { kind: k, email: email, website: value('website') };
    if (k === 'song') {
      var length = form.querySelector('input[name="length"]:checked');
      if (!value('for_whom')) return fail('Please tell me who the song is for.');
      if (!value('memories')) return fail('Please share a few memories for the song.');
      if (!length) return fail('Please choose a length.');
      payload.for_whom = value('for_whom'); payload.occasion = value('occasion'); payload.memories = value('memories');
      payload.names = value('names'); payload.mood = value('mood'); payload.length = length.value;
    } else {
      if (!value('service')) return fail('Please choose a service.');
      if (!value('details')) return fail('Please tell me what you need done.');
      payload.service = value('service'); payload.details = value('details');
    }
    submit.disabled = true;
    submit.textContent = 'Sending…';
    fetch(cfg.supabaseUrl + '/rest/v1/rpc/submit_ghostheart_order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: cfg.supabaseKey },
      body: JSON.stringify({ payload: payload })
    }).then(function (response) {
      if (!response.ok) throw new Error(String(response.status));
      return response.json();
    }).then(function (orderId) {
      if (typeof orderId !== 'string' || !/^[0-9a-f-]{36}$/.test(orderId)) throw new Error('bad id');
      if (k === 'song') {
        var url = cfg.songPayLink + '?client_reference_id=' + encodeURIComponent(orderId);
        window.location.assign(url);
        return;
      }
      form.reset(); showKind();
      setStatus('Got it. Thank you.', 'I’ll email you the total for your job. You only pay once you agree to it.', true);
      statusBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
      submit.disabled = false;
    }).catch(function () {
      fail('That didn’t go through. Please try again in a few minutes.');
      submit.disabled = false; showKind();
    });
  });
}());
