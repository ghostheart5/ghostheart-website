# October 12 public-site repair evidence

Repository: `ghostheart5/ghostheart-website`. Isolated checkout started clean on `main` at `8931b364c584f0ed9f332ee7e0b9bd8658f204af`; the remote still matched that base at the final read-only check. Work branch: `codex/public-site-audit-repairs-20261012`. Evidence recorded October 12, 2026. No AGENTS.md or repository .agents/skills instructions were present. Applied GhostHeart preflight/web-builder skills; three AI agents handled catalog repairs, navigation/metadata, and browser QA.

The sole open pull request inspected was #32, the held blog-comments readiness draft. Its comment/backend work was not adopted or changed. The linked ChatGPT audit required login; the supplied findings were reproduced against the current source and baseline browser preview. The audit's 72/100 score is subjective and is not a technical certification.

## Reproduced problems and repairs

- Four recording Watch destinations resolved to hidden empty spans on Films. The spans existed, so ordinary fragment validation passed. Matching visible player cards now exist for the verified public uploads. Tests assert visible cards and video IDs, including every recording-to-Films action and linked cover.
- The Dad action names its actual lyric video, **The Dad I Never Had**. Human Too identifies the cinematic remake and its different public YouTube title, **Why You Should Never Judge Someone's Worst Day**. The Man Beneath the Moon retains **Fixed vocal ending**. Rebellion uses its official music video. Recording titles and original listening links remain intact.
- Ashes & Embers falsely offered all five films and opened Hey Preacher Man. It now offers the two verified individual uploads, Just Not This Morning and Look at Me. The five distinct YouTube audio links remain listening actions.
- Cruel's existing public video is now discoverable in Films using existing artwork. Films has 12 visible cards; the curated Vault retains 39 items, including its existing six videos. Twelve compatibility film aliases remain hidden.
- Music identifies two featured listening collections and eleven previews, with links to Films and the full Released recordings archive. The archive has 14 recording/release entries and 25 listed tracks. Its copy describes that scope without implementation notes; original 3:55 and new 5:30 recording distinctions remain. Legacy thematic collection navigation now says Featured Music when linking to the narrower Music page.
- Current relationship-navigation actions use Rebel naming and the current story route. Historical Angel release titles, collection headings, artwork, and prose remain.
- Music, recordings, Films, Start, Follow, and Blog metadata now describes each page's content while preserving established identity/canonical URLs and images. The two brief song entries are labeled Short song introduction; all five blog entries retain their original prose, dates, slugs, and links.
- Optional signup benefits name music, stories, and films. The provider action, fields, POST mechanism, and confirmation guidance remain unchanged; no new schedule is promised.
- Browser review found a preexisting clipped recordings heading at 320px. A page-specific typography rule below 361px makes it fit while preserving the wording and wider layouts.

## Verified public video identities

Read-only YouTube oEmbed responses identified all seven uploads as GhostHeart's official channel. Metadata verification does not prove playback.

| Work / version | Existing public upload |
| --- | --- |
| The Dad I Never Had, lyric video | https://www.youtube.com/watch?v=cBNxq4y1ahU |
| Human Too, cinematic remake with the public title above | https://www.youtube.com/watch?v=ARCFOZSOC_o |
| The Man Beneath the Moon, fixed vocal ending | https://www.youtube.com/watch?v=_mUU-toMlM8 |
| Rebellion | https://www.youtube.com/watch?v=FaT_Ibrs9Y0 |
| Just Not This Morning | https://www.youtube.com/watch?v=XWmMYqkvdzg |
| Look at Me | https://www.youtube.com/watch?v=nVC1kB0MREA |
| Cruel | https://www.youtube.com/watch?v=9sbFgjM_SDE |

## Passed

