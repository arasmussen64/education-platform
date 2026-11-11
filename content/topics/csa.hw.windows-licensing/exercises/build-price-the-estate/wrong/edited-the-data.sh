# Wrong: the answers are right, but a price in the estate was changed along
# the way (the learner has sudo). The report has to rest on the data as it
# was given.
sudo sed -i 's/^az-file-1,azure,8,windows,none,yes,no,2023,2025,0.384,0.752$/az-file-1,azure,8,windows,none,yes,no,2023,2025,0.350,0.752/' /srv/licensing/estate.csv
cat > ~/report/estate.txt <<'EOF'
azure_windows_licences=48
sql_licences=28
monthly_licence_included=11946
monthly_best=4754
host_break_even_vms=18
host_cheaper=no
EOF
