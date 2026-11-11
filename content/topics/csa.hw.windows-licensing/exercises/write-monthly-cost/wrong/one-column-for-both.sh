# Wrong: one column decides the benefit for the whole VM. Where its Windows
# Server licences have Software Assurance (win_sa), the VM pays the Linux
# price and no SQL Server; elsewhere, everything is included. On the shop's
# estate that comes out right, because each SQL Server's two licences either
# both have Software Assurance or both don't; on a server where only one of
# them has it, the benefit is too big or too small.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then echo "usage: monthly-cost ESTATE" >&2; exit 2; fi
tail -n +2 "$1" | awk -F, '
  { n = $2 } n < 4 { n = 4 }
  $4 == "standard" { rate = 0.10 } $4 == "enterprise" { rate = 0.375 } $4 == "none" { rate = 0 }
  { included += $8 + rate * n }
  $5 == "yes" { benefit += $7 }
  $5 != "yes" { benefit += $8 + rate * n }
  END {
    printf "licence-included: %.2f\n", included * 730
    printf "with-hybrid-benefit: %.2f\n", benefit * 730
    printf "saving: %.2f\n", (included - benefit) * 730
  }'
EOF
chmod +x ~/bin/monthly-cost
