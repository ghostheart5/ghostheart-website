-- Applied to GhostHeart Studios pgqaqqliefpofsktjhjq by Supabase migration
-- 20261008000357_prepare_restricted_ghostheart_comments_login.
-- No password was created or transmitted. The role remains NOLOGIN until
-- the owner enters a password through a secure provider-facing step.

create role ghostheart_comments_api
  nologin noinherit nosuperuser nocreatedb nocreaterole noreplication nobypassrls;

grant usage on schema ghostheart_blog to ghostheart_comments_api;
grant select (id, thread, display_name, body, approved_at, status),
  insert (thread, display_name, body)
  on ghostheart_blog.comments to ghostheart_comments_api;
grant usage on sequence ghostheart_blog.comments_id_seq
  to ghostheart_comments_api;
grant select (marker, attempted_at), insert (marker)
  on ghostheart_blog.attempts to ghostheart_comments_api;

create policy blog_comments_login_read_approved on ghostheart_blog.comments
  for select to ghostheart_comments_api using (status = 'approved');
create policy blog_comments_login_submit_pending on ghostheart_blog.comments
  for insert to ghostheart_comments_api
  with check (status = 'pending' and approved_at is null);
create policy blog_attempts_login_read on ghostheart_blog.attempts
  for select to ghostheart_comments_api using (true);
create policy blog_attempts_login_insert on ghostheart_blog.attempts
  for insert to ghostheart_comments_api with check (true);
