# Wrong: treats Software Assurance as carrying Windows Server to AWS's shared
# instances, so the six AWS servers are priced as Linux. Windows Server has
# no License Mobility: on shared instances it is licence included, whatever
# its Software Assurance.
cat > ~/report/estate.txt <<'EOF'
azure_windows_licences=48
sql_licences=28
monthly_licence_included=11946
monthly_best=3948
host_break_even_vms=18
host_cheaper=no
EOF
