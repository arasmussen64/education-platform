# Wrong: 16 as the Windows Server minimum, which is the minimum for a whole
# physical server licensed by its cores. A VM under Azure Hybrid Benefit
# needs at least 8.
sed -i -e 's/windows_minimum = \.\.\./windows_minimum = 16/' \
  -e 's/sql_minimum = \.\.\./sql_minimum = 4/' \
  -e 's/runs_sql = \.\.\./runs_sql = $4 != "none"/' \
  -e 's|packs: " \.\.\.|packs: " sql / 2|' ~/bin/licence-count
~/bin/licence-count /srv/licensing/estate.csv
