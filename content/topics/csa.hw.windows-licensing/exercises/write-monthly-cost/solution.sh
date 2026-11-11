# One way to write it. `cat > FILE <<'EOF'` writes every line up to the
# closing EOF into FILE, exactly as typed. The awk program works out each
# server's hour twice, with every licence included and with Azure Hybrid
# Benefit where its Software Assurance allows it, and the minimum of 4 vCPUs
# for SQL Server is the same two rules as in the worked example.
mkdir -p ~/bin
cat > ~/bin/monthly-cost <<'EOF'
#!/bin/bash
# Usage: monthly-cost ESTATE
# Prints what an estate's servers cost in a 730-hour month on Azure with
# every licence included, the same with Azure Hybrid Benefit wherever the
# licences have Software Assurance, and the difference.
if [ $# -ne 1 ]; then
  echo "usage: monthly-cost ESTATE" >&2
  exit 2
fi

tail -n +2 "$1" | awk -F, '
  # SQL Server is charged per vCPU, for at least 4.
  { n = $2 }
  n < 4 { n = 4 }
  $4 == "standard" { rate = 0.10 }
  $4 == "enterprise" { rate = 0.375 }
  $4 == "none" { rate = 0 }

  # Licence included: the Windows price (the Linux one on a Linux server) and SQL Server.
  { included += $8 + rate * n }

  # With the benefit: the Linux price where Windows has Software Assurance,
  # and no SQL Server charge where SQL Server has it.
  { hourly = $8 }
  $5 == "yes" { hourly = $7 }
  $6 != "yes" { hourly += rate * n }
  { benefit += hourly }

  END {
    printf "licence-included: %.2f\n", included * 730
    printf "with-hybrid-benefit: %.2f\n", benefit * 730
    printf "saving: %.2f\n", (included - benefit) * 730
  }'
EOF
chmod +x ~/bin/monthly-cost
~/bin/monthly-cost /srv/licensing/estate.csv
