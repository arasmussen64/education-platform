# Wrong: no minimums. Every VM takes one licence a vCPU however small it is,
# so the 2- and 4-vCPU Windows servers count less than the 8 each must have,
# and db-1's SQL Server 2 instead of 4.
sed -i -e 's/windows_minimum = \.\.\./windows_minimum = 0/' \
  -e 's/sql_minimum = \.\.\./sql_minimum = 0/' \
  -e 's/runs_sql = \.\.\./runs_sql = $4 != "none"/' \
  -e 's|packs: " \.\.\.|packs: " sql / 2|' ~/bin/licence-count
~/bin/licence-count /srv/licensing/estate.csv
