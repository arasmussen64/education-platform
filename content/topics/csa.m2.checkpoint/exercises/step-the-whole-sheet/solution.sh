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

# w1, orders-api: the 95th percentile, 27.2% of n4-standard-8's 8 vCPUs, is
#   2.18 vCPUs, at most 60% of the new size: 2.18 / 0.6 = 3.63 vCPUs.
#   Memory: the peak, 11.2 GiB, at most 80%: 14.00 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; Google Cloud; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "gcp" && $6 == "x86" && $7 >= 3.63 && $8 >= 14.00 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# w2, ledger-db: the 95th percentile, 24.2% of D16s_v5's 16 vCPUs, is
#   3.87 vCPUs, at most 60% of the new size: 3.87 / 0.6 = 6.45 vCPUs.
#   Memory: the peak, 41.3 GiB, at most 80%: 51.63 GiB.
#   Its peaks are long, so no burstable size.
#   a size with a Windows price; Azure; Windows Server and SQL Server Standard; 730 hours a month.
awk -F, 'NR > 1 && $2 == "azure" && $7 >= 6.45 && $8 >= 51.63 && $12 == "" && $14 != "" {print ($14 + 0.10 * ($7 < 4 ? 4 : $7)) * 730, $4}' prices.csv | sort -n | head -n 3

# w3, thumbnailer: the 95th percentile, 50.2% of m7i.xlarge's 4 vCPUs, is
#   2.01 vCPUs, at most 60% of the new size: 2.01 / 0.6 = 3.35 vCPUs.
#   Memory: the peak, 9.0 GiB, at most 80%: 11.25 GiB.
#   Its peaks are long, so no burstable size.
#   Arm, as its team decided (nothing in it is tied to x86); AWS; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "aws" && $6 == "arm" && $7 >= 3.35 && $8 >= 11.25 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# w4, caption-model: the 95th percentile, 9.0% of NC24ads_A100_v4's 24 vCPUs, is
#   2.16 vCPUs, at most 60% of the new size: 2.16 / 0.6 = 3.60 vCPUs.
#   Memory: the peak, 11.6 GiB, at most 80%: 14.50 GiB.
#   GPU memory: the peak, 19.4 GiB, at most 90%: 21.56 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; any cloud; Linux; 180 hours a month.
awk -F, 'NR > 1 && $6 == "x86" && $7 >= 3.60 && $8 >= 14.50 && $11 != "" && $11 >= 21.56 && $12 == "" {print $13 * 180, $4}' prices.csv | sort -n | head -n 3

# w5, wiki: the 95th percentile, 30.2% of m7i.large's 2 vCPUs, is
#   0.60 vCPUs, at most 60% of the new size: 0.60 / 0.6 = 1.00 vCPUs.
#   Memory: the peak, 2.9 GiB, at most 80%: 3.63 GiB.
#   Its peaks are short, so a burstable size may do if its average,
#   8.13% of 2 vCPUs = 0.16 vCPUs, is within the baseline.
#   x86 only; AWS or Azure; Linux; 730 hours a month.
awk -F, 'NR > 1 && ($2 == "aws" || $2 == "azure") && $6 == "x86" && $7 >= 1.00 && $8 >= 3.63 && ($12 == "" || 0.16 <= $12 / 100 * $7) {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# Today: 264.84 + 2265.92 + 147.17 + 661.14 + 73.58 = 3412.66 a month.
# The new sizes: 1629.72. The saving: 3412.66 - 1629.72 = 1782.94.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,1782.94
EOF
cat ~/sizing/answers.csv
