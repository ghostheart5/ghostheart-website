// Keeps the "Next Live" line honest: once the listed Live has ended, the date is replaced
// with "coming soon" instead of showing a past date. No requests, no storage.
(function () {
  var now = Date.now();
  function passed(el, attr) {
    var until = Date.parse(el.getAttribute(attr));
    return !isNaN(until) && now > until;
  }
  // Home feature: one block per week. Show the block whose dates hold today; hide the rest.
  Array.prototype.forEach.call(document.querySelectorAll('[data-week-from], [data-week-until]'), function (el) {
    var from = Date.parse(el.getAttribute('data-week-from'));
    var off = (!isNaN(from) && now < from) || passed(el, 'data-week-until');
    el.hidden = off;
    el.style.display = off ? 'none' : '';
  });
  // Song of the week: show the first featured song whose week hasn't ended.
  Array.prototype.forEach.call(document.querySelectorAll('[data-sotw]'), function (box) {
    var items = box.querySelectorAll('[data-sotw-item]');
    var shown = null;
    Array.prototype.forEach.call(items, function (it) {
      var hide = shown || passed(it, 'data-until');
      it.hidden = !!hide;
      if (!hide) shown = it;
    });
    if (!shown) { box.hidden = true; return; }
    var when = box.querySelector('[data-sotw-when]');
    if (when && passed(shown, 'data-from')) when.textContent = 'Song of the week · This week';
  });
  // Pages with a list of upcoming Lives: the "Next Live" line rolls to the first one still ahead.
  Array.prototype.forEach.call(document.querySelectorAll('[data-live-next]'), function (box) {
    var scope = box.closest('section') || document;
    var slots = scope.querySelectorAll('[data-live-slot]');
    var next = null;
    Array.prototype.forEach.call(slots, function (s) { if (!next && !passed(s, 'data-live-hide-after')) next = s; });
    var label = box.querySelector('[data-live-slot-label]');
    var topic = scope.querySelector('[data-live-slot-topic]');
    if (next) {
      if (label) label.textContent = next.getAttribute('data-live-when');
      if (topic) topic.textContent = next.getAttribute('data-live-topic');
    } else if (topic) {
      topic.hidden = true;
    }
  });
  Array.prototype.forEach.call(document.querySelectorAll('[data-live-until]'), function (el) {
    if (passed(el, 'data-live-until')) el.textContent = el.getAttribute('data-live-after') || 'coming soon';
  });
  // Announcements tied to one Live (like its topic) disappear once that Live has ended.
  Array.prototype.forEach.call(document.querySelectorAll('[data-live-hide-after]'), function (el) {
    if (passed(el, 'data-live-hide-after')) el.hidden = true;
  });
})();
