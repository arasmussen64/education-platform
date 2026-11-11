# Wrong: licences counted as vCPUs, with no minimums, and SQL Server priced
# on the vCPUs each VM has. The 2- and 4-vCPU Windows servers on Azure each
# need 8 core licences, az-db-1's SQL Server needs 4, and every cloud
# charges SQL Server licence included for at least 4 vCPUs.
cat > ~/report/estate.txt <<'EOF'
azure_windows_licences=32
sql_licences=26
monthly_licence_included=11800
monthly_best=4754
host_break_even_vms=18
host_cheaper=no
EOF
