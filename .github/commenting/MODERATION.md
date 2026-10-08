# GhostHeart blog comment moderation

Website comments are stored in the private `ghostheart_blog` schema of the existing GHOSTHEART STUDIOS Supabase project. They do not appear in Metricool. Use the signed-in Supabase SQL Editor to review them. Check the queue regularly; there is no email alert yet.

Never save a SQL query that contains a password or secret. Do not approve comments containing personal contact details, threats, crisis details, or spam. The public site shows only approved display names, comment text, and approval dates.

## Review pending comments

```sql
select id, thread, display_name, body, created_at
from ghostheart_blog.comments
where status = 'pending'
order by created_at asc
limit 100;
```

Read the full comment and note its exact `id`. Replace `0` below with only the ID you reviewed. Run one decision at a time. An update of zero rows makes no change.

## Approve one comment

```sql
begin;
set local role ghostheart_blog_moderator;
update ghostheart_blog.comments
set status = 'approved'
where id = 0 and status = 'pending'
returning id, thread, display_name, status, approved_at;
commit;
```

## Reject one comment

```sql
begin;
set local role ghostheart_blog_moderator;
update ghostheart_blog.comments
set status = 'rejected'
where id = 0 and status = 'pending'
returning id, thread, display_name, status;
commit;
```

The database fills or clears `approved_at` when the status changes and records the decision and acting role. Pending and rejected comments expire after 30 days; decision records expire after 90 days. Approved comments remain until removed. For a removal request sent to `signal@myghostheart.com`, identify the exact comment ID and verify it is the requested comment before deletion.

The public form remains closed until the local website change is published and `GHOSTHEART_BLOG_POST_ENABLED` is set to `true` for the deployed Edge Function. The comment GET endpoint can already read approved comments. The daily retention job is active, but its first automatic run still needs to be observed.
