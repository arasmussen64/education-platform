# Wrong: only the VMs' prices, as if SQL Server cost nothing. The Windows
# side is right, but SQL Server licence included is charged on top of the VM.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then echo "usage: monthly-cost ESTATE" >&2; exit 2; fi
tail -n +2 "$1" | awk -F, '
  { included += $8 }
  { hourly = $8 } $5 == "yes" { hourly = $7 }
  { benefit += hourly }
  END {
    printf "licence-included: %.2f\n", included * 730
    printf "with-hybrid-benefit: %.2f\n", benefit * 730
    printf "saving: %.2f\n", (included - benefit) * 730
  }'
EOF
chmod +x ~/bin/monthly-cost
