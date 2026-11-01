// GhostHeart Studios: Stripe webhook for the $50 custom song (owner decision OWNER-BLUEPRINT-20261028).
// Supabase Edge Function. Deploy: supabase functions deploy stripe-webhook --no-verify-jwt
// (Stripe cannot send a Supabase login token, so the Stripe signature check below is the lock instead.)
//
// What it does:
//   * Checks that the request really came from Stripe (Stripe-Signature, HMAC-SHA256 with the endpoint's
//     signing secret, at most 5 minutes old). Anything else gets 400 and changes nothing.
//   * On checkout.session.completed (and checkout.session.async_payment_succeeded) whose payment_status is
//     'paid', it marks the order named by client_reference_id as paid, once, through
//     public.ghostheart_mark_order_paid (see ../../verified-payment.review.sql).
//   * Every other event gets 200 and is ignored. Repeats of the same event change nothing.
//
// Secrets (Supabase > Edge Functions > Secrets; never in this repository):
//   STRIPE_WEBHOOK_SECRET      required. The endpoint's signing secret from Stripe (whsec_...).
//   STRIPE_PAYMENT_LINK_ID     optional, recommended. The song Payment Link's id (plink_...). When set, only
//                              payments made through that link can mark a song order paid.
//   SONG_MIN_AMOUNT_CENTS      optional. Lowest amount that counts as the song payment. Default 5000 ($50 USD).
//   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY are provided by Supabase automatically.
//
// Nothing here charges anyone, sends email, or returns order details.

const TOLERANCE_SECONDS = 300;
const ORDER_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

type CheckoutSession = {
  id?: string;
  object?: string;
  client_reference_id?: string | null;
  payment_status?: string;
  payment_link?: string | null;
  amount_total?: number | null;
  currency?: string | null;
};

type StripeEvent = {
  id?: string;
  type?: string;
  data?: { object?: CheckoutSession };
};

function reply(status: number, message: string): Response {
  return new Response(JSON.stringify({ ok: status < 300, message }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function toHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer), (b) => b.toString(16).padStart(2, "0")).join("");
}

// Same-length comparison that does not stop at the first different character.
function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// Stripe's documented scheme: header "t=<unix seconds>,v1=<hex>[,v1=<hex>...]";
// v1 = HMAC-SHA256(secret, "<t>.<raw body>").
async function verifyStripeSignature(
  rawBody: string,
  header: string | null,
  secret: string,
  nowSeconds: number = Math.floor(Date.now() / 1000),
): Promise<boolean> {
  if (!header || !secret) return false;
  let timestamp = "";
  const signatures: string[] = [];
  for (const part of header.split(",")) {
    const eq = part.indexOf("=");
    if (eq < 0) continue;
    const key = part.slice(0, eq).trim();
    const value = part.slice(eq + 1).trim();
    if (key === "t") timestamp = value;
    else if (key === "v1") signatures.push(value);
  }
  if (!/^\d+$/.test(timestamp) || signatures.length === 0) return false;
  if (Math.abs(nowSeconds - Number(timestamp)) > TOLERANCE_SECONDS) return false;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const expected = toHex(
    await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(timestamp + "." + rawBody)),
  );
  return signatures.some((sig) => safeEqual(sig.toLowerCase(), expected));
}

async function markPaid(orderId: string, sessionId: string): Promise<string> {
  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !serviceKey) throw new Error("Supabase settings missing");
  const response = await fetch(url + "/rest/v1/rpc/ghostheart_mark_order_paid", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: serviceKey,
      Authorization: "Bearer " + serviceKey,
    },
    body: JSON.stringify({ order_id: orderId, session_id: sessionId }),
  });
  if (!response.ok) throw new Error("mark paid failed: " + response.status);
  return String(await response.json());
}

async function handle(request: Request): Promise<Response> {
  if (request.method !== "POST") return reply(405, "POST only");
  const secret = Deno.env.get("STRIPE_WEBHOOK_SECRET") ?? "";
  if (!secret) return reply(500, "STRIPE_WEBHOOK_SECRET is not set");

  // The signature covers the exact raw bytes, so read the body as text before parsing it.
  const rawBody = await request.text();
  if (!(await verifyStripeSignature(rawBody, request.headers.get("stripe-signature"), secret))) {
    return reply(400, "bad signature");
  }

  let event: StripeEvent;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return reply(400, "bad body");
  }

  const type = event.type ?? "";
  if (type !== "checkout.session.completed" && type !== "checkout.session.async_payment_succeeded") {
    return reply(200, "ignored: " + type);
  }
  const session = event.data?.object ?? {};
  if (session.object !== "checkout.session" || session.payment_status !== "paid") {
    return reply(200, "ignored: not paid yet");
  }
  const orderId = String(session.client_reference_id ?? "").toLowerCase();
  const sessionId = String(session.id ?? "");
  if (!ORDER_ID.test(orderId) || !/^cs_[A-Za-z0-9_]+$/.test(sessionId)) {
    return reply(200, "ignored: no order id");
  }
  const linkId = Deno.env.get("STRIPE_PAYMENT_LINK_ID") ?? "";
  if (linkId && session.payment_link !== linkId) {
    return reply(200, "ignored: other payment link");
  }
  const minAmount = Number(Deno.env.get("SONG_MIN_AMOUNT_CENTS") ?? "5000");
  if (String(session.currency ?? "").toLowerCase() !== "usd" || Number(session.amount_total ?? 0) < minAmount) {
    return reply(200, "ignored: amount below the song price");
  }

  try {
    const result = await markPaid(orderId, sessionId);
    console.log("stripe-webhook", event.id, sessionId, result);
    return reply(200, result);
  } catch (error) {
    // 500 makes Stripe retry later (it retries for up to 3 days).
    console.error("stripe-webhook", event.id, String(error));
    return reply(500, "could not record payment");
  }
}

Deno.serve(handle);
