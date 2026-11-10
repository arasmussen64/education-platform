#!/usr/bin/env bash
# Rehearses the backup's restore path (ADR-0020) on the LOCAL database, so we
# never rely on a backup nobody has restored:
#
#   1. a learner with one event goes in;
#   2. the data is dumped the way the nightly backup dumps it;
#   3. the dump is encrypted and decrypted with a throwaway passphrase;
#   4. the local database is reset: empty tables, the schema from the
#      migrations, which is what a new project looks like;
#   5. the dump is restored with psql, the way docs/setup.md says to;
#   6. the learner, their profile and the event must be back.
#
# CI runs it on every pull request (the database job). To run it yourself,
# with the local Supabase running (npm run db:start), from the repository
# root in Git Bash:
#
#   bash tools/backup_restore_check.sh
#
# Step 4 resets the local database, and step 5 puts back everything that was
# in it, plus the test learner. It can't touch the real project: the dump and
# the reset target the local database only (ADR-0010).
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n== %s\n' "$*"; }
fail() { printf 'FAILED: %s\n' "$*" >&2; exit 1; }

# The local database runs in a container that has psql in it, so this works
# on a PC without psql installed. The container's name starts with
# supabase_db_ (the rest is project_id in supabase/config.toml).
find_container() { docker ps --filter 'name=^supabase_db_' --format '{{.Names}}' | head -n 1; }
container=$(find_container)
[ -n "$container" ] || fail "the local database isn't running; start it with: npm run db:start"

# Runs SQL on the local database as postgres. -tA prints bare values.
sql() { docker exec -i "$container" psql -U postgres -d postgres -v ON_ERROR_STOP=1 -tA "$@"; }

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

step "1. A learner with one event goes in"
user_id=$(sql -c 'select gen_random_uuid()')
event_id=$(sql -c 'select gen_random_uuid()')
sql <<SQL
insert into auth.users (id, email)
values ('$user_id', 'restore-check-${user_id:0:8}@example.com');
insert into public.events (id, user_id, type, topic_id, item_id, context,
  correct, duration_ms, content_build, session_id, occurred_at)
values ('$event_id', '$user_id', 'answer', 'py.programs-and-print', 'mcq-print',
  'learn', true, 1000, 'restore-check', gen_random_uuid(), now());
SQL
# Signing up creates the profile (a trigger); the restore must bring it back.
[ "$(sql -c "select count(*) from public.profiles where id = '$user_id'")" = 1 ] ||
  fail "signing up didn't create a profile"

step "2. Dump the data, the way the nightly backup does"
npx supabase db dump --data-only --schema public,auth --use-copy -f "$work/dump.sql"
grep -q '"public"."events"' "$work/dump.sql" || fail "the dump has no events data"
echo "$(wc -c <"$work/dump.sql") bytes"

step "3. Encrypt and decrypt it, with a throwaway passphrase"
passphrase=$(sql -c 'select md5(random()::text)')
printf '%s' "$passphrase" | gpg --batch --quiet --symmetric --cipher-algo AES256 \
  --pinentry-mode loopback --passphrase-fd 0 -o "$work/dump.sql.gpg" "$work/dump.sql"
printf '%s' "$passphrase" | gpg --batch --quiet --decrypt \
  --pinentry-mode loopback --passphrase-fd 0 -o "$work/restore.sql" "$work/dump.sql.gpg"
cmp -s "$work/dump.sql" "$work/restore.sql" || fail "the decrypted dump differs from the original"

step "4. Reset the local database: empty tables, the schema from the migrations"
npx supabase db reset --no-seed
container=$(find_container)
[ "$(sql -c "select count(*) from public.events where id = '$event_id'")" = 0 ] ||
  fail "the reset left the event in place"

step "5. Restore the dump"
# Any error stops it and rolls the whole restore back. Results of the dump's
# own housekeeping queries aren't worth printing; errors still are.
docker exec -i "$container" psql -U postgres -d postgres -v ON_ERROR_STOP=1 \
  --single-transaction --quiet -o /dev/null -f - <"$work/restore.sql"

step "6. The learner, their profile and the event must be back"
[ "$(sql -c "select count(*) from auth.users where id = '$user_id'")" = 1 ] ||
  fail "the learner didn't come back"
[ "$(sql -c "select count(*) from public.profiles where id = '$user_id'")" = 1 ] ||
  fail "the profile didn't come back"
[ "$(sql -c "select count(*) from public.events where id = '$event_id' and user_id = '$user_id'")" = 1 ] ||
  fail "the event didn't come back"
echo "Restored. The backup's restore path works."
