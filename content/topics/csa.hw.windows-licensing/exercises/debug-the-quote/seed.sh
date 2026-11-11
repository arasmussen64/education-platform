#!/bin/bash
# Lays down the debug: a colleague's quoting script, its README, Harbour
# Dental's inventory and a second customer's. The servers are invented; the
# prices are real Azure list prices (East US, pay-as-you-go, read from the
# public Azure Retail Prices API on 2026-11-11): Standard_D2s_v5 0.096 and
# 0.188, Standard_D4s_v5 0.192 and 0.376, Standard_D8s_v5 0.384 and 0.752,
# Standard_E4s_v5 0.252 and 0.436, Standard_E8s_v5 0.504 and 0.872 (Linux
# and Windows, an hour); the Dasv5-Type1 dedicated host 5.298 an hour,
# holding at most 28 Standard_D4as_v5 (Microsoft's general-purpose host
# sizes page, 2026-09-25); SQL Server licence meters Standard 0.10 and
# Enterprise 0.375 a vCPU-hour, the smallest named "1-4 vCPU VM".
set -euo pipefail

q=/home/learner/quote
install -d -o learner -g learner "$q"

cat > "$q/README.txt" <<'EOF'
Quotes for moving to Azure
==========================

Prices are Azure's, region East US, pay-as-you-go list prices in US dollars
an hour, read from Microsoft's public Azure Retail Prices API on 2026-11-11.
A month is 730 hours.

An inventory is a CSV: a heading line, then one line a row.

  name            the server's name, or the dedicated host's
  kind            vm      a VM on shared hardware
                  host    a dedicated host of the customer's own
                  hosted  a VM that runs on that dedicated host
  vcpus           the VM's vCPUs (- on a host)
  os              windows or linux (- on a host)
  sql             the SQL Server edition it runs: none, standard or enterprise
  win_sa          yes if its Windows Server licences have active Software
                  Assurance (- on a host)
  sql_sa          yes if its SQL Server licences have active Software
                  Assurance (- on a host)
  linux_hourly    on a vm, its price an hour as Linux: the machine alone; on
                  a host, the host's price an hour; 0 on a hosted VM, whose
                  machine the host is
  windows_hourly  on a vm, its price an hour with Windows Server licence
                  included; on a host, the host's price again; 0 on a hosted VM
  slots           on a host, how many VMs of its size it holds (- otherwise)

An inventory has at most one dedicated host. Every physical core of it is
licensed with the customer's own Windows Server Datacenter licences, with
Software Assurance, so the Windows VMs on it need no other Windows Server
licence. The licences a customer owns are of the edition each server runs.

SQL Server licence included is charged on top of the VM, per vCPU an hour,
for at least 4 vCPUs: standard 0.10, enterprise 0.375.

A quote has one line a charge, and the total:

  compute  NAME   a VM on shared hardware: its machine for the month
  windows  NAME   a Windows VM on shared hardware: its Windows Server licence
                  for the month, 0.00 where the customer brings its own
  sql      NAME   a VM that runs SQL Server: its SQL Server licence for the
                  month, 0.00 where the customer brings its own
  host     NAME   the dedicated host for the month
  total           the month's total
EOF

cat > "$q/inventory.csv" <<'EOF'
name,kind,vcpus,os,sql,win_sa,sql_sa,linux_hourly,windows_hourly,slots
hg-1,host,-,-,none,-,-,5.298,5.298,28
records-1,hosted,4,windows,standard,yes,yes,0,0,-
records-2,hosted,4,windows,standard,yes,no,0,0,-
web-1,vm,2,windows,none,yes,no,0.096,0.188,-
web-2,vm,2,windows,none,no,no,0.096,0.188,-
booking-1,vm,4,windows,none,no,no,0.192,0.376,-
imaging-1,vm,8,windows,none,yes,no,0.384,0.752,-
db-1,vm,2,windows,standard,no,no,0.096,0.188,-
db-2,vm,8,windows,enterprise,yes,yes,0.504,0.872,-
mail-1,vm,4,linux,none,no,no,0.192,0.192,-
EOF

cat > "$q/inventory-b.csv" <<'EOF'
name,kind,vcpus,os,sql,win_sa,sql_sa,linux_hourly,windows_hourly,slots
app-1,vm,4,windows,none,yes,no,0.192,0.376,-
app-2,vm,8,windows,none,no,no,0.384,0.752,-
ledger-1,vm,2,windows,standard,no,no,0.096,0.188,-
ledger-2,vm,4,windows,enterprise,no,yes,0.252,0.436,-
files-1,vm,2,windows,none,no,no,0.096,0.188,-
web-1,vm,2,linux,none,no,no,0.096,0.096,-
EOF

install -m 755 -o learner -g learner /usr/local/lib/lab/make-quote "$q/make-quote"
chown learner:learner "$q"/*.csv "$q/README.txt"
chmod 644 "$q"/*.csv "$q/README.txt"
rm /usr/local/lib/lab/make-quote
# What the checks compare the inputs with, so a changed price can't make the
# quote come out right.
(cd "$q" && sha256sum README.txt inventory.csv inventory-b.csv) > /usr/local/lib/lab/inputs.sha256
