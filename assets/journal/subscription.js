(() => {
  'use strict';
  document.querySelectorAll('.journal-signup .g-form').forEach(form => {
    form.addEventListener('submit', () => {
      form.querySelector('.g-form-status').textContent =
        'Opening Mailchimp to finish signup. Confirm through its email; this page does not confirm your subscription.';
    });
  });
})();
