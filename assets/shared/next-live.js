// Keeps the "Next Live" line honest: once the listed Live has ended, the date is replaced
// with "coming soon" instead of showing a past date. No requests, no storage.
(function () {
  var els = document.querySelectorAll('[data-live-until]');
  var now = Date.now();
  Array.prototype.forEach.call(els, function (el) {
    var until = Date.parse(el.getAttribute('data-live-until'));
    if (!isNaN(until) && now > until) el.textContent = el.getAttribute('data-live-after') || 'coming soon';
  });
  // Announcements tied to one Live (like its topic) disappear once that Live has ended.
  Array.prototype.forEach.call(document.querySelectorAll('[data-live-hide-after]'), function (el) {
    var until = Date.parse(el.getAttribute('data-live-hide-after'));
    if (!isNaN(until) && now > until) el.hidden = true;
  });
})();
