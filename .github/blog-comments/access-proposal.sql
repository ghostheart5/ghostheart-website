-- REVIEW DRAFT ONLY. Do not apply before the approved login is securely
-- created by the owner and the existing GhostHeart Studios work is reconciled.
-- Uses the existing private ghostheart_blog.comments table. No new table,
-- schema, or parallel API role is proposed.

-- The approved LOGIN role is ghostheart_comments_api. Its password is generated
-- and entered by the owner in a secure administrator interface, never in Git.
-- The function needs only these column grants and sequence usage.
grant usage on schema ghostheart_blog to ghostheart_comments_api;
grant select (id, thread, display_name, body, approved_at, status),
  insert (thread, display_name, body)
  on ghostheart_blog.comments to ghostheart_comments_api;
grant usage on sequence ghostheart_blog.comments_id_seq
  to ghostheart_comments_api;

create policy blog_comments_login_read_approved on ghostheart_blog.comments
  for select to ghostheart_comments_api
  using (status = 'approved');
create policy blog_comments_login_submit_pending on ghostheart_blog.comments
  for insert to ghostheart_comments_api
  with check (status = 'pending' and approved_at is null);

-- No attempts, retention_state, moderation, UPDATE, or DELETE grant is included.
-- Pending entries remain invisible to the public reader role.
