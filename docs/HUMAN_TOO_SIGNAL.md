# Human Too Signal

## Purpose

`Human Too` is the owned GhostHeart release destination for the August 21, 2026 launch. Its campaign message is: **See the person. Not the label.** The page explains the release without presenting GhostHeart as addiction treatment or a substitute for professional support.

## Route

`https://www.myghostheart.com/ghostheart-website/human-too.html`

The root page currently redirects into `ghostheart-website/`, so this route follows the existing deployed file layout.

## Content Ownership

The displayed lyric excerpt is founder-owned material authorized for this page. Do not add complete lyrics without a separate release-content review.

The approved GH-MUS-001 consumer artwork is `ghostheart-website/assets/images/releases/human-too-cover.jpg`, copied from `GH-MUS-001_Human_Too_Cover_3000x3000_RGB.jpg`. It is the required Human Too hero, Open Graph, and Twitter card image. Do not substitute the legacy `Copilot_20260715_184612.png` asset on this release page.

## Release State

The confirmed release date is August 21, 2026. The page is intentionally useful before and after release. Until verified DSP URLs are available, each listening destination remains plain status text. It is not a link, button, or disabled control.

## Artwork Update Procedure

1. Preserve the approved source file outside the website repository with its release records.
2. Add any future approved artwork as a new, release-specific asset under `ghostheart-website/assets/images/releases/`; do not overwrite shared legacy imagery.
3. Update the hero `img`, `og:image`, and `twitter:image` together, using the `https://www.myghostheart.com/` hostname for absolute metadata URLs.
4. Confirm the image dimensions, provenance record, meaningful alt text, metadata values, and local HTTP response.
5. Run the website checks before committing.

## DSP-Link Update Procedure

1. Obtain the exact, verified public destination from the relevant DSP or distributor.
2. Replace only that service's status item in `ghostheart-website/human-too.html` with an accessible `<a>` link using the verified HTTPS URL.
3. Add `data-analytics-event="human_too_listen_click"` to the new link.
4. Confirm the visible service name, destination, and link behavior in a browser.
5. Run the website checks and update this document's release state if needed.

Never insert placeholder URLs, `href="#"`, search links, or guessed service IDs.

## Analytics Event Contract

No analytics provider is configured in this branch, so the page makes no analytics network calls. The following event names are reserved for a future provider integration:

| Event | Trigger | Allowed properties |
| --- | --- | --- |
| `human_too_page_view` | Page becomes available to the provider | page path, release identifier managed privately |
| `human_too_listen_click` | Verified DSP link click | service name only |
| `human_too_resource_click` | Verified resource link click | resource label only |
| `human_too_ghostheart_continue` | GhostHeart internal navigation click | destination section only |

Do not send visitor-entered text, personal stories, health information, or other sensitive information.

## Accessibility Requirements

- Use semantic heading order and landmarks.
- Preserve the visible skip link and keyboard-visible focus styles.
- Do not embed essential text in imagery.
- Keep listening destinations non-interactive until a verified URL exists.
- Preserve responsive layouts and reduced-motion behavior supplied by the shared stylesheet.

## Safety and Content Boundary

The page may discuss addiction, judgment, pain, dignity, and support. It must not diagnose, promise recovery, present love as treatment, or publish unverified support organizations, helplines, or streaming destinations.

## Rollback Procedure

1. Revert the commit that introduced or changed this page on the recovery branch through a new revert commit.
2. Run the website checks to confirm the previous site still validates.
3. Do not force-push, rewrite history, or change production settings as part of a rollback.
