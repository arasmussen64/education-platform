#!/bin/bash
# Lays down the lab: the licensing workbench's README and the shop's seven
# servers moving to Azure. The servers are invented; their prices are real
# Azure list prices (East US, pay-as-you-go, read from the public Azure Retail
# Prices API on 2026-11-11): Standard_D2s_v5 0.096 and 0.188,
# Standard_D4s_v5 0.192 and 0.376, Standard_E8s_v5 0.504 and 0.872,
# Standard_D16s_v5 0.768 and 1.504 (Linux and Windows, an hour), and the
# SQL Server licence meters, Standard 0.10 and Enterprise 0.375 a vCPU-hour
# with the smallest meter named "1-4 vCPU VM".
set -euo pipefail

mkdir -p /srv/licensing
cat > /srv/licensing/README.txt <<'EOF'
The licensing workbench: what the files here are
=================================================

Prices are Azure's, region East US, pay-as-you-go list prices in US dollars
an hour, read from Microsoft's public Azure Retail Prices API on 2026-11-11.
They will have moved since; today's are on
https://azure.microsoft.com/en-us/pricing/details/virtual-machines/windows/

A month is 730 hours (365 days x 24 hours / 12).

An estate file is a CSV: a heading line, then one server a line.

  server          the server's name
  vcpus           its vCPUs on Azure
  os              windows or linux
  sql             the SQL Server edition it runs: none, standard or enterprise
  win_sa          yes if its Windows Server licences have active Software
                  Assurance, so it may use Azure Hybrid Benefit
  sql_sa          yes if its SQL Server licences have active Software
                  Assurance, so it may use Azure Hybrid Benefit for SQL Server
  linux_hourly    the VM's price an hour as Linux: the machine alone
  windows_hourly  the VM's price an hour with Windows Server licence included
                  (the same as linux_hourly on a Linux server)

SQL Server licence included is charged on top of the VM, per vCPU an hour,
and for at least 4 vCPUs:

  standard    0.10
  enterprise  0.375

The licences the shop owns are of the edition each server runs.
EOF

cat > /srv/licensing/shop-estate.csv <<'EOF'
server,vcpus,os,sql,win_sa,sql_sa,linux_hourly,windows_hourly
web-1,2,windows,none,yes,no,0.096,0.188
web-2,2,windows,none,yes,no,0.096,0.188
app-1,4,windows,none,no,no,0.192,0.376
db-1,2,windows,standard,yes,yes,0.096,0.188
db-2,8,windows,enterprise,yes,no,0.504,0.872
rpt-1,16,windows,none,yes,no,0.768,1.504
cache-1,4,linux,none,no,no,0.192,0.192
EOF

chmod 644 /srv/licensing/*
# What the checks compare the files with, so a changed price can't make the
# answers come out right.
mkdir -p /usr/local/lib/lab
(cd /srv/licensing && sha256sum README.txt shop-estate.csv) > /usr/local/lib/lab/data.sha256
