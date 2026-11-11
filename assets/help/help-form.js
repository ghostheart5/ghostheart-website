// "More ways I can help" request form on Work with GhostHeart (Dom, Nov 2 2026: the section needs its own email box).
// Saves the job as an office order (kind 'office'), the same way the song form saves orders. No payment here:
// Dom emails the total first. Stays closed until orders-config.js has the database settings.
(function () {
  'use strict';
  var form = document.getElementById('help-form');
  if (!form) return;
  var cfg = window.GHOSTHEART_ORDERS || {};
  var fields = form.querySelector('[data-help-fields]');
  var errorBox = form.querySelector('[data-help-error]');
  var submit = form.querySelector('[data-help-submit]');
  var statusBox = form.querySelector('[data-help-status]');
  function setStatus(title, text, ok) {
    form.querySelector('[data-help-status-title]').textContent = title;
    form.querySelector('[data-help-status-text]').textContent = text;
    statusBox.classList.toggle('ok', Boolean(ok));
    statusBox.hidden = false;
  }
  var hasDatabase = /^https:\/\/[a-z0-9]+\.supabase\.co$/.test(cfg.supabaseUrl || '') &&
    typeof cfg.supabaseKey === 'string' && cfg.supabaseKey.length > 20;
  if (!hasDatabase || !window.fetch) { setStatus('Requests open soon', 'This form isn’t taking requests yet, so nothing you type here is sent.'); return; }
  fields.disabled = false;
  function value(name) { var el = form.elements[name]; return el ? String(el.value || '').trim() : ''; }
  function fail(message) { errorBox.textContent = message; errorBox.hidden = false; }
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    errorBox.hidden = true;
    if (!value('service')) return fail('Please choose a job.');
    if (!value('details')) return fail('Please tell me what you need done.');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value('email'))) return fail('Please add an email address so I can reach you.');
    // The Wake the Heart page also asks for an optional name and date; they ride along in the request text.
    var picked = form.elements.service && form.elements.service.selectedOptions ? form.elements.service.selectedOptions[0] : null;
    var extra = [];
    if (picked && picked.textContent) extra.push('Help with: ' + picked.textContent.trim());
    if (value('name')) extra.push('Name: ' + value('name'));
    if (value('when')) extra.push('Needed by: ' + value('when'));
    var details = (extra.length ? extra.join('\n') + '\n\n' : '') + value('details');
    var payload = { kind: 'office', email: value('email'), website: value('website'), service: value('service'), details: details };
    // Where the visitor came from (order-form.js notes it on arrival). Saved with the request; no name or email in it.
    if (typeof window.ghostheartOrderSource === 'function') payload.source = window.ghostheartOrderSource();
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
      if (typeof window.ghostheartOrderTrack === 'function') window.ghostheartOrderTrack('generate_lead', { lead_type: 'office_help' });
      form.reset();
      setStatus('Got it. Thank you.', 'I’ll email you the total for your job. You only pay once you agree to it.', true);
      statusBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }).catch(function () {
      fail('That didn’t go through. Please try again in a few minutes.');
    }).then(function () { submit.disabled = false; submit.textContent = 'Send my request'; });
  });
}());
