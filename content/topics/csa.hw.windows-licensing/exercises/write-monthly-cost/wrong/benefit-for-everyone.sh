# Wrong: Azure Hybrid Benefit on every server, Software Assurance or not.
# The month with the benefit is too cheap: web-2, app-2, db-1 and db-4 have
# no Software Assurance to bring.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then echo "usage: monthly-cost ESTATE" >&2; exit 2; fi
tail -n +2 "$1" | awk -F, '
  { n = $2 } n < 4 { n = 4 }
  $4 == "standard" { rate = 0.10 } $4 == "enterprise" { rate = 0.375 } $4 == "none" { rate = 0 }
  { included += $8 + rate * n }
  { benefit += $7 }
  END {
    printf "licence-included: %.2f\n", included * 730
    printf "with-hybrid-benefit: %.2f\n", benefit * 730
    printf "saving: %.2f\n", (included - benefit) * 730
  }'
EOF
chmod +x ~/bin/monthly-cost
