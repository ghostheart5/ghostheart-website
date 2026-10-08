(() => {
  'use strict';
  const section = document.querySelector('.journal-comments[data-comment-thread]');
  const configured = window.GHOSTHEART_COMMENTS_ENDPOINT;
  if (!section || !configured) return;

  let endpoint;
  try {
    endpoint = new URL(configured);
    if (endpoint.protocol !== 'https:' || endpoint.username || endpoint.password || endpoint.search || endpoint.hash) return;
  } catch { return; }

  const thread = section.dataset.commentThread;
  if (!/^journal:[a-z0-9-]+$/.test(thread)) return;
  const make = (tag, className, content) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (content) element.textContent = content;
    return element;
  };
  const status = make('p', 'journal-comment-status');
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  const list = make('ol', 'journal-comment-list');
  list.setAttribute('aria-label', 'Approved comments');
  const form = make('form', 'journal-comment-form');
  const intro = make('p', '', 'Share a thought about this entry. Comments are held for review before they appear. Please avoid personal or crisis details.');
  const label = (title, control) => {
    const wrapper = make('label');
    wrapper.append(make('span', '', title), control);
    return wrapper;
  };
  const name = make('input');
  name.name = 'name'; name.autocomplete = 'nickname'; name.required = true;
  name.minLength = 2; name.maxLength = 60;
  const body = make('textarea');
  body.name = 'body'; body.required = true; body.minLength = 10;
  body.maxLength = 1000; body.rows = 5;
  const trap = make('input');
  trap.name = 'website'; trap.autocomplete = 'off'; trap.tabIndex = -1;
  trap.setAttribute('aria-hidden', 'true');
  const trapLabel = label('Leave this field empty', trap);
  trapLabel.className = 'journal-comment-trap';
  const consent = make('input');
  consent.type = 'checkbox'; consent.required = true;
  const consentLabel = label('I agree that my chosen name and comment will be stored for review and, if approved, displayed publicly. A short-lived address-derived marker helps limit abuse.', consent);
  consentLabel.className = 'journal-comment-consent';
  const privacy = make('p');
  privacy.append('Read the ', Object.assign(make('a', '', 'privacy notice'), { href: '/GhostHeart_Privacy.html' }), '. For urgent support, use ', Object.assign(make('a', '', 'Help & Resources'), { href: '/GhostHeart_Resources.html' }), '.');
  const button = make('button', '', 'Submit for review');
  button.type = 'submit';
  form.append(intro, label('Display name', name), label('Comment', body), trapLabel, consentLabel, privacy, button);
  section.replaceChildren(section.querySelector('h2'), list, status, form);

  async function load() {
    status.textContent = 'Loading approved comments…';
    try {
      const url = new URL(endpoint);
      url.searchParams.set('thread', thread);
      const response = await fetch(url, { headers: { Accept: 'application/json' }, cache: 'no-store' });
      if (!response.ok) throw new Error('Unavailable');
      const data = await response.json();
      if (!Array.isArray(data.comments)) throw new Error('Unexpected response');
      list.replaceChildren();
      for (const comment of data.comments.slice(0, 100)) {
        if (typeof comment.name !== 'string' || typeof comment.body !== 'string' || typeof comment.published_at !== 'string') continue;
        const item = make('li');
        const author = make('strong', '', comment.name);
        const content = make('p', '', comment.body);
        item.append(author);
        if (!Number.isNaN(Date.parse(comment.published_at))) {
          const date = make('time', '', new Date(comment.published_at).toLocaleDateString());
          date.dateTime = comment.published_at;
          item.append(date);
        }
        item.append(content);
        list.append(item);
      }
      status.textContent = list.childElementCount ? '' : 'No approved comments yet. You can start the conversation.';
    } catch {
      status.textContent = 'Comments could not be loaded right now. Please try again later.';
    }
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    button.disabled = true;
    status.textContent = 'Sending your comment for review…';
    try {
      const response = await fetch(endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ thread, name: name.value.trim(), body: body.value.trim(), consent: consent.checked, website: trap.value })
      });
      if (response.status === 429) throw new Error('Too many comments. Please try again later.');
      if (!response.ok) throw new Error('Your comment could not be submitted. Please try again later.');
      const result = await response.json();
      if (result.status !== 'pending') throw new Error('Your comment could not be confirmed. Please try again later.');
      form.reset();
      status.textContent = 'Thank you. Your comment is waiting for review and is not public yet.';
    } catch (error) {
      status.textContent = error.message || 'Your comment could not be submitted. Please try again later.';
    } finally { button.disabled = false; }
  });
  load();
})();
