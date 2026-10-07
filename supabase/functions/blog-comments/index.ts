// Public blog conversation endpoint. Deploy only after the restricted database
// role, RLS policies, and GHOSTHEART_COMMENTS_DB_URL secret are installed.
import postgres from 'npm:postgres@3.4.7'

const origin = 'https://www.myghostheart.com'
const allowedPosts = new Set([
  'this-is-ghostheart',
  'ghosthearts-oath',
  'youre-not-god',
  'how-we-got-here',
])
const databaseUrl = Deno.env.get('GHOSTHEART_COMMENTS_DB_URL')
if (!databaseUrl) throw new Error('GHOSTHEART_COMMENTS_DB_URL is required')
const sql = postgres(databaseUrl, { max: 1, idle_timeout: 10, connect_timeout: 5, prepare: false })

function reply(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'access-control-allow-origin': origin,
      'access-control-allow-methods': 'GET, POST, OPTIONS',
      'access-control-allow-headers': 'content-type',
      'vary': 'Origin',
      'cache-control': 'no-store',
    },
  })
}

Deno.serve(async (request) => {
  if (request.headers.get('origin') !== origin) return reply({ error: 'Origin not allowed' }, 403)
  if (request.method === 'OPTIONS') return reply({}, 200)
  const url = new URL(request.url)
  try {
    if (request.method === 'GET') {
      const post = url.searchParams.get('post')
      if (!post || !allowedPosts.has(post)) return reply({ error: 'Unknown post' }, 400)
      const comments = await sql`
        select id, display_name, body, created_at
        from ghostheart_blog.comments
        where post_slug = ${post} and status = 'approved'
        order by created_at desc
        limit 50
      `
      return reply({ comments })
    }
    if (request.method !== 'POST') return reply({ error: 'Method not allowed' }, 405)
    if (!request.headers.get('content-type')?.startsWith('application/json')) {
      return reply({ error: 'JSON required' }, 415)
    }
    const raw = await request.text()
    if (raw.length > 4000) return reply({ error: 'Comment too long' }, 413)
    const input = JSON.parse(raw)
    if (typeof input !== 'object' || input === null || Array.isArray(input)) {
      return reply({ error: 'Invalid comment' }, 400)
    }
    if (input.website) return reply({ pending: true }, 202)
    const post = input.post
    const name = typeof input.name === 'string' ? input.name.trim() : ''
    const body = typeof input.body === 'string' ? input.body.trim() : ''
    if (!allowedPosts.has(post) || name.length < 1 || name.length > 60 ||
        body.length < 1 || body.length > 2000) {
      return reply({ error: 'Check the post, name, and comment length' }, 400)
    }
    await sql`
      insert into ghostheart_blog.comments (post_slug, display_name, body)
      values (${post}, ${name}, ${body})
    `
    return reply({ pending: true }, 202)
  } catch (error) {
    console.error('Blog comments request failed', error)
    return reply({ error: 'Comments are temporarily unavailable' }, 503)
  }
})
