-- Database tests for the placement test's events (ADR-0021).
-- Run with: npm run db:test (needs the local database running).
begin;
select plan(4);

insert into auth.users (id, email) values
  ('33333333-3333-3333-3333-333333333333', 'cy@example.com');

-- Act as Cy, a signed-in learner.
set local role authenticated;
select set_config('request.jwt.claims',
  '{"sub": "33333333-3333-3333-3333-333333333333", "role": "authenticated"}', true);

select lives_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, item_id, context, correct,
        content_build, session_id, occurred_at, data)
     values
       (gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'answer',
        'py.variables', 'reassign-mcq', 'placement', false,
        'test', gen_random_uuid(), now(), '{"run": "r1", "choice": 1}') $$,
  'An answer given during a placement is an answer in the placement context'
);

select lives_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, item_id, context, correct,
        content_build, session_id, occurred_at, data)
     values
       (gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'placement',
        'python-foundations', 'placement', 'placement', null,
        'test', gen_random_uuid(), now(),
        '{"run": "r1", "kind": "track", "known": ["py.programs-and-print"], "next": "py.values-and-types"}') $$,
  'A finished placement is one placement event'
);

select throws_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, item_id, context, correct,
        content_build, session_id, occurred_at)
     values
       (gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'answer',
        'py.variables', 'reassign-mcq', 'guess', false,
        'test', gen_random_uuid(), now()) $$,
  '23514', null,
  'Other contexts are still refused'
);

select throws_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, item_id, context, correct,
        content_build, session_id, occurred_at)
     values
       (gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'guess',
        'py.variables', 'reassign-mcq', 'placement', false,
        'test', gen_random_uuid(), now()) $$,
  '23514', null,
  'Other event types are still refused'
);

select * from finish();
rollback;
