# GhostHeart website finishing pass

Public website scope: searchable film and recording libraries; current Rebellion link; Human Too film connection; The Dad in Fatherhood; nine consistently presented thematic collections with Angel before Fatherhood; original 17 quotes server-rendered with copy/search/deep links; current story replaces taxonomy hub; older reflection URLs preserved and excluded from search discovery; mission has practical next steps; signup guidance and accessible navigation are consistent. No original releases, audio, lyrics or manuscript chapters were deleted, combined or newly published.

Mailchimp: authentication blocker persists. Existing audience and form destination retained. Prepared welcome templates include provider footer/unsubscribe merge tags. Welcome activation, sending-domain verification, subscriber confirmation, delivered email, unsubscribes, newsletter scheduling and social scheduling are NOT verified or activated. No real signup or email send occurs in browser tests.

Build command: python3 .github/scripts/build_site.py. This runs the existing gateway and journal generators plus final legacy reconciliation. Rebuilds use .github/content/site-library.json, preserving the exact public quotes, recording cards and collection inputs.
