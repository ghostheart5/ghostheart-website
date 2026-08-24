(() => {
  const links = [...document.querySelectorAll('.purpose-switcher .switch-link')];

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
