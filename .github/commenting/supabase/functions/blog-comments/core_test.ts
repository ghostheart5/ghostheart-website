import { publicComment, validateSubmission } from './core.ts';
const assertEquals = (actual: unknown, expected: unknown) => {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(`Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
};

const valid = { thread: 'journal:this-is-ghostheart', name: ' Reader ', body: 'A thoughtful response.', consent: true, website: '' };
Deno.test('only a known article with explicit consent enters moderation', () => {
  assertEquals(validateSubmission(valid), { thread: valid.thread, name: 'Reader', body: valid.body });
  assertEquals(validateSubmission({ ...valid, consent: false }), null);
  assertEquals(validateSubmission({ ...valid, thread: 'journal:invented' }), null);
  assertEquals(validateSubmission({ ...valid, website: 'spam.example' }), null);
  assertEquals(validateSubmission({ ...valid, body: 'short' }), null);
});
Deno.test('public projection omits moderation and abuse fields', () => {
  assertEquals(publicComment({ display_name: 'Reader', body: 'Hello', approved_at: '2026-10-07T00:00:00Z',
    email: 'private@example.com', abuse_marker: 'private', status: 'approved' }),
    { name: 'Reader', body: 'Hello', published_at: '2026-10-07T00:00:00Z' });
});
