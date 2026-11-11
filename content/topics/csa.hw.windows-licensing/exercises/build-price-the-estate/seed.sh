#!/bin/bash
# Lays down the build: Fenwick Tools' fourteen servers, eight moving to Azure
# and six to AWS, with the facts the report needs. The servers are invented;
# the prices are real list prices read on 2026-11-11:
# - Azure, East US, pay-as-you-go (the public Azure Retail Prices API):
#   Standard_D2s_v5 0.096 and 0.188, Standard_D4s_v5 0.192 and 0.376,
#   Standard_D8s_v5 0.384 and 0.752, Standard_D16s_v5 0.768 and 1.504,
#   Standard_E8s_v5 0.504 and 0.872 (Linux and Windows, an hour); SQL Server
#   licence meters Standard 0.10 and Enterprise 0.375 a vCPU-hour, the
#   smallest named "1-4 vCPU VM".
# - AWS, US East (N. Virginia), on-demand (AWS's public price files,
#   published 2026-11-10): m6i.xlarge 0.192 Linux, 0.376 Windows, 0.856 with
#   SQL Server Standard and 1.876 with Enterprise, so SQL Server adds 0.12 and
#   0.375 a vCPU-hour for at least 4 vCPUs; the M6i Dedicated Host 6.758 an
#   hour, with 2 sockets and 64 physical cores, at most 32 m6i.xlarge (AWS's
#   Dedicated Hosts pricing page and its guide "Bring licenses for Windows
#   and SQL Server workloads").
set -euo pipefail

mkdir -p /srv/licensing
cat > /srv/licensing/README.txt <<'EOF'
Fenwick Tools: the move to two clouds
=====================================

Prices are list prices in US dollars an hour, read on 2026-11-11:
  Azure  East US, pay-as-you-go, from Microsoft's public Azure Retail Prices API
  AWS    US East (N. Virginia), on-demand, from AWS's public price files
They will have moved since; today's are on each cloud's price pages.

A month is 730 hours (365 days x 24 hours / 12).

estate.csv is one server a line, after a heading line:

  server          the server's name
  cloud           where it is going: azure or aws
  vcpus           its vCPUs there
  os              windows or linux
  sql             the SQL Server edition it runs: none, standard or enterprise
  win_sa          yes if its Windows Server licences have active Software Assurance
  sql_sa          yes if its SQL Server licences have active Software Assurance
  win_bought      the year its Windows Server licences were bought (- for none)
  win_version     the Windows Server version those licences are for (- for none)
  linux_hourly    its VM's price an hour as Linux, on shared hardware: the machine alone
  windows_hourly  the same VM with Windows Server licence included, on shared
                  hardware (the same as linux_hourly on a Linux server)

The six AWS servers are m6i.xlarge instances (4 vCPUs, 16 GiB).

sql-rates.csv is what SQL Server licence included adds on each cloud, on top
of the VM, per vCPU an hour, for at least 4 vCPUs. Fenwick's SQL Server
licences are of the edition each server runs.

host.txt describes an AWS M6i Dedicated Host, which Fenwick is weighing for
its six AWS servers. Fenwick owns Windows Server 2019 Datacenter core
licences, bought in 2018, enough for all of one host's physical cores, so on
such a host its Windows VMs would cost nothing but the host. The question of
the host is about Windows Server only: compare the host with the same VMs on
shared instances with Windows licence included, and leave SQL Server out of
that sum.

The report goes in ~/report/estate.txt, one key=value line for each key:

  azure_windows_licences    Windows Server core licences to set aside for
                            Azure Hybrid Benefit
  sql_licences              SQL Server core licences Fenwick brings under
                            Software Assurance, on both clouds
  monthly_licence_included  all 14 servers with every licence included, in
                            whole dollars a month
  monthly_best              all 14 servers on shared hardware, each on the
                            cheapest option Fenwick's licences allow, in whole
                            dollars a month
  host_break_even_vms       the fewest of these AWS Windows VMs (m6i.xlarge)
                            for which one M6i Dedicated Host with Fenwick's own
                            licences costs less than the same VMs with Windows
                            licence included
  host_cheaper              yes or no: for Fenwick's six AWS servers, would
                            the host cost less than licence included?

The two monthly totals may be off by 1%; the other answers must be exact.
EOF

cat > /srv/licensing/estate.csv <<'EOF'
server,cloud,vcpus,os,sql,win_sa,sql_sa,win_bought,win_version,linux_hourly,windows_hourly
az-web-1,azure,2,windows,none,yes,no,2023,2025,0.096,0.188
az-web-2,azure,4,windows,none,yes,no,2023,2025,0.192,0.376
az-app-1,azure,4,windows,none,no,no,2021,2019,0.192,0.376
az-db-1,azure,2,windows,standard,yes,yes,2023,2025,0.096,0.188
az-db-2,azure,16,windows,enterprise,yes,yes,2023,2025,0.768,1.504
az-rpt-1,azure,8,windows,standard,no,no,2021,2019,0.504,0.872
az-file-1,azure,8,windows,none,yes,no,2023,2025,0.384,0.752
az-cache-1,azure,4,linux,none,no,no,-,-,0.192,0.192
aw-app-1,aws,4,windows,none,yes,no,2018,2019,0.192,0.376
aw-app-2,aws,4,windows,none,yes,no,2018,2019,0.192,0.376
aw-app-3,aws,4,windows,none,yes,no,2018,2019,0.192,0.376
aw-db-1,aws,4,windows,standard,yes,yes,2018,2019,0.192,0.376
aw-db-2,aws,4,windows,enterprise,yes,yes,2018,2019,0.192,0.376
aw-db-3,aws,4,windows,standard,yes,no,2018,2019,0.192,0.376
EOF

cat > /srv/licensing/sql-rates.csv <<'EOF'
cloud,edition,per_vcpu_hour
azure,standard,0.10
azure,enterprise,0.375
aws,standard,0.12
aws,enterprise,0.375
EOF

cat > /srv/licensing/host.txt <<'EOF'
# An AWS M6i Dedicated Host, US East (N. Virginia), on-demand, read 2026-11-11
price_hourly=6.758
sockets=2
physical_cores=64
holds_m6i_xlarge=32
EOF

chmod 644 /srv/licensing/*
install -d -o learner -g learner /home/learner/report
mkdir -p /usr/local/lib/lab
(cd /srv/licensing && sha256sum README.txt estate.csv sql-rates.csv host.txt) > /usr/local/lib/lab/data.sha256
