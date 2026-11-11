# One way through the report, with the pipelines of this topic's practice.
# Every number could also be worked out with a calculator; that is the same
# skill. The rules, as the Product Terms stood in November 2026:
# - Azure Hybrid Benefit needs active Software Assurance, and at least 8
#   Windows Server core licences a VM (4 for SQL Server).
# - On AWS, SQL Server with Software Assurance comes across through License
#   Mobility, onto shared instances, at least 4 a VM. Windows Server has no
#   License Mobility, so on shared instances it is licence included whatever
#   its Software Assurance; its old licences (bought in 2018, for 2019) may
#   only go to dedicated hardware, which the host question prices.
e=/srv/licensing/estate.csv
cd ~/report

# Windows Server licences for Azure Hybrid Benefit: Azure, Windows, Software
# Assurance, at least 8 a VM.
w=$(tail -n +2 $e | awk -F, '$2 == "azure" && $4 == "windows" && $6 == "yes"' | awk -F, '{n = $3} n < 8 {n = 8} {total += n} END {print total}')

# SQL Server licences brought with Software Assurance, either cloud, at least 4.
s=$(tail -n +2 $e | awk -F, '$5 != "none" && $7 == "yes"' | awk -F, '{n = $3} n < 4 {n = 4} {total += n} END {print total}')

# Every licence included: the Windows price, plus SQL Server at its cloud's
# rate (sql-rates.csv) on at least 4 vCPUs.
li=$(tail -n +2 $e | awk -F, '{n = $3} n < 4 {n = 4}
  {hourly = $11}
  $2 == "azure" && $5 == "standard" {hourly += 0.10 * n}
  $2 == "azure" && $5 == "enterprise" {hourly += 0.375 * n}
  $2 == "aws" && $5 == "standard" {hourly += 0.12 * n}
  $2 == "aws" && $5 == "enterprise" {hourly += 0.375 * n}
  {total += hourly} END {printf "%.0f\n", total * 730}')

# The cheapest allowed, on shared hardware: the Linux price only for Azure
# Windows servers with Software Assurance; no SQL Server charge wherever its
# Software Assurance is active, on either cloud.
best=$(tail -n +2 $e | awk -F, '{n = $3} n < 4 {n = 4}
  {hourly = $11}
  $2 == "azure" && $6 == "yes" {hourly = $10}
  $7 != "yes" && $2 == "azure" && $5 == "standard" {hourly += 0.10 * n}
  $7 != "yes" && $2 == "azure" && $5 == "enterprise" {hourly += 0.375 * n}
  $7 != "yes" && $2 == "aws" && $5 == "standard" {hourly += 0.12 * n}
  $7 != "yes" && $2 == "aws" && $5 == "enterprise" {hourly += 0.375 * n}
  {total += hourly} END {printf "%.0f\n", total * 730}')

# The host: $6.758 an hour for any number of Windows VMs, against $0.376 an
# hour each with Windows licence included. 6.758 / 0.376 = 17.97, so 17 VMs
# still cost less licence included and 18 cost more. Six don't come near.
be=$(awk 'BEGIN {print int(6.758 / 0.376) + 1}')
cheaper=no

printf 'azure_windows_licences=%s\nsql_licences=%s\nmonthly_licence_included=%s\nmonthly_best=%s\nhost_break_even_vms=%s\nhost_cheaper=%s\n' \
  "$w" "$s" "$li" "$best" "$be" "$cheaper" > estate.txt
cat estate.txt
