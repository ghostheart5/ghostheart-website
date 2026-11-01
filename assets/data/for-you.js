// "For how you feel" picks on the Vault page (site audit 2026-11-01, owner yes).
// Hand-curated: every "why" line is wording already published on the site (film
// descriptions, blog summaries, passage subtitles, Short titles, the quotes).
// Songs without a published description are left out until one is approved.
// moods: strength, judged, change, love, protect, alone. how: line, watch, listen, read.
window.GHOSTHEART_FOR_YOU = {
  moods: [
    ['strength', 'I need strength'],
    ['alone', 'I want to feel less alone'],
    ['judged', 'I feel judged'],
    ['change', 'Something has to change'],
    ['love', 'I’m thinking about love'],
    ['protect', 'I want to look out for someone']
  ],
  how: [
    ['line', 'Just a line', 'seconds'],
    ['watch', 'Watch', '1–5 minutes'],
    ['listen', 'Listen', 'about 3 minutes'],
    ['read', 'Read', '5 minutes or more']
  ],
  picks: [
    {id: 'film-this-is-ghostheart', how: 'watch', title: 'This Is GhostHeart', kind: 'Film', href: '/GhostHeart_Videos.html#film-this-is-ghostheart', why: 'The name, the scars, and the reason a hidden heart chose to be seen.', moods: ['alone', 'strength']},
    {id: 'film-ghosthearts-oath', how: 'watch', title: 'GhostHeart’s Oath', kind: 'Film', href: '/GhostHeart_Videos.html#film-ghosthearts-oath', why: 'The promise to protect the light in others.', moods: ['protect', 'strength']},
    {id: 'film-i-wont-pretend-to-speak-for-you', how: 'watch', title: 'I Won’t Pretend to Speak for You', kind: 'Film', href: '/GhostHeart_Videos.html#film-i-wont-pretend-to-speak-for-you', why: 'One marriage began beneath a church-house light. Two women began with trembling hands and borrowed flowers.', moods: ['love', 'judged']},
    {id: 'film-hey-preacher-man', how: 'watch', title: 'Hey Preacher Man', kind: 'Film', href: '/GhostHeart_Videos.html#film-hey-preacher-man', why: 'A direct answer to the judgment that tried to define a life from the outside.', moods: ['judged', 'strength']},
    {id: 'film-that-aint-holy', how: 'watch', title: 'That Ain’t Holy', kind: 'Film', href: '/GhostHeart_Videos.html#film-that-aint-holy', why: 'Mercy should not check your pockets at the door. A father-and-son story about poverty, dignity, and who gets judged.', moods: ['judged', 'protect', 'change']},
    {id: 'short-a-child-should-never-have-to-earn-love', how: 'watch', title: 'A Child Should Never Have to Earn Love', kind: 'Short', href: 'https://www.youtube.com/shorts/bkm3czEmk5g', why: 'A Short from That Ain’t Holy.', moods: ['protect', 'love']},
    {id: 'short-son-you-did-no-wrong', how: 'watch', title: 'Son, You Did No Wrong', kind: 'Short', href: 'https://www.youtube.com/shorts/5b43JyYmIts', why: 'A Short from That Ain’t Holy.', moods: ['judged', 'alone']},
    {id: 'short-porch-light', how: 'watch', title: 'Would You Leave the Porch Light On?', kind: 'Short', href: 'https://www.youtube.com/shorts/5HUWedEnnsA', why: 'A Short from That Ain’t Holy.', moods: ['protect', 'alone']},
    {id: 'short-mercy-empty-seat', how: 'watch', title: 'Mercy That Leaves an Empty Seat', kind: 'Short', href: 'https://www.youtube.com/shorts/ofU09J3bkHI', why: 'A Short from That Ain’t Holy.', moods: ['judged', 'change']},
    {id: 'song-cruel', how: 'listen', title: 'Cruel', kind: 'Song', href: '/music/#song-cruel', why: 'From GhostHeart’s Awakening. Something needs to change.', moods: ['change']},
    {id: 'song-this-is-ghostheart', how: 'listen', title: 'This Is GhostHeart', kind: 'Song', href: '/music/#song-this-is-ghostheart', why: 'The name, the scars, and the reason a hidden heart chose to be seen.', moods: ['alone', 'strength']},
    {id: 'song-ghosthearts-oath', how: 'listen', title: 'GhostHeart’s Oath', kind: 'Song', href: '/music/#song-ghosthearts-oath', why: 'The promise to protect the light in others.', moods: ['protect']},
    {id: 'song-i-wont-pretend-to-speak-for-you', how: 'listen', title: 'I Won’t Pretend to Speak for You', kind: 'Song', href: '/music/#song-i-wont-pretend-to-speak-for-you', why: 'Fifty years later, this song asks what a lifetime of love can tell us that appearances cannot.', moods: ['love']},
    {id: 'song-hey-preacher-man', how: 'listen', title: 'Hey Preacher Man', kind: 'Song', href: '/music/#song-hey-preacher-man', why: 'A direct answer to the judgment that tried to define a life from the outside.', moods: ['judged', 'strength']},
    {id: 'song-that-aint-holy', how: 'listen', title: 'That Ain’t Holy', kind: 'Song', href: '/music/#song-that-aint-holy', why: 'Mercy should not check your pockets at the door.', moods: ['judged', 'protect']},
    {id: 'read-this-is-ghostheart', how: 'read', title: 'This is GhostHeart.', kind: 'Blog', href: '/journal/this-is-ghostheart.html', why: 'A heart that survived, and a question about what comes next.', moods: ['alone', 'strength']},
    {id: 'read-ghosthearts-oath', how: 'read', title: 'GhostHeart’s Oath', kind: 'Blog', href: '/journal/ghosthearts-oath.html', why: 'What might protecting the light in others look like in an ordinary moment?', moods: ['protect']},
    {id: 'read-youre-not-god', how: 'read', title: 'You’re Not God', kind: 'Blog', href: '/journal/youre-not-god.html', why: 'A question about belief, judgement and the difference between care and control.', moods: ['judged']},
    {id: 'read-cruel', how: 'read', title: 'Cruel — Something Needs to Change', kind: 'Blog', href: '/journal/cruel-something-needs-to-change.html', why: 'What happens after the video ends?', moods: ['change']},
    {id: 'read-papa', how: 'read', title: 'Papa Didn’t Raise No Fool', kind: 'Passage', href: '/passages/papa-didnt-raise-no-fool.html', why: 'A backbone and a heart.', moods: ['strength']},
    {id: 'read-im-not', how: 'read', title: 'I’m Not', kind: 'Passage', href: '/passages/im-not.html', why: 'More than one chapter.', moods: ['alone', 'strength']},
    {id: 'read-1950s', how: 'read', title: 'It’s Not the 1950s', kind: 'Passage', href: '/passages/its-not-the-1950s.html', why: 'Grandma remembers the rights people fought for—and the pain behind the victory speeches.', moods: ['change', 'love']},
    {id: 'quote-13', how: 'line', title: 'Strength is quiet until it roars.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-13', why: 'From the Quote Vault.', moods: ['strength']},
    {id: 'quote-14', how: 'line', title: 'Even broken steel remembers first.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-14', why: 'From the Quote Vault.', moods: ['strength', 'alone']},
    {id: 'quote-02', how: 'line', title: 'You can’t fight what you don’t face.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-02', why: 'From the Quote Vault.', moods: ['change', 'strength']},
    {id: 'quote-01', how: 'line', title: 'Equality isn’t given; it’s reborn in the hearts of those who refuse to let it die.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-01', why: 'From the Quote Vault.', moods: ['change']},
    {id: 'quote-17', how: 'line', title: 'Reflection is rebellion.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-17', why: 'From the Quote Vault.', moods: ['change', 'alone']},
    {id: 'quote-15', how: 'line', title: 'Love doesn’t ask permission to exist.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-15', why: 'From the Quote Vault.', moods: ['love', 'judged']},
    {id: 'quote-04', how: 'line', title: 'They call it rebellion when you love who you want.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-04', why: 'From the Quote Vault.', moods: ['love', 'judged']},
    {id: 'quote-08', how: 'line', title: 'I gave my life so yours could live—the heart that glows is the one that gave.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-08', why: 'From the Quote Vault.', moods: ['protect']},
    {id: 'quote-03', how: 'line', title: 'When the promise breaks, the heart must carry it.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-03', why: 'From the Quote Vault.', moods: ['protect', 'alone']},
    {id: 'quote-11', how: 'line', title: 'It doesn’t matter what they say; they couldn’t handle it anyway.', kind: 'Quote', href: '/GhostHeart_Quotes.html#quote-11', why: 'From the Quote Vault.', moods: ['judged']}
  ]
};
