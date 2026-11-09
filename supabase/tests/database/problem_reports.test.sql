-- Database tests for problem reports (v1 spec, F15).
-- Run with: npm run db:test (needs the local database running).
-- Everything happens in one transaction that's rolled back at the end.
begin;
select plan(9);

-- Two learners, Ada and Bob.
insert into auth.users (id, email) values
  ('11111111-1111-1111-1111-111111111111', 'ada@example.com'),
  ('22222222-2222-2222-2222-222222222222', 'bob@example.com');

-- Bob's report, added as an admin would see it.
insert into public.problem_reports (user_id, topic_id, item_id, item_rev, message)
values ('22222222-2222-2222-2222-222222222222', 'py.variables', 'mcq-1', 1,
        'The second choice is also right.');

-- As Ada, a signed-in learner ------------------------------------------------

set local role authenticated;
select set_config('request.jwt.claims',
  '{"sub": "11111111-1111-1111-1111-111111111111", "role": "authenticated"}', true);

select lives_ok(
  $$ insert into public.problem_reports (user_id, topic_id, item_id, item_rev, message)
     values ('11111111-1111-1111-1111-111111111111', 'py.variables', 'fill-swap', 2,
             'The hint mentions a line that is not there.') $$,
  'A learner can report a problem with an item'
);

select lives_ok(
  $$ insert into public.problem_reports (user_id, topic_id, message)
     values ('11111111-1111-1111-1111-111111111111', 'py.variables',
             'The video link is dead.') $$,
  'A report can be about the topic as a whole'
);

select results_eq(
  $$ select count(*)::int from public.problem_reports where status = 'open' $$,
  $$ values (2) $$,
  'A new report starts open, and a learner sees only their own reports'
);

select throws_ok(
  $$ insert into public.problem_reports (user_id, topic_id, message)
     values ('22222222-2222-2222-2222-222222222222', 'py.variables', 'Not mine') $$,
  '42501', null,
  'A learner cannot report in someone else''s name'
);

select throws_ok(
  $$ insert into public.problem_reports (user_id, topic_id, message, status)
     values ('11111111-1111-1111-1111-111111111111', 'py.variables', 'Done already',
             'resolved') $$,
  '42501', null,
  'A learner cannot open a report as resolved'
);

select throws_ok(
  $$ update public.problem_reports set status = 'resolved' $$,
  '42501', null,
  'A learner cannot resolve reports'
);

select throws_ok(
  $$ delete from public.problem_reports $$,
  '42501', null,
  'A learner cannot delete reports'
);

select throws_ok(
  $$ insert into public.problem_reports (user_id, topic_id, message)
     values ('11111111-1111-1111-1111-111111111111', 'py.variables', '') $$,
  '23514', null,
  'A report needs a message'
);

-- As the owner, in the dashboard ---------------------------------------------

reset role;

select lives_ok(
  $$ update public.problem_reports set status = 'resolved'
     where user_id = '22222222-2222-2222-2222-222222222222' $$,
  'The owner can resolve a report'
);

select * from finish();
rollback;
