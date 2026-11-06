-- Learner data, part 1: profiles and the append-only event log.
-- Design: docs/specs/data-model.md and ADR-0008.
--
-- Once this migration has reached production, never edit it. Change the
-- schema with a new migration instead (ADR-0010).

------------------------------------------------------------------------------
-- Profiles: one row per learner, created automatically at sign-up.
------------------------------------------------------------------------------

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text check (char_length(display_name) <= 100),
  -- Lets this learner use the AI features while sign-ups are closed
  -- (v1 spec, F1). Learners can't change it themselves; see the grants below.
  allowed boolean not null default false,
  settings jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

comment on table public.profiles is
  'One row per learner, created by a trigger when an auth user is created.';

alter table public.profiles enable row level security;

create policy "Learners can read their own profile"
  on public.profiles for select to authenticated
  using ((select auth.uid()) = id);

create policy "Learners can update their own profile"
  on public.profiles for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

-- Learners may read their row and change only these two columns of it.
revoke all on public.profiles from anon, authenticated;
grant select on public.profiles to authenticated;
grant update (display_name, settings) on public.profiles to authenticated;

-- Runs with the table owner's rights, so it can insert the profile row.
create function public.create_profile_for_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(
      new.raw_user_meta_data ->> 'name',
      new.raw_user_meta_data ->> 'user_name'
    )
  );
  return new;
end;
$$;

revoke execute on function public.create_profile_for_new_user()
  from public, anon, authenticated;

create trigger create_profile_after_sign_up
  after insert on auth.users
  for each row execute function public.create_profile_for_new_user();

------------------------------------------------------------------------------
-- Events: the append-only record of everything a learner does (ADR-0008).
-- Progress is computed from these rows. They are never edited or deleted.
------------------------------------------------------------------------------

create table public.events (
  -- Created in the browser, so a retried upload can't create a duplicate.
  id uuid primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  type text not null check (type in (
    'lesson_view', 'answer', 'code_run', 'code_check',
    'explain_submit', 'hint', 'review'
  )),
  topic_id text not null check (char_length(topic_id) between 1 and 200),
  item_id text check (char_length(item_id) between 1 and 200),
  context text not null
    check (context in ('learn', 'practice', 'prove', 'review')),
  correct boolean,
  duration_ms integer check (duration_ms >= 0),
  hints_used integer not null default 0 check (hints_used >= 0),
  item_rev integer check (item_rev >= 1),
  -- The git commit the content was built from.
  content_build text not null,
  session_id uuid not null,
  -- When it happened, by the learner's clock.
  occurred_at timestamptz not null,
  -- When the server got it. Always set by the database (see the grants).
  received_at timestamptz not null default now(),
  data jsonb not null default '{}'::jsonb
    check (pg_column_size(data) <= 16384)
);

comment on table public.events is
  'Append-only learner history (ADR-0008). Future ML training data: never edit or delete.';

create index events_by_user_and_time on public.events (user_id, occurred_at);
create index events_by_user_and_topic on public.events (user_id, topic_id);

alter table public.events enable row level security;

create policy "Learners can read their own events"
  on public.events for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "Learners can add their own events"
  on public.events for insert to authenticated
  with check ((select auth.uid()) = user_id);

-- Learners can read and add events, nothing else. received_at isn't in the
-- insert list, so it always gets the server's time.
revoke all on public.events from anon, authenticated;
grant select on public.events to authenticated;
grant insert (
  id, user_id, type, topic_id, item_id, context, correct, duration_ms,
  hints_used, item_rev, content_build, session_id, occurred_at, data
) on public.events to authenticated;

-- Belt and braces: even an admin or the service role can't rewrite history.
-- The one exception is deliberately deleting a whole account: an admin runs
--   set local app.allow_event_deletion = 'on';
-- in the same transaction as deleting the user.
create function public.forbid_event_changes()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if tg_op = 'DELETE'
     and current_setting('app.allow_event_deletion', true) = 'on' then
    return old;
  end if;
  raise exception 'events are append-only: % is not allowed (ADR-0008)',
    lower(tg_op);
end;
$$;

revoke execute on function public.forbid_event_changes()
  from public, anon, authenticated;

create trigger events_are_never_changed
  before update or delete on public.events
  for each row execute function public.forbid_event_changes();

create trigger events_are_never_truncated
  before truncate on public.events
  for each statement execute function public.forbid_event_changes();
