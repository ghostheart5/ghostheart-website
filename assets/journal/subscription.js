(() => {
  'use strict';
  document.querySelectorAll('.journal-signup .g-form').forEach(form => {
    form.addEventListener('submit', () => {
      form.querySelector('.g-form-status').textContent =
        'Opening Mailchimp to complete signup. This page does not confirm your subscription or email delivery.';
    });
  });
})();