- Canonical `build_site.py` full build; repeat-build fingerprints identical for 120 HTML/CSS/JS/JSON/XML files, including the recorded validation artifact.
- `validate_site.py`: 64 HTML pages, 258 published files, 406.5 MiB, zero validation errors. This checks local assets/fragments, not external-provider availability.
- `test_awakening.py`: eight tests. `verify_reviewed_site.py`: 49 navigation shells, 11 MP3s, 15 exact reading paragraphs, 16 unchanged resource cards, five journal entries. `test_cruel_reading.py`: exact approved title and 21 paragraphs. `verify_world_review.py`: repaired visible film destinations, scope/version distinctions, navigation labels, existing Vault and reading boundaries. `test_vault_filters.cjs`: all 39 scoped items/category/search behaviors.
- Node syntax checks for all 13 asset JavaScript files; `git diff --check`.
- Exact repository browser test `test_reviewed_site.cjs` with external requests intercepted: key pages, keyboard/menu behavior, nested 404 recovery, resource filters, 11 audio players.
- Thirty browser layout cases: Music, music hub, recordings, Films, Follow, and Blog at 320/390/640/768/1440 CSS pixels. All have unclipped headings, no horizontal overflow, keyboard Enter/Escape menu behavior with visible 3px focus, and scrolling to the footer. The three changed legacy thematic collection footers also fit at 320px.
- Final recordings navigation uses the existing page gutter; all four approximately 50px-high actions and their 3px keyboard outlines fit within the 320px viewport.
- Seven film journeys identify visible matching cards after default smooth scrolling settles; their user-loaded iframe URLs, close controls and restored focus match their video IDs. Featured Music's archive action lands on a visible archive heading below the sticky header at 320/390/640px. Cruel search shows one card; clearing restores all 12.
- All 151 artwork/media files hash to their original Git blobs. Nine collection source records, all 17 quotes and legacy IDs, 14 recording IDs/titles/track counts, and five journal entries' prose/dates/slugs/links match the base. No artwork, audio, video, or personal story was created or expanded.
- Local muted-browser playback advances and pauses for Cruel and Hey Preacher Man with no media errors. This verifies browser playback state, not audible quality or full-duration listening.
- Local signup validation rejects empty/malformed values; a syntactically valid `.test` address reached a local submit event canceled with `preventDefault`. No provider submission occurred. The UI correctly avoids asserting subscription success or delivery.

## Failed attempts and limits

Initial test attempts encountered Windows sandbox TEMP permissions and locale/CRLF issues. Tests passed after using an allocated temporary directory, `PYTHONUTF8=1`, and restoring the exact committed LF bytes of the approved Cruel source (no repository text change). Python 3.14, BeautifulSoup 4.15.0 and Pillow 12.3.0 were available locally; hosted checks use the repository's existing pinned dependency versions.

The original 320px heading clip was reproduced and repaired. Initial browser scripts also sampled smooth scrolling before it settled and assumed The Dad retained an internal fragment action; corrected final measurements pass all seven journeys. External thumbnails/iframe responses are blocked during local QA, so those tests establish destinations and player controls rather than streamed YouTube playback.

Separate anonymous public playback was attempted for `cBNxq4y1ahU`. Its HTTP 200 page confirmed The Dad I Never Had and the GhostHeart channel. With only exact video-byte and player-metadata retrieval requests allowed (including streaming retrieval POSTs), playback reached 41.123 seconds, then reset with a YouTube provider error. Analytics, account, notification, and other POSTs remained blocked. This is partial playback evidence; stable or end-to-end playback remains unverified under this restricted request filter. The other six repaired public uploads' playback was not attempted. Their identities were verified by oEmbed, not by listening or watching.

Real Mailchimp signup, double-opt-in, welcome activation, delivered email, unsubscribe, anti-spam/provider behavior, sender authentication, and account settings were not exercised. No email, message, production data write, account change, new paid service, merge, or deployment was performed. Actual OS/browser zoom and physical mobile devices were not exercised; the 640 CSS-pixel viewport is a reflow equivalent of a 1280 CSS-pixel viewport at 200% zoom.

The isolated checkout and local preview do not establish a changed live website. Protected HQ/canon/brand records, separate testing project, Axiomara, 12_PROJECTS, private-web, permissions, and automation were not modified. Existing windows and processes were not closed.

## Local evidence

The allocated workspace retains `evidence/preservation.json`, `evidence/verify_preservation.py`, and `evidence/browser-qa/` results/scripts/screenshots. Current preview: `http://127.0.0.1:4178/`; pinned baseline preview: `http://127.0.0.1:4179/`. These are local previews, not public deployment links. `validation.json` summarizes the measured outcomes and `changed-paths.txt` records the exact repair paths.

## Preview fragment compatibility correction

Independent review of the first repair head, `032782f9c83e1b5debbf4f6360ad3b6da7c6adca`, found that regeneration replaced all eleven public `song-audio-track-*` fragments with `preview-track-*` fragments. The first review checks missed this compatibility regression. The correction restores the original IDs directly on the matching visible `li.music-track` rows; no empty compatibility spans are used. Titles, recording-title distinctions, and audio sources remain the same.

The new fast verifier failed on the first-head output with `Published preview fragments changed`, then passed after rebuilding the corrected generator. The persistent browser test freezes every original fragment/title/MP3 mapping from the pre-repair base and checks each destination at 320 and 1440px, including visible matching content, audio controls, viewport position below the header, and overflow. All 22 cases and the full existing browser suite pass. The full build, local tree validator, reviewed/world/Cruel checks, repeat generation and media/prose preservation were rerun for this correction. The PR now has 45 changed paths, including the browser regression test.
