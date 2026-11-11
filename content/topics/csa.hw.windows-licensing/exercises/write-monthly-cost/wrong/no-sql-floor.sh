# Wrong: SQL Server priced on the vCPUs as they are, with no minimum of 4.
# db-1's SQL Server Standard on 2 vCPUs, with no Software Assurance, comes out
# at half what Azure charges for it, in both months.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then echo "usage: monthly-cost ESTATE" >&2; exit 2; fi
tail -n +2 "$1" | awk -F, '
  { n = $2 }
  $4 == "standard" { rate = 0.10 } $4 == "enterprise" { rate = 0.375 } $4 == "none" { rate = 0 }
  { included += $8 + rate * n }
  { hourly = $8 } $5 == "yes" { hourly = $7 } $6 != "yes" { hourly += rate * n }
  { benefit += hourly }
  END {
    printf "licence-included: %.2f\n", included * 730
    printf "with-hybrid-benefit: %.2f\n", benefit * 730
    printf "saving: %.2f\n", (included - benefit) * 730
  }'
EOF
chmod +x ~/bin/monthly-cost
