-- Lets the two newer blog posts take comments (2026-10-31).
-- Run once in the Supabase SQL editor for project pgqaqqliefpofsktjhjq,
-- then redeploy the blog-comments Edge Function (its core.ts allowlist was updated too).
begin;
alter table ghostheart_blog.comments drop constraint if exists comments_thread_check;
alter table ghostheart_blog.comments add constraint comments_thread_check check (thread in (
  'journal:how-we-got-here', 'journal:this-is-ghostheart',
  'journal:ghosthearts-oath', 'journal:youre-not-god',
  'journal:wake-the-heart-week', 'journal:cruel-something-needs-to-change'));
commit;
