-- GhostHeart Studios: "Pick the Door" Sunday Live vote (Lives page).
-- Run once in Supabase > GHOSTHEART STUDIOS > SQL Editor. Safe to run again.
--
-- What it does:
--   * A private schema ghostheart_votes that the public API cannot see.
--   * door_polls: one row per vote (id, closing time). door_votes: one row per tap.
--   * Two functions the website may call:
--       public.door_vote_totals(p_poll)                    -> counts only, never who voted
--       public.cast_door_vote(p_poll, p_pick, p_voter)     -> saves one vote, returns counts
--     "p_voter" is a random id the visitor's browser makes. It is not a name or email.
--     One vote per browser per poll; changing your mind replaces your old vote.
--   * A flood guard: at most 600 votes per hour across the whole site.
--
-- Nothing here collects emails, charges anyone or sends anything.

create schema if not exists ghostheart_votes;
revoke all on schema ghostheart_votes from public, anon, authenticated;

create table if not exists ghostheart_votes.door_polls (
  id         text primary key check (id ~ '^[a-z0-9-]{3,60}$'),
  closes_at  timestamptz not null
);
create table if not exists ghostheart_votes.door_votes (
  poll       text not null references ghostheart_votes.door_polls(id) on delete cascade,
  voter      text not null check (voter ~ '^[a-z0-9-]{16,64}$'),
  pick       text not null check (pick in ('a', 'b')),
  voted_at   timestamptz not null default now(),
  primary key (poll, voter)
);
alter table ghostheart_votes.door_polls enable row level security;
alter table ghostheart_votes.door_votes enable row level security;
revoke all on ghostheart_votes.door_polls, ghostheart_votes.door_votes from public, anon, authenticated;
create index if not exists door_votes_time on ghostheart_votes.door_votes (voted_at desc);

-- The first vote: which door the Sunday, November 22, 2026 Live goes through.
-- Closes Saturday night, November 21, at midnight Central.
insert into ghostheart_votes.door_polls (id, closes_at)
values ('sunday-2026-11-22', '2026-11-22T06:00:00Z')
on conflict (id) do update set closes_at = excluded.closes_at;

create or replace function public.door_vote_totals(p_poll text)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select jsonb_build_object(
    'a', count(*) filter (where v.pick = 'a'),
    'b', count(*) filter (where v.pick = 'b'),
    'open', coalesce((select now() < p.closes_at from ghostheart_votes.door_polls p where p.id = p_poll), false),
    'closes_at', (select p.closes_at from ghostheart_votes.door_polls p where p.id = p_poll)
  )
  from ghostheart_votes.door_votes v
  where v.poll = p_poll;
$$;

create or replace function public.cast_door_vote(p_poll text, p_pick text, p_voter text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  recent integer;
  is_open boolean;
begin
  select now() < p.closes_at into is_open from ghostheart_votes.door_polls p where p.id = p_poll;
  if is_open is null then
    raise exception 'no such vote' using errcode = '22023';
  end if;
  if not is_open then
    raise exception 'voting closed' using errcode = '22023';
  end if;
  select count(*) into recent from ghostheart_votes.door_votes where voted_at > now() - interval '1 hour';
  if recent >= 600 then
    raise exception 'busy, try again later' using errcode = '53400';
  end if;
  insert into ghostheart_votes.door_votes (poll, voter, pick)
  values (p_poll, lower(p_voter), p_pick)
  on conflict on constraint door_votes_pkey do update set pick = excluded.pick, voted_at = now();
  return public.door_vote_totals(p_poll);
exception
  when check_violation or not_null_violation or foreign_key_violation then
    raise exception 'invalid vote' using errcode = '22023';
end;
$$;

revoke all on function public.door_vote_totals(text) from public, authenticated;
revoke all on function public.cast_door_vote(text, text, text) from public, authenticated;
grant execute on function public.door_vote_totals(text) to anon;
grant execute on function public.cast_door_vote(text, text, text) to anon;

-- Check: "anon can vote" and "anon can count" true, "anon can read votes" false.
select has_function_privilege('anon', 'public.cast_door_vote(text, text, text)', 'execute') as "anon can vote",
       has_function_privilege('anon', 'public.door_vote_totals(text)', 'execute') as "anon can count",
       has_table_privilege('anon', 'ghostheart_votes.door_votes', 'select') as "anon can read votes (must be false)";

-- To see results yourself: select pick, count(*) from ghostheart_votes.door_votes where poll = 'sunday-2026-11-22' group by pick;
-- To turn it off: drop function public.cast_door_vote(text, text, text); (the page then shows "Voting opens soon").
