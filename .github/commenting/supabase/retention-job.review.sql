-- Daily Supabase Cron SQL job. Cron connects as postgres and immediately
-- switches to the narrow ghostheart_blog_retention role for every data action.
-- Every table deletion is capped at 1000 rows per run. A backlog leaves the
-- heartbeat stale so the public POST endpoint closes until cleanup catches up.
begin;
set local role ghostheart_blog_retention;

with expired as (
  select ctid from ghostheart_blog.attempts
  where attempted_at < now() - interval '2 days'
  order by attempted_at limit 1000
)
delete from ghostheart_blog.attempts a using expired e where a.ctid = e.ctid;

with expired as (
  select ctid from ghostheart_blog.comments
  where status in ('pending', 'rejected')
    and created_at < now() - interval '30 days'
  order by created_at limit 1000
)
delete from ghostheart_blog.comments c using expired e where c.ctid = e.ctid;

with expired as (
  select ctid from ghostheart_blog.moderation_events
  where decided_at < now() - interval '90 days'
  order by decided_at limit 1000
)
delete from ghostheart_blog.moderation_events m using expired e where m.ctid = e.ctid;

update ghostheart_blog.retention_state set last_run_at = now()
where singleton = true
  and not exists (select 1 from ghostheart_blog.attempts
                  where attempted_at < now() - interval '2 days')
  and not exists (select 1 from ghostheart_blog.comments
                  where status in ('pending', 'rejected')
                    and created_at < now() - interval '30 days')
  and not exists (select 1 from ghostheart_blog.moderation_events
                  where decided_at < now() - interval '90 days');

commit;
