// "I'm here to help" order settings (owner decision OWNER-BLUEPRINT-20261028).
// The form stays closed ("Orders open soon") until all three values are filled in:
//   supabaseKey : the project's PUBLISHABLE (anon) key from Supabase > Project Settings > API keys.
//                 It is meant to be public. Never paste the secret / service_role key here.
//   songPayLink : the Stripe Payment Link for the $50 custom song (https://buy.stripe.com/...).
// After setting them, run .github/orders/supabase/story-orders.review.sql in Supabase once.
window.GHOSTHEART_ORDERS = {
  supabaseUrl: 'https://pgqaqqliefpofsktjhjq.supabase.co',
  supabaseKey: 'sb_publishable_P7GsZrSsz839xa3xhJ3bbA_JKcTZNXp',
  songPayLink: ''
};
