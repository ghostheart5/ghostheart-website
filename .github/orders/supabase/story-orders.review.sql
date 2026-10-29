-- GhostHeart Studios: "I'm here to help" order intake (owner decision OWNER-BLUEPRINT-20261028).
-- Run once in Supabase > GHOSTHEART STUDIOS > SQL Editor. Safe to run again.
--
-- What it does:
--   * A private schema ghostheart_orders that the public API cannot see.
--   * One table of story and help requests. Row-level security on, no public policies:
--     nobody can read orders through the website key.
--   * One function the website may call, public.submit_ghostheart_order(payload jsonb).
--     It checks every field, refuses oversized text, rate-limits, and returns only a new order id.
--   * A NOLOGIN reader role (ghostheart_orders_reader) for Work HQ's morning brief later.
--     It is granted to no login here.
--
-- Nothing in this file charges anyone or sends any email.

create schema if not exists ghostheart_orders;
revoke all on schema ghostheart_orders from public, anon, authenticated;

create table if not exists ghostheart_orders.story_orders (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  kind        text not null check (kind in ('song', 'office')),
  status      text not null default 'new' check (status in ('new', 'paid', 'in_progress', 'delivered', 'cancelled')),
  email       text not null check (char_length(email) between 6 and 254 and email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  for_whom    text check (char_length(for_whom) <= 200),
  occasion    text check (char_length(occasion) <= 200),
  memories    text check (char_length(memories) <= 4000),
  names       text check (char_length(names) <= 500),
  mood        text check (char_length(mood) <= 200),
  length      text check (length in ('full', 'short')),
  service     text check (service in ('data_entry', 'word', 'resume', 'powerpoint', 'excel', 'writing', 'proofreading')),
  details     text check (char_length(details) <= 4000),
  constraint song_has_story check (kind <> 'song' or (for_whom is not null and memories is not null and length is not null)),
  constraint office_has_request check (kind <> 'office' or (service is not null and details is not null))
);
alter table ghostheart_orders.story_orders enable row level security;
revoke all on ghostheart_orders.story_orders from public, anon, authenticated;
create index if not exists story_orders_created on ghostheart_orders.story_orders (created_at desc);

create or replace function public.submit_ghostheart_order(payload jsonb)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  clean   jsonb := coalesce(payload, '{}'::jsonb);
  new_id  uuid;
  recent  integer;
  t       text;
begin
  if jsonb_typeof(clean) <> 'object' or pg_column_size(clean) > 16000 then
    raise exception 'invalid order' using errcode = '22023';
  end if;
  -- Honeypot: the website leaves this empty; simple bots fill it.
  if coalesce(clean->>'website', '') <> '' then
    raise exception 'invalid order' using errcode = '22023';
  end if;
  -- Flood guard across the whole form: at most 30 new requests per hour.
  select count(*) into recent from ghostheart_orders.story_orders where created_at > now() - interval '1 hour';
  if recent >= 30 then
    raise exception 'busy, try again later' using errcode = '53400';
  end if;
  insert into ghostheart_orders.story_orders (kind, email, for_whom, occasion, memories, names, mood, length, service, details)
  values (
    clean->>'kind',
    lower(btrim(clean->>'email')),
    nullif(btrim(clean->>'for_whom'), ''),
    nullif(btrim(clean->>'occasion'), ''),
    nullif(btrim(clean->>'memories'), ''),
    nullif(btrim(clean->>'names'), ''),
    nullif(btrim(clean->>'mood'), ''),
    nullif(clean->>'length', ''),
    nullif(clean->>'service', ''),
    nullif(btrim(clean->>'details'), '')
  )
  returning id into new_id;
  return new_id;
exception
  when check_violation or not_null_violation then
    raise exception 'invalid order' using errcode = '22023';
end;
$$;
revoke all on function public.submit_ghostheart_order(jsonb) from public;
grant execute on function public.submit_ghostheart_order(jsonb) to anon;

-- Reader role for Work HQ (morning brief). NOLOGIN; connect it later in a separate, reviewed step.
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'ghostheart_orders_reader') then
    create role ghostheart_orders_reader nologin noinherit;
  end if;
end;
$$;
grant usage on schema ghostheart_orders to ghostheart_orders_reader;
grant select on ghostheart_orders.story_orders to ghostheart_orders_reader;
grant update (status) on ghostheart_orders.story_orders to ghostheart_orders_reader;
drop policy if exists orders_reader_all on ghostheart_orders.story_orders;
create policy orders_reader_all on ghostheart_orders.story_orders
  for all to ghostheart_orders_reader using (true) with check (true);

-- Check: should return one row, "submit_ghostheart_order | anon can execute: true".
select 'submit_ghostheart_order' as fn,
       has_function_privilege('anon', 'public.submit_ghostheart_order(jsonb)', 'execute') as "anon can execute",
       has_table_privilege('anon', 'ghostheart_orders.story_orders', 'select') as "anon can read orders (must be false)";
