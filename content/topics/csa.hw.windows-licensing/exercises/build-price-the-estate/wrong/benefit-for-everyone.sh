# Wrong: Azure Hybrid Benefit on every Azure Windows server, and every SQL
# Server brought, Software Assurance or not. It looks cheapest; az-app-1's
# Windows and the SQL Servers of az-rpt-1 and aw-db-3 have no Software
# Assurance, so they may not be brought.
cat > ~/report/estate.txt <<'EOF'
azure_windows_licences=64
sql_licences=40
monthly_licence_included=11946
monthly_best=3416
host_break_even_vms=18
host_cheaper=no
EOF
