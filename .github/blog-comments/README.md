# GhostHeart blog comments reconciliation

**Draft PR only. Keep deployment on hold.** GhostHeart Studios project
`pgqaqqliefpofsktjhjq` already contains a private `ghostheart_blog` schema,
with `comments`, `attempts`, `moderation_events`, and `retention_state` tables.
The existing NOLOGIN roles are `ghostheart_blog_api`,
`ghostheart_blog_moderator`, and `ghostheart_blog_retention`. This PR proposes no
parallel table or API role, and touches no Axiomara data.

The existing comments table uses a `thread` such as
`journal:this-is-ghostheart`, bigint ID, `display_name` of 2–60 characters,
`body` of 10–1000 characters, `consent_at`, `status`, and `approved_at`.
Submitted comments default to pending; only approved rows can be returned.
The form requires explicit consent before submission and renders returned text
with `textContent`.

## Restricted login handoff

The owner approved one persistent login named `ghostheart_comments_api` for
inserting pending comments and reading approved comments. A secure owner-entry
step must generate its password and place its pooler URL in the Supabase Edge
Function secret `GHOSTHEART_COMMENTS_DB_URL`. Never enter the password or URL in
Git, chat, shell commands, SQL tool arguments, or agent-visible output.
`access-proposal.sql` shows the minimal table/column and sequence privileges
plus RLS policies that login would need. Review them against the existing
Studio work before applying. Do **not** grant membership in
`ghostheart_blog_api`: that role also accesses `attempts` and
`retention_state`, beyond this approval.

The draft function does not yet enforce durable submission rate limits. The
existing `attempts` table could support that with narrowly scoped SELECT and
INSERT on `attempts` (and a non-public marker secret), but this is additional
persistent access and requires a separate approval and implementation. Keep
public posting closed until abuse controls and the moderation workflow are
resolved, then deploy the function and run end-to-end tests: pending submission
is hidden, approval makes it visible only on the correct post, rejected content
stays hidden, and the restricted login cannot access any `studio_*` table.
