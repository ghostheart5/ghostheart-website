# GhostHeart blog comments setup

**Draft PR only. Keep deployment on hold.** GhostHeart Studios project
`pgqaqqliefpofsktjhjq` already has the private `ghostheart_blog` schema and its
moderation flow. This PR adds no parallel table or service and touches no
Axiomara data.

Supabase migration `20261008000357_prepare_restricted_ghostheart_comments_login`
created the specifically approved `ghostheart_comments_api` role as **NOLOGIN**.
It has only blog comment and attempt column privileges, comment sequence usage,
and RLS policies. It cannot read `studio_members` or `retention_state`, and has
no `studio_*`, moderator, UPDATE, or DELETE privileges. The applied SQL is in
`access-applied.sql`. No password or connection secret has been created here.

The existing comments table uses `thread`, bigint ID, `display_name` of 2–60
characters, `body` of 10–1000 characters, `consent_at`, `status`, and
`approved_at`. The form requires explicit consent. Submissions are pending by
default; only approved rows can be returned. The page renders text with
`textContent`.

## Secure owner-entry handoff

1. The owner generates a long unique password in a password manager. In the GhostHeart Studios [Supabase SQL Editor](https://supabase.com/dashboard/project/pgqaqqliefpofsktjhjq/sql), the owner personally runs `ALTER ROLE ghostheart_comments_api WITH LOGIN PASSWORD '<password from your manager>';`. Do not send the password to the assistant or place it in Git or chat. This SQL may remain in editor history; if the owner has a local PostgreSQL client, `\password ghostheart_comments_api` in `psql` followed by `ALTER ROLE ghostheart_comments_api LOGIN;` avoids putting the password literal in SQL history. Supabase's [Postgres Roles guide](https://supabase.com/docs/guides/database/postgres/roles) documents password-login roles.
2. In the project's **Connect** panel, the owner selects the transaction pooler connection method for serverless functions and builds a connection URL using the restricted role. Percent-encode special password characters. [Supabase connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres) identifies transaction pooling as the edge-function option.
3. In [Edge Function Secrets](https://supabase.com/dashboard/project/pgqaqqliefpofsktjhjq/functions/secrets), the owner enters the restricted URL as `GHOSTHEART_COMMENTS_DB_URL` and a separate random 32-character-or-longer marker secret as `GHOSTHEART_COMMENT_MARKER_KEY`. These values belong only in provider-managed secrets. [Supabase secret guide](https://supabase.com/docs/guides/functions/secrets) documents this screen.
4. Tell the assistant only that both secrets have been entered, never their values. The assistant can then deploy and test the function without reading them.

The draft function hashes the last proxy-added IP address with HMAC before
storing a marker in `ghostheart_blog.attempts`. It serializes submissions per
marker and permits at most five per hour. Before opening comments, verify in a
staged live call that Supabase's gateway reliably appends or overwrites
`x-forwarded-for`; otherwise the rate limit could be evaded or fail closed.
Also test submission, 429 after five attempts, pending invisibility, manual
approval and rejection, post isolation, and the restricted login's denial on
all unrelated Studio tables. Keep public posting closed until these pass.
