// "I'm here to help" order form. Sends nothing until orders-config.js is complete.
(function () {
  'use strict';
  var form = document.getElementById('story-form');
  if (!form) return;
  var cfg = window.GHOSTHEART_ORDERS || {};
  var fields = form.querySelector('[data-order-fields]');
  var errorBox = form.querySelector('[data-order-error]');
  var submit = form.querySelector('[data-order-submit]');
  var fine = form.querySelector('[data-order-fine]');
  var statusBox = document.querySelector('[data-order-status]');
  var statusTitle = document.querySelector('[data-order-status-title]');
  var statusText = document.querySelector('[data-order-status-text]');

  function setStatus(title, text, ok) {
    if (!statusBox) return;
    statusTitle.textContent = title;
    statusText.textContent = text;
    statusBox.classList.toggle('ok', Boolean(ok));
    statusBox.hidden = false;
  }

  var params = new URLSearchParams(window.location.search);
  var hasDatabase = /^https:\/\/[a-z0-9]+\.supabase\.co$/.test(cfg.supabaseUrl || '') &&
    typeof cfg.supabaseKey === 'string' && cfg.supabaseKey.length > 20;

  // The order id waits in this tab while the customer is on Stripe, so the return can ask about it.
  var ORDER_KEY = 'ghostheart.order.pending.v1';
  function rememberOrder(id) { try { window.sessionStorage.setItem(ORDER_KEY, id); } catch (e) { /* storage blocked: honest note only */ } }
  function storedOrder() {
    try { var id = window.sessionStorage.getItem(ORDER_KEY) || ''; return /^[0-9a-f-]{36}$/.test(id) ? id : ''; } catch (e) { return ''; }
  }
  function forgetOrder() { try { window.sessionStorage.removeItem(ORDER_KEY); } catch (e) { /* nothing to do */ } }

  // The return address alone can't prove a payment (anyone can add ?paid=1), so this note
  // points to Stripe's receipt instead of confirming payment itself (site audit 2026-11-01).
  function receiptNote() {
    setStatus('Thank you for your order.', 'Stripe emails your receipt when the payment goes through. Once it does, I’ll write your song and email it to you within 7 days.', true);
  }
  // "Payment confirmed" only shows when the database says Stripe's signed webhook marked this
  // order paid (public.ghostheart_order_paid). Webhooks can lag, so ask a few times over ~20 seconds.
  var PAID_CHECKS = 8, PAID_WAIT_MS = 2500;
  function checkPaid(id, tries) {
    fetch(cfg.supabaseUrl + '/rest/v1/rpc/ghostheart_order_paid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: cfg.supabaseKey },
      body: JSON.stringify({ order_id: id })
    }).then(function (response) {
      return response.ok ? response.json() : false;
    }).catch(function () { return false; }).then(function (paid) {
      if (paid === true) {
        forgetOrder();
        setStatus('Payment confirmed.', 'Thank you. I’ll write your song and email it within 7 days.', true);
      } else if (tries + 1 < PAID_CHECKS) {
        window.setTimeout(function () { checkPaid(id, tries + 1); }, PAID_WAIT_MS);
      } else {
        receiptNote();
      }
    });
  }
  if (params.get('paid') === '1') {
    var paidId = storedOrder();
    if (paidId && hasDatabase && window.fetch) {
      setStatus('Checking your payment…', 'This takes a few seconds while Stripe confirms it.', true);
      checkPaid(paidId, 0);
    } else {
      receiptNote();
    }
  }

  var ready = hasDatabase &&
    /^https:\/\/buy\.stripe\.com\/(?!test_)[A-Za-z0-9_]+$/.test(cfg.songPayLink || ''); // live links only
  // The status box stays hidden unless there is news for the visitor (Dom, Nov 2: no warning box).
  if (!ready) {
    if (params.get('paid') !== '1') setStatus('Orders open soon', 'The form isn’t taking orders yet, so nothing you type here is sent.');
    return;
  }

  fields.disabled = false;
  // A link like /here-to-help/?pick=song#order opens straight on the full song.
  var pick = form.querySelector('input[name="kind"][value="' + (params.get('pick') || '').replace(/[^a-z]/g, '') + '"]');
  if (pick) pick.checked = true;

  function kind() { var k = form.querySelector('input[name="kind"]:checked'); return k ? k.value : 'try'; }
  function showKind() {
    var k = kind();
    form.querySelectorAll('[data-kind]').forEach(function (el) { el.hidden = el.getAttribute('data-kind').split(' ').indexOf(k) < 0; });
    submit.textContent = k === 'song' ? 'Continue to payment · $50' : k === 'try' ? 'Send for my free preview' : 'Send my request';
    if (fine) fine.textContent = k === 'song' ? 'You pay $50 on Stripe’s secure page, and your song arrives within 7 days.' : k === 'try' ? 'The free preview costs nothing and asks for no card.' : 'I’ll email you the total. You only pay once you agree to it.';
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
    if (k === 'song' || k === 'try') {
      var length = form.querySelector('input[name="length"]:checked');
      if (!value('for_whom')) return fail('Please tell me who the song is for.');
      if (!value('memories')) return fail('Please share a few memories for the song.');
      if (k === 'song' && !length) return fail('Please choose a length.');
      payload.kind = 'song';
      payload.for_whom = value('for_whom'); payload.occasion = value('occasion'); payload.memories = value('memories');
      payload.names = value('names'); payload.mood = value('mood');
      // The free try is saved as a song story marked FREE TRY, with no payment (the order list needs no change).
      payload.length = k === 'try' ? 'full' : length.value;
      if (k === 'try') payload.details = 'FREE TRY: send a song title and 2 lines. No payment yet.';
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
        rememberOrder(orderId);
        var url = cfg.songPayLink + '?client_reference_id=' + encodeURIComponent(orderId);
        window.location.assign(url);
        return;
      }
      form.reset(); showKind();
      if (k === 'try') setStatus('Got it. Thank you.', 'Within 2 days I’ll email you the song title and first 2 lines. If you love them, the full song is $50.', true);
      else setStatus('Got it. Thank you.', 'I’ll email you the total for your job. You only pay once you agree to it.', true);
      statusBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
      submit.disabled = false;
    }).catch(function () {
      fail('That didn’t go through. Please try again in a few minutes.');
      submit.disabled = false; showKind();
    });
  });
}());
