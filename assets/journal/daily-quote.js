(() => {
  const target = document.querySelector('[data-daily-quote]');
  if (!target) return;
  const quotes = ["Equality isn’t given; it’s reborn in the hearts of those who refuse to let it die.", "You can’t fight what you don’t face.", "When the promise breaks, the heart must carry it.", "They call it rebellion when you love who you want.", "You can’t close a revolving door, but you can get out.", "You can burn every bridge behind you, but ashes don’t rebuild paths.", "When the fire dies, silence becomes the loudest scream.", "I gave my life so yours could live—the heart that glows is the one that gave.", "Some bonds burn brighter... until they consume you.", "Everyone has something to say, but gets real quiet when it’s their turn.", "It doesn’t matter what they say; they couldn’t handle it anyway.", "I can’t draw or sing, but these are my words, and I say what I mean.", "Strength is quiet until it roars.", "Even broken steel remembers first.", "Love doesn’t ask permission to exist.", "Truth dances in silence.", "Reflection is rebellion."];
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Chicago', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(new Date()).filter(p => p.type !== 'literal').map(p => [p.type, Number(p.value)]));
  const day = Math.floor(Date.UTC(parts.year, parts.month - 1, parts.day) / 86400000);
  target.textContent = quotes[((day % quotes.length) + quotes.length) % quotes.length];
})();
