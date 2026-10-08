// Public blog conversation endpoint for the existing ghostheart_blog schema.
// Deploy only after its approved restricted login, RLS policies, and secret exist.
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
const markerSecret = Deno.env.get('GHOSTHEART_COMMENT_MARKER_KEY')
if (!markerSecret || markerSecret.length < 32) throw new Error('GHOSTHEART_COMMENT_MARKER_KEY is required')
const sql = postgres(databaseUrl, { max: 1, idle_timeout: 10, connect_timeout: 5, prepare: false })
const markerKey = crypto.subtle.importKey('raw', new TextEncoder().encode(markerSecret),
  { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])

async function markerFor(request: Request) {
  // Use the last proxy-added address. Launch testing must verify that the
  // Supabase gateway appends or overwrites this value, not merely forwards it.
  const address = request.headers.get('x-forwarded-for')?.split(',').at(-1)?.trim()
  if (!address || !/^[0-9a-fA-F:.]{3,64}$/.test(address)) return null
  const signature = await crypto.subtle.sign('HMAC', await markerKey,
    new TextEncoder().encode(`ghostheart-blog-v1:${address}`))
  return [...new Uint8Array(signature)].map(byte => byte.toString(16).padStart(2, '0')).join('')
}

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
      const thread = `journal:${post}`
      const comments = await sql`
        select id, display_name, body, approved_at
        from ghostheart_blog.comments
        where thread = ${thread} and status = 'approved'
        order by approved_at desc
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
    let input
    try { input = JSON.parse(raw) } catch { return reply({ error: 'Invalid JSON' }, 400) }
    if (typeof input !== 'object' || input === null || Array.isArray(input)) {
      return reply({ error: 'Invalid comment' }, 400)
    }
    if (input.website) return reply({ pending: true }, 202)
    const post = input.post
    const name = typeof input.name === 'string' ? input.name.trim() : ''
    const body = typeof input.body === 'string' ? input.body.trim() : ''
    if (!allowedPosts.has(post) || name.length < 2 || name.length > 60 ||
        body.length < 10 || body.length > 1000 || input.consent !== true) {
      return reply({ error: 'Check the post, name, and comment length' }, 400)
    }
    const marker = await markerFor(request)
    if (!marker) return reply({ error: 'Could not verify submission source' }, 400)
    const thread = `journal:${post}`
    const accepted = await sql.begin(async (tx) => {
      // Serialize concurrent submissions from the same marker before counting.
      await tx`select pg_advisory_xact_lock(hashtextextended(${marker}, 0))`
      const [{ total }] = await tx`
        select count(*)::int as total from ghostheart_blog.attempts
        where marker = ${marker} and attempted_at > now() - interval '1 hour'
      `
      if (total >= 5) return false
      await tx`insert into ghostheart_blog.attempts (marker) values (${marker})`
      await tx`
        insert into ghostheart_blog.comments (thread, display_name, body)
        values (${thread}, ${name}, ${body})
      `
      return true
    })
    if (!accepted) return reply({ error: 'Please wait before commenting again' }, 429)
    return reply({ pending: true }, 202)
  } catch (error) {
    console.error('Blog comments request failed', error)
    return reply({ error: 'Comments are temporarily unavailable' }, 503)
  }
})
