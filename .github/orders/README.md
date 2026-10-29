# "I'm here to help" orders

Owner decision OWNER-BLUEPRINT-20261028. The page is `/here-to-help/`.

## How an order flows
1. **Custom song:** the customer fills in the story form. It is saved in Supabase (`ghostheart_orders.story_orders`),
   then the browser goes to the Stripe Payment Link with only the order id (`client_reference_id`). Stripe shows the
   payment with that id, so each payment matches one story.
2. **Office and production help:** the request is saved the same way, with no payment yet. The owner replies by
   email with the total, then sends a Stripe payment link or invoice.
3. Nothing is emailed or charged by the website itself. The website key can only add an order, never read one.

## Turning it on (owner, once)
1. Stripe: set the account to GhostHeart Studios (sole proprietor, EIN). Create a Payment Link for
   "Custom GhostHeart song", $50. Under "After payment", choose "Don't show confirmation page" and redirect to
   `https://www.myghostheart.com/here-to-help/?paid=1#order`.
2. Supabase > GHOSTHEART STUDIOS > SQL Editor: paste `supabase/story-orders.review.sql` and press Run. The last
   line must show `anon can execute = true` and `anon can read orders = false`.
3. Fill in `assets/help/orders-config.js`: the project's publishable key (Project Settings > API keys) and the
   Payment Link. The form opens on its own once both are set.

Only a **live** link (not `buy.stripe.com/test_...`) opens the form. A test link for trying the flow:
`https://buy.stripe.com/test_9B6cN551A2Ml24haFA6Ri00` (GhostHeart Studios sandbox, created 2026-10-28; no real money).

## Reading orders
Supabase > Table Editor > schema `ghostheart_orders` > `story_orders`. Stripe sends its own payment emails.

## Turning it off
Run `supabase/rollback.review.sql` (keeps saved orders), or empty `songPayLink` in `orders-config.js`.
