# Collection scope and sharing review

Repository: `ghostheart5/ghostheart-website`. Review branch: `codex/collection-scope-sharing-20261012`, starting from verified deployed main `6000b1c3a69554f88c276f59ebd44aabff931a91` (PR #46). The allocated checkout was clean. The only open PR inspected was the unrelated held blog-comments draft #32; it was not changed. No repository AGENTS.md or .agents/skills instructions were present. The owner approved these fixes for review on October 12, 2026 at 21:17:08 UTC. Applied GhostHeart preflight/web-builder skills and AI agents for collection wording, browser verification, independent review, and a separate homepage proposal.

## Changes

- Eight inaccurate paragraph nouns change from album to collection across Broken Man, Fatherhood, Human After All, Love Is Love, The Ones We Carry, and You're Not God. Every other source-library field remains identical, including genuine release/recording titles, tracks, legacy IDs, quotes and film mappings.
- Film links to the known nine thematic website routes now say Explore the collection or GhostHeart collection. Sixteen visible catalog-link labels and twelve associated accessible labels are corrected. Destination URLs, titles, video IDs and versions stay the same. The generator handles accessible labels independently of visible labels so repeat builds repair an already-converted catalog.
- Vault identifies itself as a selected collection in its hero and description, with a prominent normal-page Browse Films action. Its 39 cards remain identical: 11 songs, six videos, five Shorts and 17 quotes. Films retains twelve visible cards. The link does not claim a complete artist catalog.
- The relationship page's Open Graph image uses the existing displayed `ghostheart-rebel-in-the-rain.png`, with actual dimensions 1374 by 1145 and the same accurate alt text as its displayed image. Canonical URL, page identity, prose and artwork remain unchanged.
- The existing World verifier now checks scope, visible Films navigation, relationship metadata, classification wording, and catalog accessible labels, alongside PR #46's film/version/preview-fragment invariants.

## Preservation and verification

See `validation.json`, `preservation.json` and `changed-paths.txt` for the measured checks and exact inventory. All 151 artwork/media files match their original Git blobs. All existing IDs and destinations on changed HTML pages are retained. The homepage, Music, recordings, Follow, Live, Story, resources, privacy, projects and historical Angel collection output remain unchanged. No genuine recording title or listening source is renamed.

Local canonical build and repeat generation pass; all measured HTML/CSS/JS/JSON/XML files are stable after the repeat. Tree validation reports 64 HTML pages, 258 published files, zero errors. The eight Awakening tests, reviewed-site/World/Cruel checks, thirteen JavaScript syntax checks, Vault filters and diff check pass. Python 3.14, BeautifulSoup 4.15.0 and Pillow 12.3.0 were available locally; the existing hosted workflow uses its pinned dependencies.

Initial local tests encountered Windows sandbox TEMP permissions; all eight affected tests passed with TEMP/TMP inside the allocated workspace. Independent review caught an em-dash accessible-label mismatch before commit. A supplementary browser data check also found two related links labeled GhostHeart album despite targeting the same thematic collection. Added regressions failed against both stale catalog forms, then passed after correction and regeneration. An unrelated generated GATEWAY_STATUS note was restored to main's exact bytes after builds; no unrelated documentation edit is included.

Browser evidence is recorded separately in `browser-summary.json`. Local previews use provider-request blocking and perform no signup or email action. A local browser and generated source do not establish any new public deployment.

## Separate homepage proposal

The homepage source is unchanged. A review-only Current/Proposed mockup lives outside the repository at allocated-workspace `evidence/next-pass-20261012/homepage-proposal.html`, with a brief, twelve passing checks and eight screenshots. Local preview: `http://127.0.0.1:8768/homepage-proposal.html`.

The proposal keeps every existing word, route, artwork and lower-section order. It puts the unchanged identity copy on a dark panel beside the full rooftop artwork on desktop, and stacks the artwork below the actions on mobile. Experience Cruel remains primary and still scrolls to the existing feature. Story/support links remain visible. This is a design choice requiring separate approval for production implementation. At 640px the full stacked artwork makes the hero taller; the desktop opening is shorter and visually calmer.

## Limits and review boundary

No merge, deployment, real signup/email, provider account action, automation, permissions, protected project, private worksite or media creation occurred. The prior successful PR #46 deployment remains verified. Existing windows/processes were not closed.

The original Rebel image was inspected at full size. A hypothetical centered 1.91:1 social-card crop could cut the top logo and portions of the heads because the original image is 1.20:1. The full original image is supplied unchanged; actual third-party card rendering, cropping and cache refresh remain unverified. No new crop asset was created.

Physical mobile devices, native browser zoom, comprehensive screen-reader/contrast/performance review, streamed provider playback, real opt-in/delivery/unsubscribe and actual social-provider previews remain untested in this pass. The 640 CSS-pixel case is reflow evidence, not native 200% zoom certification. The subjective re-audit score is not a test target or technical certification.
