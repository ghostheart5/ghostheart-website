const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');

// Run the function handler with a fake SQL connection. A real database test is
// required before opening comments; this checks HTTP validation and SQL shape.
let source = fs.readFileSync('supabase/functions/blog-comments/index.ts', 'utf8');
source = source.replace("import postgres from 'npm:postgres@3.4.7'", '');
source = source.replace('function reply(data: unknown, status = 200)', 'function reply(data, status = 200)');
source = source.replace('markerFor(request: Request)', 'markerFor(request)');
let handler;
const queries = [];
const attempts = new Map();
const sql = async (parts, ...values) => {
  const query = parts.join('?');
  queries.push({ query, values });
  if (query.includes('select id')) return [
    { id: 7, display_name: 'Sam', body: 'An approved comment', approved_at: '2026-10-07' },
  ];
  if (query.includes('count(*)::int')) return [{ total: attempts.get(values[0]) || 0 }];
  if (query.includes('insert into ghostheart_blog.attempts')) {
    attempts.set(values[0], (attempts.get(values[0]) || 0) + 1);
  }
  return [];
};
sql.begin = async fn => fn(sql);
vm.runInNewContext(source, {
  Deno: { env: { get: name => name === 'GHOSTHEART_COMMENTS_DB_URL'
    ? 'postgres://restricted.example.invalid/blog' : 'test-marker-secret-with-over-32-characters' },
    serve: fn => { handler = fn; } },
  postgres: () => sql, Request, Response, URL, Set, TextEncoder, Uint8Array,
  crypto: webcrypto, console,
});
const origin = 'https://www.myghostheart.com';
const request = (method, path, data, requestOrigin = origin, forwardedFor = '198.51.100.10') => new Request(
  `https://example.invalid${path}`,
  { method, headers: { origin: requestOrigin, 'x-forwarded-for': forwardedFor,
    ...(data ? { 'content-type': 'application/json' } : {}) },
    ...(data ? { body: JSON.stringify(data) } : {}) },
);

(async () => {
  assert.equal((await handler(request('GET', '/?post=this-is-ghostheart', null, 'https://evil.invalid'))).status, 403);
  const list = await handler(request('GET', '/?post=this-is-ghostheart'));
  assert.equal(list.status, 200);
  assert.equal((await list.json()).comments[0].display_name, 'Sam');
  assert.match(queries[0].query, /where thread = \? and status = 'approved'/);
  assert.equal(queries[0].values[0], 'journal:this-is-ghostheart');
  const valid = { post: 'ghosthearts-oath', name: 'Sam', body: 'A thoughtful comment.', consent: true };
  assert.equal((await handler(request('POST', '/', { ...valid, consent: false }))).status, 400);
  assert.equal((await handler(request('POST', '/', { ...valid, body: 'short' }))).status, 400);
  assert.equal((await handler(request('POST', '/', valid, origin, ''))).status, 400);
  assert.equal((await handler(request('POST', '/', valid))).status, 202);
  const first = queries.slice(1);
  assert.match(first[0].query, /pg_advisory_xact_lock/);
  assert.match(first[1].query, /ghostheart_blog.attempts/);
  assert.match(first[1].query, /attempted_at > now\(\) - interval '1 hour'/);
  assert.match(first[2].query, /insert into ghostheart_blog.attempts/);
  assert.match(first[3].query, /insert into ghostheart_blog.comments \(thread, display_name, body\)/);
  assert.deepEqual(first[3].values, ['journal:ghosthearts-oath', 'Sam', 'A thoughtful comment.']);
  assert.equal(first[0].values[0], first[1].values[0], 'lock and count share marker');
  for (let i = 0; i < 4; i++) {
    assert.equal((await handler(request('POST', '/', valid))).status, 202);
  }
  assert.equal((await handler(request('POST', '/', valid, origin,
    '203.0.113.88, 198.51.100.10'))).status, 429,
    'spoofing the leftmost forwarded address must not evade the limit');
  assert.equal(queries.filter(item => item.query.includes('insert into ghostheart_blog.comments')).length, 5);
  assert.equal(attempts.size, 1, 'only HMAC markers are stored');
  console.log('PASS blog comments: origin, approval, consent, pending insert, durable five-per-hour limit');
})().catch(error => { console.error(error); process.exitCode = 1; });
