-- Database tests for the AI call log and the month's spending (ADR-0013).
-- Run with: npm run db:test (needs the local database running).
-- Everything happens in one transaction that's rolled back at the end.
begin;
select plan(11);

-- Two learners, Ada and Bob.
insert into auth.users (id, email) values
  ('11111111-1111-1111-1111-111111111111', 'ada@example.com'),
  ('22222222-2222-2222-2222-222222222222', 'bob@example.com');

-- As the proxy would log them: a call each this month, and one of Ada's
-- from last month.
insert into public.ai_calls
  (user_id, action, model, input_tokens, output_tokens, cost_usd, created_at)
values
  ('11111111-1111-1111-1111-111111111111', 'grade_explanation',
   'claude-haiku-5-5', 1500, 900, 0.0006, now()),
  ('22222222-2222-2222-2222-222222222222', 'grade_explanation',
   'claude-haiku-5-5', 1400, 800, 0.0005, now()),
  ('11111111-1111-1111-1111-111111111111', 'grade_explanation',
   'claude-haiku-5-5', 1500, 900, 2.5,
   date_trunc('month', now(), 'UTC') - interval '1 day');

select is(
  public.ai_spend_this_month(),
  0.0011::numeric,
  'The month''s spending adds up this calendar month''s calls only'
);

-- As Ada, a signed-in learner ------------------------------------------------

set local role authenticated;
select set_config('request.jwt.claims',
  '{"sub": "11111111-1111-1111-1111-111111111111", "role": "authenticated"}', true);

select results_eq(
  $$ select count(*)::int from public.ai_calls $$,
  $$ values (2) $$,
  'A learner reads only their own AI calls'
);

select throws_ok(
  $$ insert into public.ai_calls (user_id, action, model) values
     ('11111111-1111-1111-1111-111111111111', 'grade_explanation', 'claude-haiku-5-5') $$,
  '42501', null,
  'A learner cannot log an AI call: only the proxy can'
);

select throws_ok(
  $$ update public.ai_calls set cost_usd = 0 $$,
  '42501', null,
  'A learner cannot change an AI call'
);

select throws_ok(
  $$ select public.ai_spend_this_month() $$,
  '42501', null,
  'A learner cannot ask for the month''s spending'
);

-- As a signed-out visitor ----------------------------------------------------

set local role anon;

select throws_ok(
  $$ select count(*) from public.ai_calls $$,
  '42501', null,
  'A signed-out visitor cannot read AI calls'
);

-- As the proxy (the service role) --------------------------------------------

set local role service_role;

select lives_ok(
  $$ insert into public.ai_calls (user_id, action, model, cost_usd) values
     ('22222222-2222-2222-2222-222222222222', 'grade_explanation',
      'claude-haiku-5-5', 0.0004) $$,
  'The proxy can log a call'
);

select is(
  public.ai_spend_this_month(),
  0.0015::numeric,
  'The proxy can ask for the month''s spending, which includes the new call'
);

select throws_ok(
  $$ update public.ai_calls set cost_usd = 0 $$,
  'P0001', 'ai_calls is append-only: update is not allowed (ADR-0013)',
  'Even the proxy cannot rewrite a call'
);

select throws_ok(
  $$ delete from public.ai_calls $$,
  'P0001', 'ai_calls is append-only: delete is not allowed (ADR-0013)',
  'Even the proxy cannot delete a call'
);

-- Deliberately deleting a whole account ---------------------------------------

reset role;
select set_config('app.allow_event_deletion', 'on', true);
delete from auth.users where id = '22222222-2222-2222-2222-222222222222';

select results_eq(
  $$ select count(*)::int from public.ai_calls
     where user_id = '22222222-2222-2222-2222-222222222222' $$,
  $$ values (0) $$,
  'Deliberately deleting an account removes its AI calls too'
);

select * from finish();
rollback;
