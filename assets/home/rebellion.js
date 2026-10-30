(() => {
  'use strict';
  const quote = document.querySelector('#daily-line [data-daily-quote]');
  const link = document.getElementById('qlink');
  const copy = document.querySelector('[data-home-copy]');
  const share = document.querySelector('[data-home-share]');
  const status = document.getElementById('home-share-status');
  const fallback = document.getElementById('home-share-fallback');
  const field = document.getElementById('home-share-text');
  if (!quote || !link || !copy || !share || !status || !fallback || !field) return;
  copy.hidden = share.hidden = false;
  const payload = () => ({
    title: 'A line from GhostHeart',
    text: quote.textContent.trim(),
    url: new URL(link.getAttribute('href'), 'https://www.myghostheart.com').href
  });
  async function copyText(value, message) {
    try {
      await navigator.clipboard.writeText(value);
      fallback.hidden = true;
      status.textContent = message;
    } catch {
      fallback.hidden = false;
      field.value = value;
      field.focus();
      field.select();
      status.textContent = 'Automatic copying is unavailable. Select and copy the text below.';
    }
  }
  copy.addEventListener('click', () => {
    const data = payload();
    return copyText(`${data.text}\n${data.url}`, 'Quote and link copied.');
  });
  share.addEventListener('click', async () => {
    const data = payload();
    if (typeof navigator.share === 'function') {
      try {
        await navigator.share(data);
        fallback.hidden = true;
        status.textContent = 'Share sheet completed.';
        return;
      } catch (error) {
        if (error.name === 'AbortError') {
          status.textContent = 'Sharing cancelled.';
          return;
        }
      }
    }
    await copyText(`${data.text}\n${data.url}`, 'Quote and link copied. Paste them wherever you want to share.');
  });
})();
