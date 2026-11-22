-- Starting everything over, for real (ADR-0029, amended 2026-11-22; an
-- exception to ADR-0008 that the owner asked for).
--
-- A learner who starts everything over wants their history gone, not
-- hidden. Events are append-only: learners have no DELETE grant, and a
-- trigger refuses every delete, even an admin's, unless the transaction
-- sets app.allow_event_deletion (see the first migration). This function is
-- the one door through both, and it is narrow:
--
--   * it deletes only the events of whoever calls it (auth.uid()), all of
--     them, and nothing else: no other learner's rows, no other table;
--   * it takes no arguments, so there is nothing a caller can aim;
--   * the permission to delete lasts only for this transaction.
--
-- It is "security definer": it runs with its owner's rights, because the
-- caller has none to delete with. That is why search_path is empty and
-- every name below is written in full.
--
-- What it leaves: the learner's profile and sign-in, their problem reports
-- (messages to the owner), and ai_calls, which is the spending ledger the
-- monthly cap is counted from (ADR-0013).

create function public.erase_my_history()
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  learner uuid := (select auth.uid());
  erased bigint;
begin
  if learner is null then
    raise exception 'erase_my_history: nobody is signed in';
  end if;
  -- true = for this transaction only.
  perform set_config('app.allow_event_deletion', 'on', true);
  delete from public.events where user_id = learner;
  get diagnostics erased = row_count;
  perform set_config('app.allow_event_deletion', 'off', true);
  return erased;
end;
$$;

comment on function public.erase_my_history() is
  'Deletes every event of the signed-in learner, for good (ADR-0029, amended 2026-11-22). Returns how many.';

revoke execute on function public.erase_my_history() from public, anon;
grant execute on function public.erase_my_history() to authenticated;
