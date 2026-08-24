(() => {
  const stage = document.querySelector('.stage-shell');
  const audio = document.getElementById('version-voice-player');
  const status = document.getElementById('version-voice-status');
  const title = document.querySelector('h1')?.textContent?.trim() || 'This Version';

  if (!stage || !audio || !status) return;

  const setIdle = (message = `${title} voice ready.`) => {
    stage.classList.remove('is-playing');
    status.textContent = message;
  };

  audio.addEventListener('loadedmetadata', () => {
    const seconds = Math.round(audio.duration);
    const duration = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    setIdle(`${title} voice ready • ${duration}`);
  });
  audio.addEventListener('play', () => {
    stage.classList.add('is-playing');
    status.textContent = `Playing ${title}.`;
  });
  audio.addEventListener('pause', () => {
    if (!audio.ended && audio.currentTime > 0) setIdle(`${title} voice paused.`);
  });
  audio.addEventListener('ended', () => {
    stage.classList.remove('is-playing');
    status.textContent = `${title} voice finished.`;
  });
  audio.addEventListener('error', () => {
    stage.classList.remove('is-playing');
    status.textContent = `${title} could not load.`;
  });
})();
