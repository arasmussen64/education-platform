# Wrong: the break-even divides the host's price by the Linux price of an
# m6i.xlarge (6.758 / 0.192), so it says 36. The VMs the host would replace
# are Windows VMs with the licence included, at 0.376 an hour each.
cat > ~/report/estate.txt <<'EOF'
azure_windows_licences=48
sql_licences=28
monthly_licence_included=11946
monthly_best=4754
host_break_even_vms=36
host_cheaper=no
EOF
