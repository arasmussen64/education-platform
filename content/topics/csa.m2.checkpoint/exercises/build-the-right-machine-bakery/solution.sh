# A reference, one way among several: each brief, metric-summary for each
# workload, the policy worked out by hand, then an awk filter over
# prices.csv for the sizes that meet it, the cheapest first. The numbers
# in the filters are the ones metric-summary prints. cat > FILE <<'EOF'
# writes the lines up to EOF into FILE.
cd /srv/sizing
cat README.txt
cat workloads/w1/brief.txt
metric-summary workloads/w1/metrics.csv
cat workloads/w2/brief.txt
metric-summary workloads/w2/metrics.csv
cat workloads/w3/brief.txt
metric-summary workloads/w3/metrics.csv
cat workloads/w4/brief.txt
metric-summary workloads/w4/metrics.csv
cat workloads/w5/brief.txt
metric-summary workloads/w5/metrics.csv

# w1, shop-front: the 95th percentile, 22.2% of m7i.2xlarge's 8 vCPUs, is
#   1.78 vCPUs, at most 60% of the new size: 1.78 / 0.6 = 2.97 vCPUs.
#   Memory: the peak, 10.4 GiB, at most 80%: 13.00 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; AWS; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "aws" && $6 == "x86" && $7 >= 2.97 && $8 >= 13.00 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# w2, orders-db: the 95th percentile, 26.2% of r7i.2xlarge's 8 vCPUs, is
#   2.10 vCPUs, at most 60% of the new size: 2.10 / 0.6 = 3.50 vCPUs.
#   Memory: the peak, 23.0 GiB, at most 80%: 28.75 GiB.
#   Its peaks are long, so no burstable size.
#   a size with a Windows price; AWS; Windows Server and SQL Server Standard; 730 hours a month.
awk -F, 'NR > 1 && $2 == "aws" && $7 >= 3.50 && $8 >= 28.75 && $12 == "" && $14 != "" {print ($14 + 0.12 * ($7 < 4 ? 4 : $7)) * 730, $4}' prices.csv | sort -n | head -n 3

# w3, recipe-search: the 95th percentile, 45.2% of D4s_v6's 4 vCPUs, is
#   1.81 vCPUs, at most 60% of the new size: 1.81 / 0.6 = 3.02 vCPUs.
#   Memory: the peak, 8.8 GiB, at most 80%: 11.00 GiB.
#   Its peaks are long, so no burstable size.
#   Arm, as its team decided (nothing in it is tied to x86); Azure; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "azure" && $6 == "arm" && $7 >= 3.02 && $8 >= 11.00 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# w4, forecast-tuning: the 95th percentile, 15.8% of a2-highgpu-1g's 12 vCPUs, is
#   1.90 vCPUs, at most 60% of the new size: 1.90 / 0.6 = 3.17 vCPUs.
#   Memory: the peak, 20.5 GiB, at most 80%: 25.63 GiB.
#   GPU memory: the peak, 31.0 GiB, at most 90%: 34.45 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; any cloud; Linux; 120 hours a month.
awk -F, 'NR > 1 && $6 == "x86" && $7 >= 3.17 && $8 >= 25.63 && $11 != "" && $11 >= 34.45 && $12 == "" {print $13 * 120, $4}' prices.csv | sort -n | head -n 3

# w5, till-sync: the 95th percentile, 26.7% of m7i.xlarge's 4 vCPUs, is
#   1.07 vCPUs, at most 60% of the new size: 1.07 / 0.6 = 1.79 vCPUs.
#   Memory: the peak, 5.1 GiB, at most 80%: 6.38 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; AWS or Azure; Linux; 730 hours a month.
awk -F, 'NR > 1 && ($2 == "aws" || $2 == "azure") && $6 == "x86" && $7 >= 1.79 && $8 >= 6.38 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# Today: 294.34 + 1355.76 + 147.46 + 440.81 + 147.17 = 2385.53 a month.
# The new sizes: 1220.65. The saving: 2385.53 - 1220.65 = 1164.88.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,m7i.xlarge,147.17
w2,r7i.xlarge,677.88
w3,D4ps_v6,102.20
w4,g6e.xlarge,223.32
w5,D2s_v5,70.08
saving,,1164.88
EOF
cat ~/sizing/answers.csv
