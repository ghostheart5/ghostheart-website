-- GhostHeart Studios: verified payment for the $50 custom song (owner decision OWNER-BLUEPRINT-20261028).
-- Run once in Supabase > GHOSTHEART STUDIOS > SQL Editor, AFTER story-orders.review.sql. Safe to run again.
--
-- What it does:
--   * Adds two columns to ghostheart_orders.story_orders: paid_at (when Stripe confirmed the payment)
--     and stripe_session_id (the Stripe Checkout Session id, unique, so one payment marks one order).
--   * public.ghostheart_mark_order_paid(order_id uuid, session_id text): used ONLY by the stripe-webhook
--     Edge Function with the service_role key, after it has checked Stripe's signature. It moves a song
--     order from 'new' to 'paid' once; repeats of the same Stripe event change nothing.
--   * public.ghostheart_order_paid(order_id uuid): the website may call this (anon key). It answers only
--     true or false: has Stripe confirmed payment for this order id? It reveals nothing else. Order ids
--     are random uuids, so nobody can guess someone else's.
--
-- Nothing in this file charges anyone or sends any email. The website key still cannot read any order.

alter table ghostheart_orders.story_orders add column if not exists paid_at timestamptz;
alter table ghostheart_orders.story_orders add column if not exists stripe_session_id text;
create unique index if not exists story_orders_stripe_session
  on ghostheart_orders.story_orders (stripe_session_id);

-- Called by the stripe-webhook Edge Function only (service_role). Returns what happened:
--   'marked'  : the order was 'new' and is now 'paid'.
--   'already' : this same Stripe session already marked this order (a repeated webhook). Nothing changed.
--   'skipped' : no such song order, or it is no longer 'new' (owner moved it on), or the session id is odd.
create or replace function public.ghostheart_mark_order_paid(order_id uuid, session_id text)
returns text
language plpgsql
security definer
set search_path = ''
as $$
begin
  if order_id is null or session_id is null
     or char_length(session_id) not between 4 and 255 or session_id !~ '^cs_[A-Za-z0-9_]+$' then
    return 'skipped';
  end if;
  update ghostheart_orders.story_orders o
     set status = 'paid', paid_at = now(), stripe_session_id = session_id
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
revoke all on function public.ghostheart_mark_order_paid(uuid, text) from public, anon, authenticated;
grant execute on function public.ghostheart_mark_order_paid(uuid, text) to service_role;

-- Called by the website after Stripe sends the customer back. Only true or false, nothing else.
-- True only once the webhook has recorded Stripe's confirmation (paid_at is set by nothing else).
create or replace function public.ghostheart_order_paid(order_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from ghostheart_orders.story_orders o
     where o.id = ghostheart_order_paid.order_id
       and o.paid_at is not null
  );
$$;
revoke all on function public.ghostheart_order_paid(uuid) from public, authenticated, service_role;
grant execute on function public.ghostheart_order_paid(uuid) to anon;

-- Check: should return one row with
--   anon can check paid = true, anon can mark paid = false, service can mark paid = true,
--   anon can read orders = false.
select has_function_privilege('anon', 'public.ghostheart_order_paid(uuid)', 'execute') as "anon can check paid",
       has_function_privilege('anon', 'public.ghostheart_mark_order_paid(uuid, text)', 'execute') as "anon can mark paid (must be false)",
       has_function_privilege('service_role', 'public.ghostheart_mark_order_paid(uuid, text)', 'execute') as "service can mark paid",
       has_table_privilege('anon', 'ghostheart_orders.story_orders', 'select') as "anon can read orders (must be false)";
