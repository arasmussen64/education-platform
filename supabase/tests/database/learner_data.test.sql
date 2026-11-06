-- Database tests for profiles and the append-only event log.
-- Run with: npm run db:test (needs the local database running).
-- Everything happens in one transaction that's rolled back at the end.
begin;
select plan(18);

-- Two learners, Ada and Bob.
insert into auth.users (id, email, raw_user_meta_data) values
  ('11111111-1111-1111-1111-111111111111', 'ada@example.com', '{"name": "Ada"}'),
  ('22222222-2222-2222-2222-222222222222', 'bob@example.com', '{"user_name": "bob"}');

-- Profiles -------------------------------------------------------------------

select results_eq(
  $$ select display_name, allowed from public.profiles order by display_name $$,
  $$ values ('Ada'::text, false), ('bob'::text, false) $$,
  'Signing up creates a profile, named from the sign-in provider, not yet allowed'
);

-- From here on, act as Ada (a signed-in learner).
set local role authenticated;
select set_config('request.jwt.claims',
  '{"sub": "11111111-1111-1111-1111-111111111111", "role": "authenticated"}', true);

select results_eq(
  $$ select count(*)::int from public.profiles $$,
  $$ values (1) $$,
  'A learner can only see their own profile'
);

select lives_ok(
  $$ update public.profiles set display_name = 'Ada L.'
     where id = '11111111-1111-1111-1111-111111111111' $$,
  'A learner can rename themselves'
);

select throws_ok(
  $$ update public.profiles set allowed = true
     where id = '11111111-1111-1111-1111-111111111111' $$,
  '42501', null,
  'A learner cannot allow themselves to use the AI'
);

-- Events ---------------------------------------------------------------------

select lives_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, context, correct, content_build, session_id, occurred_at)
     values
       ('aaaaaaaa-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111',
        'answer', 'py.variables', 'practice', true, 'abc123',
        'bbbbbbbb-0000-0000-0000-000000000001', now()) $$,
  'A learner can record their own event'
);

select lives_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, context, correct, content_build, session_id, occurred_at)
     values
       ('aaaaaaaa-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111',
        'answer', 'py.variables', 'practice', true, 'abc123',
        'bbbbbbbb-0000-0000-0000-000000000001', now())
     on conflict (id) do nothing $$,
  'Re-sending the same event is harmless'
);

select results_eq(
  $$ select count(*)::int from public.events $$,
  $$ values (1) $$,
  '...and it is stored only once'
);

select throws_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, context, content_build, session_id, occurred_at)
     values
       ('aaaaaaaa-0000-0000-0000-000000000002', '22222222-2222-2222-2222-222222222222',
        'answer', 'py.variables', 'practice', 'abc123',
        'bbbbbbbb-0000-0000-0000-000000000001', now()) $$,
  '42501', null,
  'A learner cannot record events for someone else'
);

select throws_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, context, content_build, session_id, occurred_at, received_at)
     values
       ('aaaaaaaa-0000-0000-0000-000000000003', '11111111-1111-1111-1111-111111111111',
        'answer', 'py.variables', 'practice', 'abc123',
        'bbbbbbbb-0000-0000-0000-000000000001', now(), '2000-01-01') $$,
  '42501', null,
  'A learner cannot set when the server received an event'
);

select throws_ok(
  $$ insert into public.events
       (id, user_id, type, topic_id, context, content_build, session_id, occurred_at)
     values
       ('aaaaaaaa-0000-0000-0000-000000000004', '11111111-1111-1111-1111-111111111111',
        'cheat', 'py.variables', 'practice', 'abc123',
        'bbbbbbbb-0000-0000-0000-000000000001', now()) $$,
  '23514', null,
  'Unknown event types are rejected'
);

select throws_ok(
  $$ update public.events set correct = false
     where id = 'aaaaaaaa-0000-0000-0000-000000000001' $$,
  '42501', null,
  'A learner cannot edit their events'
);

select throws_ok(
  $$ delete from public.events
     where id = 'aaaaaaaa-0000-0000-0000-000000000001' $$,
  '42501', null,
  'A learner cannot delete their events'
);

-- Act as Bob: he must not see Ada's event.
select set_config('request.jwt.claims',
  '{"sub": "22222222-2222-2222-2222-222222222222", "role": "authenticated"}', true);

select is_empty(
  $$ select * from public.events $$,
  'A learner cannot see anyone else''s events'
);

-- Signed-out visitors get nothing at all.
reset role;
set local role anon;

select throws_ok(
  $$ select * from public.events $$,
  '42501', null,
  'Signed-out visitors cannot read events'
);

-- Even an admin can't rewrite history ------------------------------------------
reset role;

select throws_ok(
  $$ update public.events set correct = false $$,
  'P0001', 'events are append-only: update is not allowed (ADR-0008)',
  'Not even an admin can edit events'
);

select throws_ok(
  $$ delete from public.events $$,
  'P0001', 'events are append-only: delete is not allowed (ADR-0008)',
  'Not even an admin can delete events'
);

select throws_ok(
  $$ truncate public.events $$,
  'P0001', 'events are append-only: truncate is not allowed (ADR-0008)',
  'Not even an admin can empty the table'
);

-- ...except when deliberately deleting a whole account.
set local app.allow_event_deletion = 'on';

select lives_ok(
  $$ delete from auth.users where id = '11111111-1111-1111-1111-111111111111' $$,
  'An admin can delete a whole account, events included, when they opt in'
);

select * from finish();
rollback;
