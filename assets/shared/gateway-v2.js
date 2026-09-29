/* No tracking events, automatic media, or email delivery claims. */
(() => {
  'use strict';
  const KEY = 'ghostheart.reading.place.v1';
  const allowed = /^\/journal\/[a-z0-9-]+\.html$/;
  const getPlace = () => { try { const p = JSON.parse(localStorage.getItem(KEY)); return p && allowed.test(p.path) && Number.isFinite(p.y) ? p : null; } catch { return null; } };
  const announce = message => document.querySelectorAll('[data-reading-status]').forEach(node => { node.textContent = message; });
  const refreshResume = () => {
    const place = getPlace();
    document.querySelectorAll('.g-resume').forEach(node => { node.hidden = !place; const a=node.querySelector('[data-resume-link]'); if (place && a) a.href = place.path + '#saved-reading-place'; });
  };
  document.querySelectorAll('[data-save-reading]').forEach(button => button.addEventListener('click', () => {
    if (!allowed.test(location.pathname)) return;
    try { localStorage.setItem(KEY, JSON.stringify({path:location.pathname,y:Math.max(0,Math.round(scrollY))})); announce('Your place is saved on this device only.'); refreshResume(); }
    catch { announce('This browser could not save your place. You can still read everything.'); }
  }));
  document.querySelectorAll('[data-forget-reading]').forEach(button => button.addEventListener('click', () => {
    try { localStorage.removeItem(KEY); announce('Saved reading place cleared.'); refreshResume(); } catch { announce('Browser storage is unavailable.'); }
  }));
  const saved=getPlace();
  if (location.hash === '#saved-reading-place' && saved?.path === location.pathname) window.addEventListener('load', () => window.scrollTo({top:saved.y,behavior:'auto'}), {once:true});
  refreshResume();
  document.querySelectorAll('[data-video-id]').forEach(button => button.addEventListener('click', () => {
    const id=button.dataset.videoId;
    if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return;
    document.querySelectorAll('.g-player iframe').forEach(player => {
      const card=player.closest('.g-film'); player.remove(); card.querySelector('[data-video-id]').hidden=false; card.querySelector('.g-close').hidden=true;
    });
    const card=button.closest('.g-film'), frame=card.querySelector('.g-player');
    const player=document.createElement('iframe');
    player.src='https://www.youtube-nocookie.com/embed/'+id+'?rel=0&playsinline=1';
    player.title=button.dataset.videoTitle || 'GhostHeart film';
    player.allow='encrypted-media; picture-in-picture; fullscreen';player.allowFullscreen=true;
    player.referrerPolicy='strict-origin-when-cross-origin';button.hidden=true;
    frame.appendChild(player);card.querySelector('.g-close').hidden=false;player.focus();
  }));
  document.querySelectorAll('.g-close').forEach(button => button.addEventListener('click', () => {
    const card=button.closest('.g-film');card.querySelector('iframe')?.remove();
    const play=card.querySelector('[data-video-id]');play.hidden=false;button.hidden=true;play.focus();
  }));
  document.querySelectorAll('.g-form').forEach(form => form.addEventListener('submit', () => {
    // The browser submits directly to the existing provider. Never simulate success.
    form.querySelector('.g-form-status').textContent='Opening Mailchimp to complete signup. This page does not confirm your subscription or email delivery.';
  }));
})();
