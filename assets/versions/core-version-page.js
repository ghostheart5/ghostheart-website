(() => {
  const parts = document.querySelector('.three-part-rail');
  if (parts && !document.querySelector('.full-site-rail')) {
    const gateway = document.createElement('nav');
    gateway.className = 'full-site-rail';
    gateway.setAttribute('aria-label', 'Explore the full GhostHeart site');
    gateway.innerHTML = '<div class="wrap full-site-grid"><a href="index.html#home">Home</a><a href="GhostHeart_Videos.html">Videos</a><a href="GhostHeart_Songs.html">Songs</a><a href="GhostHeart_Quotes.html">Quotes</a><a href="GhostHeart_Resources.html">Resources</a><a href="GhostHeart_Projects.html">Projects</a></div>';
    parts.insertAdjacentElement('afterend', gateway);
  }

  const stage = document.querySelector('.stage-shell');
  const audio = document.getElementById('version-voice-player');
  const button = document.getElementById('version-play-button');
  const status = document.getElementById('version-voice-status');
  const title = document.querySelector('h1')?.textContent?.trim() || 'This Version';

  if (!stage || !audio || !button || !status) return;

  const setIdle = (message = `${title} voice ready.`) => {
    stage.classList.remove('is-playing');
    button.textContent = audio.currentTime > 0 && !audio.ended ? 'Resume voice' : 'Hear this voice';
    status.textContent = message;
  };

  button.addEventListener('click', async () => {
    if (!audio.paused) {
      audio.pause();
      audio.currentTime = 0;
      setIdle(`${title} voice stopped.`);
      return;
    }

    try {
      await audio.play();
    } catch (error) {
      setIdle('Playback was blocked. Use the audio controls below.');
    }
  });

  audio.addEventListener('loadedmetadata', () => {
    const seconds = Math.round(audio.duration);
    const duration = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    setIdle(`${title} voice ready • ${duration}`);
  });
  audio.addEventListener('play', () => {
    stage.classList.add('is-playing');
    button.textContent = 'Stop voice';
    status.textContent = `Playing ${title}.`;
  });
  audio.addEventListener('pause', () => {
    if (!audio.ended && audio.currentTime > 0) setIdle(`${title} voice paused.`);
  });
  audio.addEventListener('ended', () => {
    stage.classList.remove('is-playing');
    button.textContent = 'Hear this voice again';
    status.textContent = `${title} voice finished.`;
  });
  audio.addEventListener('error', () => {
    stage.classList.remove('is-playing');
    button.textContent = 'Voice unavailable';
    status.textContent = `${title} could not load.`;
  });
})();
