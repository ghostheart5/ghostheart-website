export const THREADS = new Set([
  'journal:how-we-got-here', 'journal:this-is-ghostheart',
  'journal:ghosthearts-oath', 'journal:youre-not-god',
]);

export function validateSubmission(value: unknown) {
  if (!value || typeof value !== 'object') return null;
  const input = value as Record<string, unknown>;
  if (typeof input.thread !== 'string' || !THREADS.has(input.thread) ||
      typeof input.name !== 'string' || typeof input.body !== 'string' ||
      input.consent !== true || input.website !== '') return null;
  const name = input.name.trim();
  const body = input.body.trim();
  if (name.length < 2 || name.length > 60 || body.length < 10 || body.length > 1000) return null;
  if (/[\u0000-\u001f\u007f]/.test(name) || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(body)) return null;
  return { thread: input.thread, name, body };
}

export function publicComment(row: Record<string, unknown>) {
  return { name: row.display_name, body: row.body, published_at: row.approved_at };
}
