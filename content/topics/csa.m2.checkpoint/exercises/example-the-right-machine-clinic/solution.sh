# A reference, one way among several: each brief, metric-summary for each
# workload, the policy worked out by hand, then an awk filter over
# prices.csv for the sizes that meet it, the cheapest first. The numbers
# in the filters are the ones metric-summary prints. cat > FILE <<'EOF'
# writes the lines up to EOF into FILE.
cd /srv/sizing
cat README.txt
cat workloads/c1/brief.txt
metric-summary workloads/c1/metrics.csv
cat workloads/c2/brief.txt
metric-summary workloads/c2/metrics.csv
cat workloads/c3/brief.txt
metric-summary workloads/c3/metrics.csv

# c1, booking-api: the 95th percentile, 10.2% of n4-standard-8's 8 vCPUs, is
#   0.82 vCPUs, at most 60% of the new size: 0.82 / 0.6 = 1.37 vCPUs.
#   Memory: the peak, 5.4 GiB, at most 80%: 6.75 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; Google Cloud; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "gcp" && $6 == "x86" && $7 >= 1.37 && $8 >= 6.75 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# c2, records-db: the 95th percentile, 9.2% of r7i.2xlarge's 8 vCPUs, is
#   0.74 vCPUs, at most 60% of the new size: 0.74 / 0.6 = 1.24 vCPUs.
#   Memory: the peak, 11.6 GiB, at most 80%: 14.50 GiB.
#   Its peaks are long, so no burstable size.
#   a size with a Windows price; AWS; Windows Server and SQL Server Standard; 730 hours a month.
awk -F, 'NR > 1 && $2 == "aws" && $7 >= 1.24 && $8 >= 14.50 && $12 == "" && $14 != "" {print ($14 + 0.12 * ($7 < 4 ? 4 : $7)) * 730, $4}' prices.csv | sort -n | head -n 3

# c3, scan-reader: the 95th percentile, 30.8% of g5.xlarge's 4 vCPUs, is
#   1.23 vCPUs, at most 60% of the new size: 1.23 / 0.6 = 2.05 vCPUs.
#   Memory: the peak, 9.8 GiB, at most 80%: 12.25 GiB.
#   GPU memory: the peak, 11.8 GiB, at most 90%: 13.12 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; any cloud; Linux; 90 hours a month.
awk -F, 'NR > 1 && $6 == "x86" && $7 >= 2.05 && $8 >= 12.25 && $11 != "" && $11 >= 13.12 && $12 == "" {print $13 * 90, $4}' prices.csv | sort -n | head -n 3

# Today: 264.84 + 1355.76 + 90.54 = 1711.14 a month.
# The new sizes: 627.69. The saving: 1711.14 - 627.69 = 1083.45.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
c1,n4-standard-2,66.21
c2,r7i.large,514.14
c3,NC4as_T4_v3,47.34
saving,,1083.45
EOF
cat ~/sizing/answers.csv
