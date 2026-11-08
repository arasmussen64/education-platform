-- The AI call log, and the month's spending it adds up to (ADR-0013).
-- Design: docs/specs/data-model.md ("ai_calls") and ADR-0013.
--
-- Once this migration has reached production, never edit it. Change the
-- schema with a new migration instead (ADR-0010).

------------------------------------------------------------------------------
-- ai_calls: one row per call to Claude, written only by the AI proxy (the
-- Edge Function, with the service role). It's how the monthly budget cap is
-- enforced, and how the tutor's and grader's quality gets reviewed.
------------------------------------------------------------------------------

create table public.ai_calls (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now(),
  action text not null check (action in ('grade_explanation', 'tutor_hint')),
  model text not null check (char_length(model) between 1 and 100),
  input_tokens integer not null default 0 check (input_tokens >= 0),
  output_tokens integer not null default 0 check (output_tokens >= 0),
  -- Estimated from the token counts and the proxy's price table.
  cost_usd numeric(12, 6) not null default 0 check (cost_usd >= 0),
  request jsonb not null default '{}'::jsonb
    check (pg_column_size(request) <= 16384),
  response jsonb not null default '{}'::jsonb
    check (pg_column_size(response) <= 16384)
);

comment on table public.ai_calls is
  'Append-only log of calls to Claude (ADR-0013). Only the AI proxy writes to it.';

create index ai_calls_by_time on public.ai_calls (created_at);
create index ai_calls_by_user_and_time on public.ai_calls (user_id, created_at);

alter table public.ai_calls enable row level security;

create policy "Learners can read their own AI calls"
  on public.ai_calls for select to authenticated
  using ((select auth.uid()) = user_id);

-- Learners can read their own rows and nothing else. The proxy writes with
-- the service role, which row-level security doesn't apply to.
revoke all on public.ai_calls from anon, authenticated;
grant select on public.ai_calls to authenticated;

-- Like events, a call is never rewritten. Deliberately deleting a whole
-- account works the same way as for events: in the same transaction,
--   set local app.allow_event_deletion = 'on';
create function public.forbid_ai_call_changes()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if tg_op = 'DELETE'
     and current_setting('app.allow_event_deletion', true) = 'on' then
    return old;
  end if;
  raise exception 'ai_calls is append-only: % is not allowed (ADR-0013)',
    lower(tg_op);
end;
$$;

revoke execute on function public.forbid_ai_call_changes()
  from public, anon, authenticated;

create trigger ai_calls_are_never_changed
  before update or delete on public.ai_calls
  for each row execute function public.forbid_ai_call_changes();

create trigger ai_calls_are_never_truncated
  before truncate on public.ai_calls
  for each statement execute function public.forbid_ai_call_changes();

------------------------------------------------------------------------------
-- The month's spending, for the budget cap: every call since the start of
-- this calendar month, in UTC, by anyone. Only the proxy may ask.
------------------------------------------------------------------------------

create function public.ai_spend_this_month()
returns numeric
language sql
stable
set search_path = ''
as $$
  select coalesce(sum(cost_usd), 0)
  from public.ai_calls
  where created_at >= date_trunc('month', now(), 'UTC');
$$;

revoke execute on function public.ai_spend_this_month()
  from public, anon, authenticated;
grant execute on function public.ai_spend_this_month() to service_role;
