# Website review candidate — 2026-10-19

Prepared locally; NOT published, pushed, merged, committed, or deployed.

## Source and isolation
- Origin freshly verified: https://github.com/ghostheart5/ghostheart-website.git
- Remote main and candidate HEAD: ca5dbd9ab956bd2869d6523ed66eea6fe4138495.
- Branch: codex/featured-preview-chicago-20261019.
- Isolated linked worktree: C:/jtmp/ghostheart-featured-review-20261019.
- Established owning repository: C:/Users/keegan radetski/Documents/ChatGPT/website_release (website junction points here). Original HEAD 4fa50c4651ebc24a17dcca18ddc659e2e2f746ec on codex/signup-note-cleanup-20260906, dirty; preserved.
- HQ 07_WEBSITE/Working_Source: main at 8526d03b8298dcb1964c1113d2cd51edc3162e82, dirty; preserved.
- HQ 07_WEBSITE/Working_Source_2026-10-08_Repair: codex/website-connection-repair-20261009 at 8b8fe98db983fdd96a68108107152f0445ede3b4, dirty; preserved.
- Read HQ AGENTS.md, website status, owner/workforce rules, architecture and Knowledge Core. No repository AGENTS.md was found in the candidate tracked files. Available 50-thread inventory showed no active native website editing owner; this is bounded discovery, not proof of all processes.
- No new project or backup collection, bulk clone, or asset migration into HQ. This worktree is disposable engineering isolation, not a new HQ.

## Changes
- Homepage and Films feature the exact supplied published preview https://www.youtube.com/watch?v=LPIHyzh4k_4, FEATURED NOW, It's Not the 1950s, exact supplied body, and Watch the preview.
- Cruel catalogue article/video ID retained. Removed obsolete homepage Cruel audio handler along with the replaced player.
- Long homepage title sized to fit desktop/mobile. Text/play-button treatment uses no invented or unverified thumbnail.
- Journal loads the shared America/Chicago date selector. All 17 quotes are unchanged; numbered Quote Vault link and daily counter stay aligned.
- Edited real LOUD templates and reviewed journal generator source so rebuilding preserves the fixes. Added focused regression test to website-checks CI and updated the old homepage-Cruel assertion.

## Validation
PASS: complete build with Python UTF-8 mode (`C:/Python314/python.exe -X utf8 .github/scripts/build_site.py`). Generated unrelated changes were removed from the candidate diff.
PASS: site validator, 65 HTML pages / 268 published files / zero errors.
PASS: test_awakening.py, 8 tests (accessible TEMP/TMP required in this sandbox).
PASS: verify_reviewed_site.py; verify_world_review.py; test_vault_filters.cjs.
PASS: test_featured_quote.cjs, all 17 quote literals match baseline; 32 cases across UTC/Los Angeles/Tokyo/Chicago covering Central midnight, year rollover and spring/fall DST; correct number and link; featured text/URL and preserved Cruel.
PASS: node syntax check of daily-quote.js; Git diff whitespace check.
PASS: Chrome layouts at 390 and 1440 CSS pixels, homepage/films/journal, no horizontal overflow, exact CTA URLs, aligned journal counter/link, zero JavaScript errors. Browser check script: C:/jtmp/featured-browser-check.cjs.
LIMIT: test_cruel_reading.py fails its exact raw-byte SHA check on Windows CRLF checkout. Git HEAD blob SHA is exactly the expected 6b6c074b85b70685907000a42a80a606611b3a7e179a2d285a6ef9644f135b4d; working source equals it after CRLF normalization. Approved reading not edited; this is not a clean full-CI claim.
LIMIT: no YouTube playback or public deployment acceptance was performed.

## Review previews
Local files under C:/GhostHeartLocal/playwright-output/website-featured-20261019/:
- home-desktop.png, home-mobile.png (featured section)
- films-desktop.png, films-mobile.png
- journal-1440.png, journal-390.png
No Library uploads/IDs were created. Browser profile/output stayed outside OneDrive in owner-designated folders.

## Axiomara and remaining exact bindings
Inspected GhostHeart_Projects.html and .github/scripts/build_projects.py. Generator currently emits an existing Google Play availability claim and a text-only Axiomara feature; this task did not certify Play release success or change that claim.
Inspected existing axiomora/Publication registers, Screenshots and Video/Axiomara_DaVinci_20261011 records. They identify four older Moto screenshots and a narrated reference/edit package; START HERE explicitly says no final upload/publication and captions still need listening review. No final YouTube URLs were found in those publication records. Older listing approval is not current website artwork approval.
Missing: exact current approved Axiomara website artwork path/Library ID plus version/hash and usage binding; exact final English trailer YouTube URL; exact final Spanish trailer YouTube URL; approved language/title/thumbnail mapping. No guessed assets/URLs inserted.

## Approval boundary
Root must obtain exact publication approval for this candidate diff and reviewed presentation before push/merge/deploy. Full film remains scheduled October 19 noon America/Chicago per supplied authority; candidate claims only the preview is available. No new release dates or campaign quotes invented. Passages scheduler, blank ImNot/1950s draft worksheets, readiness flags and catch-up behavior unchanged. Work HQ auth, Azure, Planner and social queue untouched.

## Follow-up correction: stable quote fixture and Cruel history
The new regression test now contains a fixed literal fixture of all 17 exact quotes from baseline ca5dbd9ab956bd2869d6523ed66eea6fe4138495. It no longer reads Git HEAD or launches any subprocess. It passed on the candidate pages (which have no inline Q array), with all child_process execution methods deliberately blocked, and again after the full build. This supersedes the earlier package's post-commit CI blocker.

Rerun results: full build PASS; validator PASS (65 pages / zero errors); 32 timezone/boundary cases and all 17 literal comparisons PASS; 8 Awakening tests PASS; reviewed-site, world-review and Vault-filter checks PASS; JavaScript syntax PASS. The original raw-byte Cruel test still fails on Windows CRLF and was not edited or bypassed. Git blobs, staged source and generated Cruel article remain unchanged; normalized working text equals committed bytes. No full green-CI claim is made for the Windows checkout.

Like-for-like historical comparison is resolved: PR41 head 14231715831779ce1acdf580e5c2237a0743b132 contains title/body source SHA256 66233e7ef339b0b9838cb0c839c97041345b0e9d8e8a6e39e08e42b09caf0776, 21 paragraphs, matching generated HTML and journal JSON. Pre-existing PR51 merge 082ef573cd408f19e6c1c5c5ce20bd8535f5aed1 revised it to 7 paragraphs and SHA256 6b6c074b85b70685907000a42a80a606611b3a7e179a2d285a6ef9644f135b4d, also matching HTML/JSON. PR51's description records owner authorization; the underlying owner receipt was not independently recovered. Original package hash 11d05eecfd2cee12df407067e01a05ae641740f5a06cd18a2566f4415e3011ac was not independently reproduced. This is historical revision outside our patch, not a change introduced by this candidate.

Scope re-review: 13 changed files; no new approval flags, dates, catch-up, publication permissions, disabled checks or unrelated generated content. Reviewed-input and active journal generators only maintain the quote number/link. The World check replaces the intentionally obsolete homepage Cruel audio assertion with exact FEATURED NOW / preview URL / CTA / no-audio assertions. CI adds the fixed regression test. Screenshot bytes and identities are unchanged. This is a self-review, not a separate reviewer acceptance.
