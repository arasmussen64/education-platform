# The script with its three faults put right, written in one go: `cat > FILE
# <<'EOF'` writes every line up to the closing EOF into FILE, exactly as
# typed. In the lab you'd change the three lines with nano. What was wrong:
# - Windows Server: the benefit was tested with the operating system, so
#   every Windows VM got Azure Hybrid Benefit. Only those whose licences have
#   Software Assurance (win_sa, the sixth column) may use it.
# - SQL Server: it was charged on the VM's vCPUs. Licence included is charged
#   for at least 4 vCPUs, so db-1's 2 are charged as 4.
# - The host: it was charged for the share of its slots in use. A dedicated
#   host is billed whole, by the hour, however many VMs run on it.
cat > ~/quote/make-quote <<'EOF'
#!/bin/bash
# Usage: make-quote INVENTORY
# Prints a month's quote for moving an inventory to Azure (East US,
# pay-as-you-go), one line a charge and the total. The prices are in the
# inventory; ~/quote/README.txt says what its columns mean.
inventory="$1"
echo "Quote for $(basename "$inventory"): Azure, East US, 730 hours a month"

tail -n +2 "$inventory" | awk -F, '
  BEGIN { hours = 730; rate["standard"] = 0.10; rate["enterprise"] = 0.375 }

  # The machine: every VM on shared hardware pays its Linux price.
  $2 == "vm" { line("compute", $1, $8 * hours) }

  # Windows Server: VMs using Azure Hybrid Benefit pay nothing more than the
  # machine; the others pay for the licence as well.
  $2 == "vm" && $4 == "windows" {
    benefit = ($6 == "yes")
    line("windows", $1, benefit ? 0 : ($9 - $8) * hours)
  }

  # SQL Server: brought with Software Assurance, or licence included by the
  # vCPU, for at least 4.
  $5 != "none" && $2 != "host" {
    n = $3; if (n < 4) n = 4
    line("sql", $1, $7 == "yes" ? 0 : rate[$5] * n * hours)
  }

  # The dedicated host: billed whole, however many VMs run on it.
  $2 == "host" { host = $1; host_price = $8 }

  END {
    if (host != "") line("host", host, host_price * hours)
    printf "%-8s %-12s %10.2f\n", "total", "", total
  }

  function line(kind, name, amount) {
    printf "%-8s %-12s %10.2f\n", kind, name, amount
    total += amount
  }'
EOF
~/quote/make-quote ~/quote/inventory.csv
