# The finished script. In the lab you fill the four gaps with nano; here the
# whole file is written in one go: `cat > FILE <<'EOF'` writes every line up
# to the closing EOF into FILE, exactly as typed. The two minimums are 8 core
# licences a VM for Windows Server and 4 for SQL Server; a comparison in awk
# is worth 1 when it holds and 0 when it doesn't, so it can be kept in a
# variable; and the packs are the licences two at a time.
cat > ~/bin/licence-count <<'EOF'
#!/bin/bash
# Usage: licence-count ESTATE
# Counts the core licences the shop would have to own to bring every server
# of an estate to Azure with its own licences: every Windows Server VM through
# Azure Hybrid Benefit, and every SQL Server VM licensed by VM. It prints the
# Windows Server core licences, the SQL Server core licences, and the SQL
# Server packs of 2 to buy. /srv/licensing/README.txt describes the columns.
estate="$1"

tail -n +2 "$estate" | awk -F, '
  BEGIN {
    windows_minimum = 8      # the fewest Windows Server core licences a VM may take
    sql_minimum = 4          # the fewest SQL Server core licences a VM may take
  }

  # Windows Server: one core licence a vCPU, raised to the minimum.
  $3 == "windows" { w = $2 }
  $3 == "windows" && w < windows_minimum { w = windows_minimum }
  $3 == "windows" { windows += w }

  # SQL Server: only on the servers that run it, one a vCPU, raised to the minimum.
  { runs_sql = $4 != "none" }       # 1 on a line whose server runs SQL Server, 0 on any other
  runs_sql { s = $2 }
  runs_sql && s < sql_minimum { s = sql_minimum }
  runs_sql { sql += s }

  END {
    print "windows core licences: " windows + 0
    print "sql core licences: " sql + 0
    print "sql 2-core packs: " sql / 2
  }'
EOF
~/bin/licence-count /srv/licensing/estate.csv
