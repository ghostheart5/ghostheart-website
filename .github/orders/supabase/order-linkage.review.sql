-- GhostHeart Studios: link each order to where it came from and to what Stripe was paid (November 11, 2026).
-- Run once in Supabase > GHOSTHEART STUDIOS > SQL Editor, AFTER story-orders.review.sql and
-- verified-payment.review.sql. Safe to run again. Until it is run, the website and the webhook keep working
-- exactly as before: the extra details are simply not saved.
--
-- What it does:
--   * Adds "where it came from" columns to ghostheart_orders.story_orders: source, medium, campaign, content
--     (the utm tags on the link the visitor followed), referrer_host (the site that linked here) and
--     landing_path (the page they arrived on). No name, email or story is in them.
--   * Adds "what was paid" columns: amount_cents, currency and payment_link_id, filled by the Stripe webhook.
--   * public.submit_ghostheart_order(payload jsonb): the same function as before, now also saving
--     payload.source when the website sends it. Everything else is unchanged.
--   * public.ghostheart_mark_order_paid(order_id, session_id, amount_cents, currency, payment_link): the same
--     one-time "mark paid" as before, also recording the amount. Used only by the stripe-webhook function.
--     The older two-value version stays, so an older copy of the webhook still works.
--
-- Nothing in this file charges anyone or sends any email. The website key still cannot read any order.

alter table ghostheart_orders.story_orders add column if not exists source text check (char_length(source) <= 80);
alter table ghostheart_orders.story_orders add column if not exists medium text check (char_length(medium) <= 80);
alter table ghostheart_orders.story_orders add column if not exists campaign text check (char_length(campaign) <= 120);
alter table ghostheart_orders.story_orders add column if not exists content text check (char_length(content) <= 120);
alter table ghostheart_orders.story_orders add column if not exists referrer_host text check (char_length(referrer_host) <= 120);
alter table ghostheart_orders.story_orders add column if not exists landing_path text check (char_length(landing_path) <= 200);
alter table ghostheart_orders.story_orders add column if not exists amount_cents integer check (amount_cents between 0 and 10000000);
alter table ghostheart_orders.story_orders add column if not exists currency text check (currency ~ '^[a-z]{3}$');
alter table ghostheart_orders.story_orders add column if not exists payment_link_id text check (char_length(payment_link_id) <= 80);

create or replace function public.submit_ghostheart_order(payload jsonb)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  clean   jsonb := coalesce(payload, '{}'::jsonb);
  src     jsonb;
  new_id  uuid;
  recent  integer;
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
  -- Where the visitor came from. Optional; anything that is not a plain object is ignored, and every value is
  -- cut to plain letters, digits and a few marks so nothing odd can be stored.
  src := case when jsonb_typeof(clean->'source') = 'object' then clean->'source' else '{}'::jsonb end;
  insert into ghostheart_orders.story_orders (kind, email, for_whom, occasion, memories, names, mood, length, service, details,
                                              source, medium, campaign, content, referrer_host, landing_path)
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
    nullif(btrim(clean->>'details'), ''),
    nullif(left(btrim(regexp_replace(coalesce(src->>'source', ''), '[^A-Za-z0-9 ._:/+-]', '', 'g')), 80), ''),
    nullif(left(btrim(regexp_replace(coalesce(src->>'medium', ''), '[^A-Za-z0-9 ._:/+-]', '', 'g')), 80), ''),
    nullif(left(btrim(regexp_replace(coalesce(src->>'campaign', ''), '[^A-Za-z0-9 ._:/+-]', '', 'g')), 120), ''),
    nullif(left(btrim(regexp_replace(coalesce(src->>'content', ''), '[^A-Za-z0-9 ._:/+-]', '', 'g')), 120), ''),
    nullif(left(btrim(regexp_replace(coalesce(src->>'referrer', ''), '[^A-Za-z0-9._-]', '', 'g')), 120), ''),
    nullif(left(btrim(regexp_replace(coalesce(src->>'landing', ''), '[^A-Za-z0-9 ._:/+-]', '', 'g')), 200), '')
  )
  returning id into new_id;
  return new_id;
exception
  when check_violation or not_null_violation then
    raise exception 'invalid order' using errcode = '22023';
end;
$$;
revoke all on function public.submit_ghostheart_order(jsonb) from public, authenticated;
grant execute on function public.submit_ghostheart_order(jsonb) to anon;

-- Called by the stripe-webhook Edge Function only (service_role), after it has checked Stripe's signature.
-- Same answers as the two-value version: 'marked', 'already' or 'skipped'.
create or replace function public.ghostheart_mark_order_paid(order_id uuid, session_id text, amount_cents integer, currency text, payment_link text)
returns text
language plpgsql
security definer
set search_path = ''
as $$
declare
  cur text := lower(coalesce(currency, ''));
begin
  if order_id is null or session_id is null
     or char_length(session_id) not between 4 and 255 or session_id !~ '^cs_[A-Za-z0-9_]+$' then
    return 'skipped';
  end if;
  update ghostheart_orders.story_orders o
     set status = 'paid', paid_at = now(), stripe_session_id = session_id,
         amount_cents = case when ghostheart_mark_order_paid.amount_cents between 0 and 10000000 then ghostheart_mark_order_paid.amount_cents end,
         currency = case when cur ~ '^[a-z]{3}$' then cur end,
         payment_link_id = case when payment_link ~ '^plink_[A-Za-z0-9]{1,70}$' then payment_link end
   where o.id = ghostheart_mark_order_paid.order_id
     and o.kind = 'song'
     and o.status = 'new'
     and o.paid_at is null;
  if found then
    return 'marked';
  end if;
  if exists (select 1 from ghostheart_orders.story_orders o
              where o.id = ghostheart_mark_order_paid.order_id
                and o.stripe_session_id = ghostheart_mark_order_paid.session_id) then
    return 'already';
  end if;
  return 'skipped';
exception
  -- The same Stripe session can never mark a second order.
  when unique_violation then
    return 'skipped';
end;
$$;
revoke all on function public.ghostheart_mark_order_paid(uuid, text, integer, text, text) from public, anon, authenticated;
grant execute on function public.ghostheart_mark_order_paid(uuid, text, integer, text, text) to service_role;

-- Check: should return one row with
--   anon can save an order = true, anon can mark paid = false, service can mark paid = true,
--   anon can read orders = false, linkage columns = 9.
select has_function_privilege('anon', 'public.submit_ghostheart_order(jsonb)', 'execute') as "anon can save an order",
       has_function_privilege('anon', 'public.ghostheart_mark_order_paid(uuid, text, integer, text, text)', 'execute') as "anon can mark paid (must be false)",
       has_function_privilege('service_role', 'public.ghostheart_mark_order_paid(uuid, text, integer, text, text)', 'execute') as "service can mark paid",
       has_table_privilege('anon', 'ghostheart_orders.story_orders', 'select') as "anon can read orders (must be false)",
       (select count(*) from information_schema.columns
         where table_schema = 'ghostheart_orders' and table_name = 'story_orders'
           and column_name in ('source', 'medium', 'campaign', 'content', 'referrer_host', 'landing_path', 'amount_cents', 'currency', 'payment_link_id')) as "linkage columns (must be 9)";
