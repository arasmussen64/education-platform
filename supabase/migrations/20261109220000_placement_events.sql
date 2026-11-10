-- The placement test (ADR-0021).
--
-- Answers given during a placement carry the context 'placement', so the
-- progress derivation knows not to count them as starting a topic, and the
-- follow-ups know they aren't practice. A finished run is summed up by one
-- 'placement' event: which topics or levels count as known, and where to
-- start. Both are appended like every other event; nothing else changes.

alter table public.events drop constraint events_type_check;
alter table public.events add constraint events_type_check check (type in (
  'lesson_view', 'answer', 'code_run', 'code_check',
  'explain_submit', 'hint', 'review', 'placement'
));

alter table public.events drop constraint events_context_check;
alter table public.events add constraint events_context_check
  check (context in ('learn', 'practice', 'prove', 'review', 'placement'));
