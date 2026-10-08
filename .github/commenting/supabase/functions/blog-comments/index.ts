// Public comment handler. Submission is controlled by GHOSTHEART_BLOG_POST_ENABLED.
import postgres from 'npm:postgres@3.4.7';
import { publicComment, THREADS, validateSubmission } from './core.ts';

const ORIGIN = 'https://www.myghostheart.com';
const headers = { 'Access-Control-Allow-Origin': ORIGIN, 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type', 'Vary': 'Origin', 'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store' };
const reply = (status: number, payload: Record<string, unknown>) =>
  new Response(JSON.stringify(payload), { status, headers });
const databasePassword = Deno.env.get('GHOSTHEART_BLOG_DB_PASSWORD');
const connection = databasePassword
  ? `postgresql://ghostheart_blog_runtime:${encodeURIComponent(databasePassword)}@db.pgqaqqliefpofsktjhjq.supabase.co:6543/postgres`
  : null;
const sql = connection ? postgres(connection, { max: 1, prepare: false, ssl: 'require',
  idle_timeout: 2, connect_timeout: 5 }) : null;

async function markerFor(address: string, key: string) {
  const material = await crypto.subtle.importKey('raw', new TextEncoder().encode(key),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  // Stable across midnight so a rolling hourly limit cannot reset at 00:00.
  // Attempts are retained only briefly and the secret is rotated operationally.
  const bytes = new Uint8Array(await crypto.subtle.sign('HMAC', material, new TextEncoder().encode(address)));
  return Array.from(bytes, value => value.toString(16).padStart(2, '0')).join('');
}

async function readLimited(request: Request, limit: number): Promise<string | null> {
  if (!request.body) return '';
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > limit) { await reader.cancel(); return null; }
      chunks.push(value);
    }
    const combined = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) { combined.set(chunk, offset); offset += chunk.byteLength; }
    return new TextDecoder('utf-8', { fatal: true }).decode(combined);
  } finally { reader.releaseLock(); }
}

Deno.serve(async request => {
  if (request.headers.get('origin') !== ORIGIN) return reply(403, { error: 'origin' });
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
  if (request.method !== 'GET' && request.method !== 'POST') return reply(405, { error: 'method' });
  if (!sql) return reply(503, { error: 'unavailable' });
  try {
    if (request.method === 'GET') {
      const thread = new URL(request.url).searchParams.get('thread');
      if (!thread || !THREADS.has(thread)) return reply(400, { error: 'thread' });
      const rows = await sql`
        select display_name, body, approved_at from ghostheart_blog.comments
        where thread = ${thread} and status = 'approved'
        order by approved_at asc limit 100`;
      return reply(200, { comments: rows.map(publicComment) });
    }
    if (Deno.env.get('GHOSTHEART_BLOG_POST_ENABLED') !== 'true')
      return reply(503, { error: 'unavailable' });
    if (Number(request.headers.get('content-length') || 0) > 4096) return reply(413, { error: 'size' });
    if (!request.headers.get('content-type')?.startsWith('application/json')) return reply(415, { error: 'type' });
    const raw = await readLimited(request, 4096);
    if (raw === null) return reply(413, { error: 'size' });
    let value: unknown;
    try { value = JSON.parse(raw); } catch { return reply(400, { error: 'json' }); }
    const input = validateSubmission(value);
    if (!input) return reply(400, { error: 'invalid' });

    // Configure this only after verifying that the gateway overwrites this header.
    // Untrusted X-Forwarded-For values must never be used for rate limiting.
    const headerName = Deno.env.get('GHOSTHEART_TRUSTED_ADDRESS_HEADER');
    const signingKey = Deno.env.get('GHOSTHEART_ABUSE_HMAC_KEY');
    const forwarded = headerName && request.headers.get(headerName);
    // The Supabase gateway overwrote a forged X-Forwarded-For value in the
    // October 7 probe. Its own header contained multiple proxy hops.
    const address = forwarded?.split(',')[0]?.trim();
    if (!headerName || !signingKey || !address) return reply(503, { error: 'unavailable' });
    const marker = await markerFor(address, signingKey);
    const accepted = await sql.begin(async tx => {
      const retention = await tx`
        select last_run_at > now() - interval '48 hours' as recent
        from ghostheart_blog.retention_state where singleton = true`;
      if (retention[0]?.recent !== true) throw new Error('retention job stale');
      await tx`select pg_advisory_xact_lock(hashtext(${marker}))`;
      const recent = await tx`
        select count(*)::int as count from ghostheart_blog.attempts
        where marker = ${marker} and attempted_at > now() - interval '1 hour'`;
      if (recent[0].count >= 3) return false;
      await tx`insert into ghostheart_blog.attempts (marker) values (${marker})`;
      await tx`
        insert into ghostheart_blog.comments (thread, display_name, body, status)
        values (${input.thread}, ${input.name}, ${input.body}, 'pending')`;
      return true;
    });
    return accepted ? reply(202, { status: 'pending' }) : reply(429, { error: 'rate' });
  } catch {
    return reply(503, { error: 'unavailable' });
  }
});
