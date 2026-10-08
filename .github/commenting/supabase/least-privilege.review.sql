-- Creates three NOLOGIN/NOINHERIT roles without any persistent credentials.
-- Only a later, separately reviewed auth route may assume them.
-- The function role must never be postgres, service_role, or BYPASSRLS.
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'ghostheart_blog_api') then
    create role ghostheart_blog_api nologin noinherit;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'ghostheart_blog_moderator') then
    create role ghostheart_blog_moderator nologin noinherit;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'ghostheart_blog_retention') then
    create role ghostheart_blog_retention nologin noinherit;
  end if;
end;
$$;

grant usage on schema ghostheart_blog to ghostheart_blog_api,
  ghostheart_blog_moderator, ghostheart_blog_retention;

grant select (thread, display_name, body, approved_at, status)
  on ghostheart_blog.comments to ghostheart_blog_api;
grant insert (thread, display_name, body, status)
  on ghostheart_blog.comments to ghostheart_blog_api;
grant usage on sequence ghostheart_blog.comments_id_seq to ghostheart_blog_api;
drop policy if exists blog_api_read_approved on ghostheart_blog.comments;
create policy blog_api_read_approved on ghostheart_blog.comments
  for select to ghostheart_blog_api using (status = 'approved');
drop policy if exists blog_api_submit_pending on ghostheart_blog.comments;
create policy blog_api_submit_pending on ghostheart_blog.comments
  for insert to ghostheart_blog_api with check (status = 'pending' and approved_at is null);

grant select (marker, attempted_at), insert (marker)
  on ghostheart_blog.attempts to ghostheart_blog_api;
drop policy if exists blog_api_read_attempts on ghostheart_blog.attempts;
create policy blog_api_read_attempts on ghostheart_blog.attempts
  for select to ghostheart_blog_api using (true);
drop policy if exists blog_api_insert_attempts on ghostheart_blog.attempts;
create policy blog_api_insert_attempts on ghostheart_blog.attempts
  for insert to ghostheart_blog_api with check (true);
grant select (singleton, last_run_at) on ghostheart_blog.retention_state
  to ghostheart_blog_api;
drop policy if exists blog_api_read_retention_state on ghostheart_blog.retention_state;
create policy blog_api_read_retention_state on ghostheart_blog.retention_state
  for select to ghostheart_blog_api using (singleton);

grant select on ghostheart_blog.comments to ghostheart_blog_moderator;
grant update (status, approved_at) on ghostheart_blog.comments
  to ghostheart_blog_moderator;
grant insert (comment_id, actor_role, previous_status, next_status)
  on ghostheart_blog.moderation_events to ghostheart_blog_moderator;
grant usage on sequence ghostheart_blog.moderation_events_id_seq
  to ghostheart_blog_moderator;
drop policy if exists blog_moderator_read on ghostheart_blog.comments;
create policy blog_moderator_read on ghostheart_blog.comments
  for select to ghostheart_blog_moderator using (true);
drop policy if exists blog_moderator_decide on ghostheart_blog.comments;
create policy blog_moderator_decide on ghostheart_blog.comments
  for update to ghostheart_blog_moderator
  using (status = 'pending')
  with check (status in ('approved', 'rejected'));
drop policy if exists blog_moderator_audit_insert on ghostheart_blog.moderation_events;
create policy blog_moderator_audit_insert on ghostheart_blog.moderation_events
  for insert to ghostheart_blog_moderator
  with check (
    actor_role = current_user and previous_status = 'pending' and
    exists (select 1 from ghostheart_blog.comments c
            where c.id = comment_id and c.status = next_status)
  );

grant delete, select on ghostheart_blog.attempts,
  ghostheart_blog.comments, ghostheart_blog.moderation_events
  to ghostheart_blog_retention;
grant select, update (last_run_at) on ghostheart_blog.retention_state
  to ghostheart_blog_retention;
drop policy if exists blog_retention_read_state on ghostheart_blog.retention_state;
create policy blog_retention_read_state on ghostheart_blog.retention_state
  for select to ghostheart_blog_retention using (singleton);
drop policy if exists blog_retention_update_state on ghostheart_blog.retention_state;
create policy blog_retention_update_state on ghostheart_blog.retention_state
  for update to ghostheart_blog_retention
  using (singleton) with check (singleton);
drop policy if exists blog_retention_read_comments on ghostheart_blog.comments;
create policy blog_retention_read_comments on ghostheart_blog.comments
  for select to ghostheart_blog_retention using (true);
drop policy if exists blog_retention_delete_comments on ghostheart_blog.comments;
create policy blog_retention_delete_comments on ghostheart_blog.comments
  for delete to ghostheart_blog_retention using (status in ('pending','rejected'));
drop policy if exists blog_retention_read_attempts on ghostheart_blog.attempts;
create policy blog_retention_read_attempts on ghostheart_blog.attempts
  for select to ghostheart_blog_retention using (true);
drop policy if exists blog_retention_delete_attempts on ghostheart_blog.attempts;
create policy blog_retention_delete_attempts on ghostheart_blog.attempts
  for delete to ghostheart_blog_retention using (true);
drop policy if exists blog_retention_read_events on ghostheart_blog.moderation_events;
create policy blog_retention_read_events on ghostheart_blog.moderation_events
  for select to ghostheart_blog_retention using (true);
drop policy if exists blog_retention_delete_events on ghostheart_blog.moderation_events;
create policy blog_retention_delete_events on ghostheart_blog.moderation_events
  for delete to ghostheart_blog_retention using (true);

-- Manual owner-only approval: connect as ghostheart_blog_moderator, review
-- pending text, then update exactly one selected ID. The trigger writes audit.
-- update ghostheart_blog.comments
-- set status = 'approved', approved_at = now()
-- where id = :reviewed_id and status = 'pending'
-- returning id, status, approved_at;
