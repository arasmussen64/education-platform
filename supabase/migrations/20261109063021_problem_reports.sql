-- Problem reports (v1 spec, F15): a learner's note that something on a
-- lesson, exercise or question is wrong, kept with the item and its revision
-- so the content can be fixed. Design: docs/specs/data-model.md.
--
-- Once this migration has reached production, never edit it. Change the
-- schema with a new migration instead (ADR-0010).

create table public.problem_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now(),
  topic_id text not null check (char_length(topic_id) between 1 and 200),
  -- The item within the topic, or null for the topic as a whole. The parts
  -- of a topic that aren't items are named too: 'lesson' and 'explain'.
  item_id text check (char_length(item_id) between 1 and 200),
  -- The item's rev when the report was made, so a report about an old
  -- version can be told apart from one about the current version.
  item_rev integer check (item_rev >= 1),
  message text not null check (char_length(message) between 1 and 2000),
  -- The owner sets resolved once the content is fixed.
  status text not null default 'open' check (status in ('open', 'resolved'))
);

comment on table public.problem_reports is
  'Learners'' reports of problems with the content (v1 spec, F15). Learners add and read their own; the owner resolves them.';

create index problem_reports_by_status_and_time
  on public.problem_reports (status, created_at);

alter table public.problem_reports enable row level security;

create policy "Learners can read their own problem reports"
  on public.problem_reports for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "Learners can add their own problem reports"
  on public.problem_reports for insert to authenticated
  with check ((select auth.uid()) = user_id);

-- Learners can add a report and read their own, nothing else. status isn't
-- in the insert list, so every new report starts open; only the owner, in
-- the dashboard, changes it.
revoke all on public.problem_reports from anon, authenticated;
grant select on public.problem_reports to authenticated;
grant insert (user_id, topic_id, item_id, item_rev, message)
  on public.problem_reports to authenticated;
