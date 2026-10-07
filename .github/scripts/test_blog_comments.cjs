const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

// Run the function handler with a fake SQL connection. A real database test is
// required before opening comments; this checks HTTP validation and SQL shape.
let source = fs.readFileSync('supabase/functions/blog-comments/index.ts', 'utf8');
source = source.replace("import postgres from 'npm:postgres@3.4.7'", '');
source = source.replace('function reply(data: unknown, status = 200)', 'function reply(data, status = 200)');
let handler;
const queries = [];
const sql = async (parts, ...values) => {
  const query = parts.join('?');
  queries.push({ query, values });
  return query.includes('select id')
    ? [{ id: 7, display_name: 'Sam', body: 'An approved comment', approved_at: '2026-10-07' }]
    : [];
};
vm.runInNewContext(source, {
  Deno: { env: { get: () => 'postgres://restricted.example.invalid/blog' }, serve: fn => { handler = fn; } },
  postgres: () => sql, Request, Response, URL, Set, console,
});
const origin = 'https://www.myghostheart.com';
const request = (method, path, data, requestOrigin = origin) => new Request(
  `https://example.invalid${path}`,
  { method, headers: { origin: requestOrigin, ...(data ? { 'content-type': 'application/json' } : {}) },
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
  assert.equal((await handler(request('POST', '/', valid))).status, 202);
  assert.match(queries[1].query, /insert into ghostheart_blog.comments \(thread, display_name, body\)/);
  assert.deepEqual(queries[1].values, ['journal:ghosthearts-oath', 'Sam', 'A thoughtful comment.']);
  assert.equal(queries.length, 2, 'invalid submissions must not reach the database');
  console.log('PASS blog comments: origin, approved read, consent, limits, pending insert shape');
})().catch(error => { console.error(error); process.exitCode = 1; });
