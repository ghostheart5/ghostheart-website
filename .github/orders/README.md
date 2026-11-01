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

## Verified payment (owner, once)
After paying, Stripe sends the customer back to `/here-to-help/?paid=1`. Anyone can type that address, so the
page only says **"Payment confirmed"** when Stripe itself has told the database the order is paid. Until these
steps are done (or if the check never says yes), the page keeps the plain note "Stripe emails your receipt when
the payment goes through". Nothing breaks either way.

How it works: Stripe calls a small Supabase Edge Function (`supabase/functions/stripe-webhook/index.ts`) when a
payment finishes. The function checks Stripe's signature, then marks that one order `paid` (with `paid_at` and the
Stripe session id). The page asks `public.ghostheart_order_paid(order_id)`, which answers only yes or no.

1. **Run the SQL.** Supabase > GHOSTHEART STUDIOS > SQL Editor: paste `supabase/verified-payment.review.sql` and
   press Run. The last line must show `anon can check paid = true`, `anon can mark paid = false`,
   `service can mark paid = true`, `anon can read orders = false`.
2. **Deploy the function.** On a computer with the Supabase CLI, signed in and linked to the project
   (`supabase link --project-ref pgqaqqliefpofsktjhjq`), copy the folder `supabase/functions/stripe-webhook` into
   the project's `supabase/functions/` folder, then run:
   `supabase functions deploy stripe-webhook --no-verify-jwt`
   (`--no-verify-jwt` is needed because Stripe cannot send a Supabase login; the Stripe signature is the lock.)
   Its address is `https://pgqaqqliefpofsktjhjq.supabase.co/functions/v1/stripe-webhook`.
3. **Add the webhook in Stripe.** Stripe > Developers > Webhooks > Add endpoint. Endpoint URL: the address above.
   Events: `checkout.session.completed` (optionally also `checkout.session.async_payment_succeeded`). Save, then
   copy the endpoint's **Signing secret** (`whsec_...`).
4. **Set the secrets.** `supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...` (or Supabase > Edge Functions >
   Secrets). Recommended: also set `STRIPE_PAYMENT_LINK_ID=plink_...` (the song Payment Link's id, shown on the
   link's page in Stripe) so only that link can mark a song paid. Never put either value in this repository.
   `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are provided to the function by Supabase automatically.
5. **Check the return address.** On the song Payment Link > After payment: "Don't show confirmation page",
   redirect to `https://www.myghostheart.com/here-to-help/?paid=1#order`.
6. **Test once in Stripe test mode.** Turn on Test mode, add a second webhook endpoint (same URL, same event) and
   set `STRIPE_WEBHOOK_SECRET` to the **test** endpoint's signing secret. Send yourself a free try from the page
   (your own email), copy its order id from `story_orders`, open the test link
   `https://buy.stripe.com/test_9B6cN551A2Ml24haFA6Ri00?client_reference_id=<that id>` and pay with card
   `4242 4242 4242 4242`, any future date, any CVC. Then check: the webhook shows `200` in Stripe, and that row now
   has `status = paid` and a `paid_at` date. Set that test row to `cancelled` afterwards.
   If you set `STRIPE_PAYMENT_LINK_ID`, set it to the test link's id for this test.
7. **Switch to live.** Set `STRIPE_WEBHOOK_SECRET` (and `STRIPE_PAYMENT_LINK_ID`) back to the **live** endpoint's
   values. Only one secret is used at a time, so the test endpoint stops working then; that is expected.

Stripe retries a webhook for up to 3 days if the function fails, and a repeated webhook changes nothing.
The function only ignores (200) other events, unpaid sessions, payments under $50 USD, or another Payment Link.

## Reading orders
Supabase > Table Editor > schema `ghostheart_orders` > `story_orders`. Stripe sends its own payment emails.
Paid song orders show `status = paid` with a `paid_at` date and the Stripe session id.

## Turning it off
Run `supabase/rollback.review.sql` (keeps saved orders), or empty `songPayLink` in `orders-config.js`.
The rollback also turns off verified payment; the page then shows the plain receipt note.
