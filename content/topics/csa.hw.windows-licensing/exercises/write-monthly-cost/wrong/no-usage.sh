# Wrong: right sums, but no check for a missing estate. Run with nothing,
# tail complains that it can't open '', and the script still prints three
# lines of 0.00 and exits 0, as if an empty estate cost nothing.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
tail -n +2 "$1" | awk -F, '
  { n = $2 } n < 4 { n = 4 }
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
