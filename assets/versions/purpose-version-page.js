(() => {
  const parts = document.querySelector('.three-part-rail');
  if (parts && !document.querySelector('.full-site-rail')) {
    const gateway = document.createElement('nav');
    gateway.className = 'full-site-rail';
    gateway.setAttribute('aria-label', 'Explore the full GhostHeart site');
    gateway.innerHTML = '<div class="wrap full-site-grid"><a href="index.html#home">Home</a><a href="GhostHeart_Videos.html">Videos</a><a href="GhostHeart_Songs.html">Songs</a><a href="GhostHeart_Quotes.html">Quotes</a><a href="GhostHeart_Resources.html">Resources</a><a href="GhostHeart_Projects.html">Projects</a></div>';
    parts.insertAdjacentElement('afterend', gateway);
  }

  const purposeSignals = {
    mission: {
      label: 'Mission',
      wound: { kicker: 'The wound', title: 'What Mission answers', copy: 'Mission answers the years GhostHeart was told his life had no direction.' },
      vow: { kicker: 'The vow', title: 'What GhostHeart chooses', copy: 'He turns survival into work that serves people who feel unseen.' },
      action: { kicker: 'The action', title: 'How Mission moves', copy: 'Build the platforms. Tell the truth. Leave a door open behind him.' }
    },
    hope: {
      label: 'Hope',
      wound: { kicker: 'The wound', title: 'What Hope answers', copy: 'Hope answers every night GhostHeart believed the story had already ended.' },
      vow: { kicker: 'The vow', title: 'What GhostHeart chooses', copy: 'He keeps one ember alive even when certainty is gone.' },
      action: { kicker: 'The action', title: 'How Hope moves', copy: 'Keep moving. Keep creating. Make survival visible.' }
    },
    father: {
      label: 'Father',
      wound: { kicker: 'The wound', title: 'What Father answers', copy: 'Father answers the absence and instability GhostHeart refuses to repeat.' },
      vow: { kicker: 'The vow', title: 'What GhostHeart chooses', copy: 'He chooses presence, protection, and love that shows up.' },
      action: { kicker: 'The action', title: 'How Father moves', copy: 'Stand steady. Listen fully. Build safety through action.' }
    },
    brother: {
      label: 'Brother',
      wound: { kicker: 'The wound', title: 'What Brother answers', copy: 'Brother answers the isolation and the years GhostHeart carried everything alone.' },
      vow: { kicker: 'The vow', title: 'What GhostHeart chooses', copy: 'He chooses loyalty without possession and truth without abandonment.' },
      action: { kicker: 'The action', title: 'How Brother moves', copy: 'Stand beside. Stay real. Move together.' }
    },
    son: {
      label: 'Son',
      wound: { kicker: 'The wound', title: 'What Son answers', copy: 'Son answers the roots GhostHeart inherited but did not choose.' },
      vow: { kicker: 'The vow', title: 'What GhostHeart chooses', copy: 'He honors where he came from without surrendering who he becomes.' },
      action: { kicker: 'The action', title: 'How Son moves', copy: 'Name the roots. Break the cycle. Choose the next branch.' }
    }
  };

  const purposeKey = document.body.dataset.purpose;
  const activePurpose = purposeSignals[purposeKey];
  const signalButtons = [...document.querySelectorAll('.signal-choice')];
  const reveal = document.getElementById('purpose-reveal');
  const revealKicker = document.getElementById('purpose-reveal-kicker');
  const revealTitle = document.getElementById('purpose-reveal-title');
  const revealCopy = document.getElementById('purpose-reveal-copy');
  const progress = reveal ? [...reveal.querySelectorAll('.signal-progress span')] : [];
  const signalOrder = ['wound', 'vow', 'action'];

  const selectSignal = (key) => {
    if (!activePurpose || !activePurpose[key] || !reveal) return;
    const signal = activePurpose[key];
    const activeIndex = signalOrder.indexOf(key);
    reveal.dataset.signal = key;
    revealKicker.textContent = signal.kicker;
    revealTitle.textContent = signal.title;
    revealCopy.textContent = signal.copy;
    reveal.classList.remove('is-changing');
    void reveal.offsetWidth;
    reveal.classList.add('is-changing');
    signalButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.signal === key)));
    progress.forEach((bar, index) => bar.classList.toggle('is-active', index === activeIndex));
    const progressGroup = reveal.querySelector('.signal-progress');
    if (progressGroup) progressGroup.setAttribute('aria-label', 'Signal ' + (activeIndex + 1) + ' of 3');
  };

  signalButtons.forEach((button, index) => {
    button.addEventListener('click', () => selectSignal(button.dataset.signal));
    button.addEventListener('keydown', (event) => {
      let targetIndex;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') targetIndex = (index + 1) % signalButtons.length;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') targetIndex = (index - 1 + signalButtons.length) % signalButtons.length;
      if (event.key === 'Home') targetIndex = 0;
      if (event.key === 'End') targetIndex = signalButtons.length - 1;
      if (targetIndex === undefined) return;
      event.preventDefault();
      signalButtons[targetIndex].focus();
      signalButtons[targetIndex].click();
    });
  });

  const switcher = document.querySelector('.purpose-switcher');
  const links = switcher ? [...switcher.querySelectorAll('.switch-link')] : [];

  links.forEach((link, index) => {
    link.addEventListener('keydown', (event) => {
      let targetIndex;
      if (event.key === 'ArrowRight') targetIndex = (index + 1) % links.length;
      if (event.key === 'ArrowLeft') targetIndex = (index - 1 + links.length) % links.length;
      if (event.key === 'Home') targetIndex = 0;
      if (event.key === 'End') targetIndex = links.length - 1;
      if (targetIndex === undefined) return;
      event.preventDefault();
      links[targetIndex].focus();
    });
  });
})();
