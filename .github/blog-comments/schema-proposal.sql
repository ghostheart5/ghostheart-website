-- REVIEW DRAFT. Do not apply until the owner approves the restricted database
-- login and its Edge Function secret for GhostHeart Studios pgqaqqliefpofsktjhjq.
-- Create the login with a generated password outside Git, then apply this SQL.
-- The login name below is the only new role this feature requires.

create schema if not exists ghostheart_blog;
revoke all on schema ghostheart_blog from public, anon, authenticated;

create table if not exists ghostheart_blog.comments (
  id uuid primary key default gen_random_uuid(),
  post_slug text not null check (post_slug in (
    'this-is-ghostheart', 'ghosthearts-oath', 'youre-not-god', 'how-we-got-here'
  )),
  display_name text not null check (char_length(display_name) between 1 and 60),
  body text not null check (char_length(body) between 1 and 2000),
  status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  created_at timestamptz not null default now()
);
create index if not exists comments_approved_post_date
  on ghostheart_blog.comments (post_slug, created_at desc)
  where status = 'approved';

revoke all on ghostheart_blog.comments from public, anon, authenticated;
alter table ghostheart_blog.comments enable row level security;
alter table ghostheart_blog.comments force row level security;

-- Run these statements only after creating the LOGIN role with a strong
-- generated password. The role has no CREATE, UPDATE, or DELETE permission.
grant usage on schema ghostheart_blog to ghostheart_comments_api;
grant select (id, post_slug, display_name, body, status, created_at),
  insert (post_slug, display_name, body)
  on ghostheart_blog.comments to ghostheart_comments_api;

create policy comments_read_approved on ghostheart_blog.comments
  for select to ghostheart_comments_api
  using (status = 'approved');
create policy comments_submit_pending on ghostheart_blog.comments
  for insert to ghostheart_comments_api
  with check (status = 'pending');

-- Moderation uses the existing project administrator in Supabase Table Editor:
-- set status to 'approved' or 'rejected'. No public update permission exists.
