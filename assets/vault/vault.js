(() => {
  const root = document.querySelector('.vault-page');
  if (!root) return;
  const buttons = [...root.querySelectorAll('[data-vault-filter]')];
  const cards = [...root.querySelectorAll('.vault-item')];
  const input = root.querySelector('#vault-search');
  const clear = root.querySelector('#vault-clear');
  const count = root.querySelector('#vault-count');
  const empty = root.querySelector('#vault-empty');
  let filter = 'featured';

  function render() {
    const query = input.value.trim().toLocaleLowerCase();
    let shown = 0;
    for (const card of cards) {
      const category = filter === 'all' || card.dataset.vaultKind === filter ||
        (filter === 'featured' && card.dataset.vaultFeatured === 'true');
      const match = !query || card.dataset.vaultSearch.includes(query);
      card.hidden = !(category && match);
      if (!card.hidden) shown++;
    }
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.vaultFilter === filter)));
    count.textContent = `${shown} ${shown === 1 ? 'selection' : 'selections'} shown.`;
    empty.hidden = shown !== 0;
    if (!shown) empty.textContent = filter === 'shorts' && !query
      ? 'Public Shorts are being gathered. Explore songs, videos, and quotes for now.'
      : 'No matches. Try another title or theme.';
  }

  buttons.forEach(button => button.addEventListener('click', () => { filter = button.dataset.vaultFilter; render(); }));
  input.addEventListener('input', () => { if (input.value.trim()) filter = 'all'; render(); });
  clear.addEventListener('click', () => { input.value = ''; filter = 'featured'; render(); input.focus(); });
  render();
})();
