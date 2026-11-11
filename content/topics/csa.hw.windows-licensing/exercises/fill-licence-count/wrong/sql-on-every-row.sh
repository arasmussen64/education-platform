# Wrong: every server counted as running SQL Server, so the servers that run
# none (web, app, file, cache) get SQL Server licences they don't need.
sed -i -e 's/windows_minimum = \.\.\./windows_minimum = 8/' \
  -e 's/sql_minimum = \.\.\./sql_minimum = 4/' \
  -e 's/runs_sql = \.\.\./runs_sql = 1/' \
  -e 's|packs: " \.\.\.|packs: " sql / 2|' ~/bin/licence-count
~/bin/licence-count /srv/licensing/estate.csv
