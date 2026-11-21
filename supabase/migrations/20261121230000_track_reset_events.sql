-- Starting a track over (ADR-0029).
--
-- A learner who wants a clean start on a track appends one 'track_reset'
-- event whose topic_id is the track's id. Nothing is deleted or changed:
-- the progress derivation ignores that track's events from before the
-- newest reset, and the full history stays in the log for the ML capstone
-- (ADR-0008). Only the list of event types changes.

alter table public.events drop constraint events_type_check;
alter table public.events add constraint events_type_check check (type in (
  'lesson_view', 'answer', 'code_run', 'code_check',
  'explain_submit', 'hint', 'review', 'placement', 'track_reset'
));
