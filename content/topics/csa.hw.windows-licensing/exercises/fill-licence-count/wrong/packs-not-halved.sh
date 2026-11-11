# Wrong: the packs line prints the core licences again. SQL Server core
# licences come two to a pack, so the packs are half as many.
sed -i -e 's/windows_minimum = \.\.\./windows_minimum = 8/' \
  -e 's/sql_minimum = \.\.\./sql_minimum = 4/' \
  -e 's/runs_sql = \.\.\./runs_sql = $4 != "none"/' \
  -e 's|packs: " \.\.\.|packs: " sql|' ~/bin/licence-count
~/bin/licence-count /srv/licensing/estate.csv
