(() => {
  const players = document.querySelectorAll('audio[data-preview-seconds]');

  players.forEach((player) => {
    const limit = Number(player.dataset.previewSeconds);
    const status = document.getElementById(player.dataset.previewStatus || '');
    const shell = player.closest('.featured-preview');
    const toggle = shell?.querySelector('[data-preview-toggle]');
    const action = shell?.querySelector('[data-preview-action]');
    const progress = shell?.querySelector('[data-preview-progress]');
    const time = shell?.querySelector('[data-preview-time]');
    let completed = false;

    if (!Number.isFinite(limit) || limit <= 0 || !toggle) return;

    const updateStatus = (message) => {
      if (status) status.textContent = message;
    };

    const updateControls = () => {
      const elapsed = Math.min(player.currentTime, limit);
      const remaining = Math.max(0, Math.ceil(limit - elapsed));
      if (progress) progress.style.width = `${(elapsed / limit) * 100}%`;
      if (time) {
        time.textContent = `0:${String(remaining).padStart(2, '0')}`;
        time.setAttribute('aria-label', `${remaining} seconds remaining`);
      }
    };

    toggle.addEventListener('click', () => {
      if (player.paused) {
        if (completed || player.currentTime >= limit - .15) player.currentTime = 0;
        completed = false;
        player.play().catch(() => updateStatus('Preview could not start. Use Watch or Stream instead.'));
      } else {
        player.pause();
      }
    });

    player.addEventListener('play', () => {
      toggle.setAttribute('aria-pressed', 'true');
      toggle.setAttribute('aria-label', 'Pause 30-second preview');
      if (action) action.textContent = 'Pause';
      updateStatus(`${limit}-second preview • playing`);
    });

    player.addEventListener('pause', () => {
      toggle.setAttribute('aria-pressed', 'false');
      toggle.setAttribute('aria-label', completed ? 'Replay 30-second preview' : 'Play 30-second preview');
      if (action) action.textContent = completed ? 'Replay' : 'Play';
      if (!completed && player.currentTime > 0 && player.currentTime < limit - .15) {
        updateStatus(`${limit}-second preview • paused`);
      }
    });

    player.addEventListener('timeupdate', () => {
      updateControls();
      if (player.currentTime < limit) return;
      completed = true;
      player.pause();
      player.currentTime = 0;
      updateStatus(`${limit}-second preview • complete`);
      updateControls();
    });

    player.addEventListener('error', () => {
      toggle.disabled = true;
      updateStatus('Preview unavailable. Use Watch or Stream instead.');
    });

    updateControls();
  });
})();
