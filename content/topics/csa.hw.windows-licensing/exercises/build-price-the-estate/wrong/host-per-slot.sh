# Wrong: prices the host as if Fenwick paid for the slots it uses, six
# thirty-seconds of its hourly price, so the host "wins". A Dedicated Host is
# billed whole, full or empty: $6.758 an hour against 6 x $0.376 = $2.256.
cat > ~/report/estate.txt <<'EOF'
azure_windows_licences=48
sql_licences=28
monthly_licence_included=11946
monthly_best=4754
host_break_even_vms=18
host_cheaper=yes
EOF
