-- Database tests for erasing one's own history (ADR-0029, amended
-- 2026-11-22). Run with: npm run db:test (needs the local database running).
begin;
select plan(8);

insert into auth.users (id, email) values
  ('55555555-5555-5555-5555-555555555555', 'eve@example.com'),
  ('66666666-6666-6666-6666-666666666666', 'fay@example.com');

-- Two events for Eve, one for Fay, written as an admin.
insert into public.events
  (id, user_id, type, topic_id, item_id, context, correct,
   content_build, session_id, occurred_at, data)
values
  (gen_random_uuid(), '55555555-5555-5555-5555-555555555555', 'answer',
   'py.variables', 'mcq-one', 'practice', true,
   'test', gen_random_uuid(), now(), '{}'),
  (gen_random_uuid(), '55555555-5555-5555-5555-555555555555', 'track_reset',
   'everything', null, 'learn', null,
   'test', gen_random_uuid(), now(), '{}'),
  (gen_random_uuid(), '66666666-6666-6666-6666-666666666666', 'answer',
   'py.variables', 'mcq-one', 'practice', false,
   'test', gen_random_uuid(), now(), '{}');

-- Nobody signed in: the function is not theirs to call.
set local role anon;
select throws_ok(
  $$ select public.erase_my_history() $$,
  '42501', null,
  'A visitor who is not signed in cannot call it'
);
reset role;

-- Act as Eve.
set local role authenticated;
select set_config('request.jwt.claims',
  '{"sub": "55555555-5555-5555-5555-555555555555", "role": "authenticated"}', true);

select is(
  (select public.erase_my_history()), 2::bigint,
  'It deletes every event of the learner who calls it, and says how many'
);

select is(
  (select count(*) from public.events), 0::bigint,
  'She has no events left'
);

select throws_ok(
  $$ delete from public.events
     where user_id = '55555555-5555-5555-5555-555555555555' $$,
  '42501', null,
  'She still cannot delete events herself'
);

select is(
  (select public.erase_my_history()), 0::bigint,
  'Calling it again with nothing left deletes nothing'
);

-- Back to an admin, to see everyone's rows.
reset role;

select is(
  (select count(*) from public.events
   where user_id = '66666666-6666-6666-6666-666666666666'), 1::bigint,
  'Another learner''s events are untouched'
);

select is(
  (select count(*) from public.profiles
   where id = '55555555-5555-5555-5555-555555555555'), 1::bigint,
  'Her profile stays'
);

select throws_ok(
  $$ delete from public.events $$,
  'P0001', 'events are append-only: delete is not allowed (ADR-0008)',
  'The permission did not outlast the call: an admin still cannot delete events'
);

select * from finish();
rollback;
