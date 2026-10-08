-- REVIEW DRAFT. Never run against GhostHeart Studio until the owner approves
-- storage, the database role, security grants, retention, and moderation access.
-- Keep this schema outside the Supabase Data API exposed schemas.
create schema if not exists ghostheart_blog;
revoke all on schema ghostheart_blog from public, anon, authenticated;

create table if not exists ghostheart_blog.comments (
  id bigint generated always as identity primary key,
  thread text not null check (thread in (
    'journal:how-we-got-here', 'journal:this-is-ghostheart',
    'journal:ghosthearts-oath', 'journal:youre-not-god')),
  display_name text not null check (char_length(display_name) between 2 and 60),
  body text not null check (char_length(body) between 10 and 1000),
  consent_at timestamptz not null default now(),
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  created_at timestamptz not null default now(),
  approved_at timestamptz,
  check ((status = 'approved') = (approved_at is not null))
);
create index if not exists blog_comments_public on ghostheart_blog.comments (thread, approved_at)
  where status = 'approved';
create index if not exists blog_comments_queue on ghostheart_blog.comments (created_at)
  where status = 'pending';

create table if not exists ghostheart_blog.attempts (
  marker text not null check (marker ~ '^[0-9a-f]{64}$'),
  attempted_at timestamptz not null default now()
);
create index if not exists blog_attempts_rate on ghostheart_blog.attempts (marker, attempted_at);

-- Records decisions without copying visitor comment text into the audit trail.
-- The moderator role is not yet created or granted access by this draft.
create table if not exists ghostheart_blog.moderation_events (
  id bigint generated always as identity primary key,
  comment_id bigint not null unique,
  actor_role text not null,
  previous_status text not null check (previous_status = 'pending'),
  next_status text not null check (next_status in ('approved', 'rejected')),
  decided_at timestamptz not null default now()
);
create index if not exists blog_moderation_events_time on ghostheart_blog.moderation_events (decided_at);

-- New submissions stay closed unless bounded retention ran recently.
create table if not exists ghostheart_blog.retention_state (
  singleton boolean primary key default true check (singleton),
  last_run_at timestamptz
);
insert into ghostheart_blog.retention_state (singleton) values (true)
  on conflict (singleton) do nothing;

create or replace function ghostheart_blog.audit_moderation() returns trigger
language plpgsql
set search_path = pg_catalog, ghostheart_blog
as $$
begin
  if old.status = new.status then return new; end if;
  if old.status <> 'pending' or new.status not in ('approved', 'rejected') then
    raise exception 'Only pending comments can be moderated';
  end if;
  insert into ghostheart_blog.moderation_events
    (comment_id, actor_role, previous_status, next_status)
    values (new.id, current_user, old.status, new.status);
  return new;
end;
$$;
revoke all on function ghostheart_blog.audit_moderation() from public, anon, authenticated;
create or replace function ghostheart_blog.prepare_moderation() returns trigger
language plpgsql
set search_path = pg_catalog, ghostheart_blog
as $$
begin
  if old.status = new.status then return new; end if;
  if old.status <> 'pending' or new.status not in ('approved', 'rejected') then
    raise exception 'Only pending comments can be moderated';
  end if;
  new.approved_at := case when new.status = 'approved' then now() else null end;
  return new;
end;
$$;
revoke all on function ghostheart_blog.prepare_moderation() from public, anon, authenticated;
drop trigger if exists prepare_blog_moderation on ghostheart_blog.comments;
create trigger prepare_blog_moderation
before update of status on ghostheart_blog.comments
for each row execute function ghostheart_blog.prepare_moderation();
drop trigger if exists audit_blog_moderation on ghostheart_blog.comments;
create trigger audit_blog_moderation
after update of status on ghostheart_blog.comments
for each row execute function ghostheart_blog.audit_moderation();

alter table ghostheart_blog.comments enable row level security;
alter table ghostheart_blog.attempts enable row level security;
alter table ghostheart_blog.moderation_events enable row level security;
alter table ghostheart_blog.retention_state enable row level security;
revoke all on all tables in schema ghostheart_blog from public, anon, authenticated;
revoke all on all sequences in schema ghostheart_blog from public, anon, authenticated;

-- Intentionally no role creation, grants, or RLS policies in this draft.
-- See least-privilege.review.sql for the precise proposed role boundary.
-- No production SQL has been applied.
