-- Turns the order form off at the database. Keeps the saved orders.
revoke execute on function public.submit_ghostheart_order(jsonb) from anon;

-- To remove everything, including saved orders (cannot be undone), run these too:
-- drop function if exists public.submit_ghostheart_order(jsonb);
-- drop schema if exists ghostheart_orders cascade;
-- drop role if exists ghostheart_orders_reader;
