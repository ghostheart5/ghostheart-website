# Awakening campaign content

`awakening.json` is the working eight-section manifest derived from the owner's
October 1, 2026 handoff and DOCX. The referenced original
`Awakening_Campaign_Manifest.json` and Markdown campaign master were not supplied
or located. This file does not claim to be either original.

The static site already uses JSON under `.github/content/` and Python builders
under `.github/scripts/`. Campaign output follows those conventions. No new
router, dependency, service, branch, or publishing automation was introduced.

Run `python .github/scripts/build_awakening.py` to build the public candidate,
and append `--check` to verify it without writing. Draft source bodies are not
stored in this manifest. The current public candidate contains the landing and
the legacy story gateway only; all eight article routes remain unpublished.

For a private preview, supply `--preview-dir <directory-outside-repository>` and
`--sources <private-source-map.json>`. The source map maps `cruel` and `wife` to
their existing absolute paths and SHA-256 hashes. HQ holds that local map and
the preview, outside the website checkout. Do not copy these into the website.
The builder reads original files and verifies hashes; it does not rewrite them.
Headings and the internal-status paragraph are rendered as page metadata; body
paragraph wording is preserved and HTML-escaped.

Approval is explicit: `status: approved`, `ready: true`, a nonempty `approval`
record, and the exact approved `source_sha256` are required. Only the contiguous
approved opening is eligible; section four cannot jump ahead of Cruel. A stale
article at a non-approved route causes a build failure, never silent deletion.
Approval and a successful local build do not deploy anything.

The preserved legacy Markdown remains at its existing `story/` source path.
Both existing Pages artifact steps now explicitly exclude that file. Publishing
the entire repository root directly bypasses that protection and is not a safe
release route. Hosting settings and the exact final artifact must be reviewed
again under separate deployment authorization. No workflow was run or enabled.

The existing signup action, EMAIL field and honeypot are reused. Local tests
prevent submission and block outbound requests: Mailchimp acceptance, actual
double opt-in, inbox delivery and future campaign sends remain unverified.

Aggregate measurement uses the existing domain-gated Metricool loader and the
campaign routes. No new tracking service, event payloads, subscriber identifiers,
reading-completion claims, or automatic campaigns were added. Local previews
do not load the tracker; production collection is not proven by local checks.

Media fields stay null until exact sources and reuse approval are verified.
There is no player, replay, schedule, Sunday destination or guessed music URL.
The Sunday notice is exactly `Sunday readings — details coming soon.`

Run `python .github/scripts/test_awakening.py` for the offline boundary checks.
Current HQ evidence and full implementation report:
`07_WEBSITE_AUDIENCE_CHANNELS/evidence/2026-10-01-awakening/`.
