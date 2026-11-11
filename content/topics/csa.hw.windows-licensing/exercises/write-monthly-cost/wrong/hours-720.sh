# Wrong: a month of 720 hours (30 days). Every line comes out 1.4% low,
# dollars off rather than cents; the README and the prompt say 730.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then echo "usage: monthly-cost ESTATE" >&2; exit 2; fi
tail -n +2 "$1" | awk -F, '
  { n = $2 } n < 4 { n = 4 }
  $4 == "standard" { rate = 0.10 } $4 == "enterprise" { rate = 0.375 } $4 == "none" { rate = 0 }
  { included += $8 + rate * n }
  { hourly = $8 } $5 == "yes" { hourly = $7 } $6 != "yes" { hourly += rate * n }
  { benefit += hourly }
  END {
    printf "licence-included: %.2f\n", included * 720
    printf "with-hybrid-benefit: %.2f\n", benefit * 720
    printf "saving: %.2f\n", (included - benefit) * 720
  }'
EOF
chmod +x ~/bin/monthly-cost
