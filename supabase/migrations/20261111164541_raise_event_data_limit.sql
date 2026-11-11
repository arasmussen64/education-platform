-- Room for long programs in the event log.
--
-- Run, Step through and Check events save the learner's code with them
-- (web/src/events/payloads.ts). The first migration capped an event's data
-- at 16,384 bytes, which fitted Python Foundations, where the browser cut
-- code at 6,000 characters. Module 8 of the ML track has programs of up to
-- 12,323 characters, so the browser now keeps up to 20,000 (MAX_CODE_CHARS),
-- and this makes room for them: the log is future training data, and a
-- program cut in half can't be filled in later.
--
-- The limit is in bytes, not characters: a character takes up to three
-- bytes ("é" two, "中" three). At the very worst, 20,000 characters of code
-- and two 2,000-character texts (what it printed, and its error) take 72,000
-- bytes. 131,072 bytes (128 KB) fits that with room to spare, so the browser
-- can never build an event the database refuses for its size. Postgres
-- compresses large values when it stores them, so a long program takes less
-- room on disk than this.
--
-- Only the limit changes. Every event already stored is under the old limit,
-- so it's under the new one too.

alter table public.events drop constraint events_data_check;
alter table public.events add constraint events_data_check
  check (pg_column_size(data) <= 131072);
