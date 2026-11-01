-- Turns the order form off at the database. Keeps the saved orders.
revoke execute on function public.submit_ghostheart_order(jsonb) from anon;

-- Turns verified payment off (verified-payment.review.sql). Keeps the saved orders and their paid_at dates.
-- The website then always shows the plain "Stripe emails your receipt" note after payment.
revoke execute on function public.ghostheart_order_paid(uuid) from anon;
revoke execute on function public.ghostheart_mark_order_paid(uuid, text) from service_role;

-- To remove everything, including saved orders (cannot be undone), run these too:
-- drop function if exists public.ghostheart_order_paid(uuid);
-- drop function if exists public.ghostheart_mark_order_paid(uuid, text);
-- drop function if exists public.submit_ghostheart_order(jsonb);
-- drop schema if exists ghostheart_orders cascade;
-- drop role if exists ghostheart_orders_reader;
