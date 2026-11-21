-- Database tests for starting a track over (ADR-0029).
-- Run with: npm run db:test (needs the local database running).
begin;
select plan(3);

insert into auth.users (id, email) values
  ('44444444-4444-4444-4444-444444444444', 'dee@example.com');

-- Act as Dee, a signed-in learner.
set local role authenticated;
select set_config('request.jwt.claims',
  '{"sub": "44444444-4444-4444-4444-444444444444", "role": "authenticated"}', true);

select lives_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, item_id, context, correct,
        content_build, session_id, occurred_at, data)
     values
       (gen_random_uuid(), '44444444-4444-4444-4444-444444444444', 'track_reset',
        'python-foundations', null, 'learn', null,
        'test', gen_random_uuid(), now(), '{}') $$,
  'Starting a track over is one track_reset event'
);

select throws_ok(
  $$ delete from public.events
     where user_id = '44444444-4444-4444-4444-444444444444' $$,
  '42501', null,
  'A reset deletes nothing, and a learner still cannot delete events'
);

select throws_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, item_id, context, correct,
        content_build, session_id, occurred_at)
     values
       (gen_random_uuid(), '44444444-4444-4444-4444-444444444444', 'reset_everything',
        'python-foundations', null, 'learn', null,
        'test', gen_random_uuid(), now()) $$,
  '23514', null,
  'Other event types are still refused'
);

select * from finish();
rollback;
