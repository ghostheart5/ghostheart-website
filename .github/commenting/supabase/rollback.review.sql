-- LOCAL ROLLBACK PLAN ONLY. Do not run without first checking that all four
-- blog tables contain no visitor data and that no external object depends on
-- the blog roles/schema. Restore from the verified project backup if needed.
-- This removes only objects created by the GhostHeart blog foundation.

do $$
begin
  if exists (select 1 from pg_namespace where nspname = 'ghostheart_blog') then
    if (select count(*) from ghostheart_blog.comments) > 0 or
       (select count(*) from ghostheart_blog.attempts) > 0 or
       (select count(*) from ghostheart_blog.moderation_events) > 0 then
      raise exception 'Blog tables contain data; rollback requires explicit data decision';
    end if;
  end if;
end;
$$;

drop schema if exists ghostheart_blog cascade;
drop role if exists ghostheart_blog_api;
drop role if exists ghostheart_blog_moderator;
drop role if exists ghostheart_blog_retention;
