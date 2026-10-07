# GhostHeart blog comments readiness

This is a review draft. The production site keeps comments closed until the
GhostHeart Studios backend has been configured and tested end to end. The
database project is `pgqaqqliefpofsktjhjq`. No Axiomara database is involved.

## Approval gate

Obtain owner approval to create one persistent PostgreSQL LOGIN role named
`ghostheart_comments_api` in GhostHeart Studios. Give it only USAGE on the
private `ghostheart_blog` schema and SELECT of approved comments plus INSERT of
pending comments on `ghostheart_blog.comments`. It receives no permissions on
any `studio_*` table, no UPDATE/DELETE, and no schema creation privileges.
Create a strong generated password, store its pooler connection URL in the
Supabase Edge Function secret `GHOSTHEART_COMMENTS_DB_URL`, and never put either
value in this repository, public JavaScript, or chat output.

After approval, create the role and password through a secure administrator
session, review and apply `schema-proposal.sql` to this project, deploy the
`blog-comments` Edge Function with public invocation (`verify_jwt = false`),
and add the secret. The function accepts only the public website Origin and a
fixed list of existing blog posts, validates lengths, and returns only approved
comments. Browser output uses `textContent`. New comments default to `pending`
and require a project administrator to mark them approved in Supabase.

Before publishing the website form, test an anonymous submission, confirm it
does not appear publicly, approve it in Supabase, confirm it then appears only
on its own post, and confirm the restricted role cannot read pending comments
or touch any `studio_*` table. Verify CORS and the production page after deploy.
The public site remains unchanged until those checks pass.
