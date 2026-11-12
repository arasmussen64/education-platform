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

# w1, job-tracker: the 95th percentile, 20.2% of D8s_v5's 8 vCPUs, is
#   1.62 vCPUs, at most 60% of the new size: 1.62 / 0.6 = 2.70 vCPUs.
#   Memory: the peak, 9.6 GiB, at most 80%: 12.00 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; Azure; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "azure" && $6 == "x86" && $7 >= 2.70 && $8 >= 12.00 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# w2, quotes-db: the 95th percentile, 21.2% of n4-highmem-8's 8 vCPUs, is
#   1.70 vCPUs, at most 60% of the new size: 1.70 / 0.6 = 2.84 vCPUs.
#   Memory: the peak, 22.4 GiB, at most 80%: 28.00 GiB.
#   Its peaks are long, so no burstable size.
#   a size with a Windows price; Google Cloud; Windows Server and SQL Server Standard; 730 hours a month.
awk -F, 'NR > 1 && $2 == "gcp" && $7 >= 2.84 && $8 >= 28.00 && $12 == "" && $14 != "" {print ($14 + 0.12 * ($7 < 4 ? 4 : $7)) * 730, $4}' prices.csv | sort -n | head -n 3

# w3, proof-renderer: the 95th percentile, 22.2% of n4-standard-8's 8 vCPUs, is
#   1.78 vCPUs, at most 60% of the new size: 1.78 / 0.6 = 2.97 vCPUs.
#   Memory: the peak, 10.8 GiB, at most 80%: 13.50 GiB.
#   Its peaks are long, so no burstable size.
#   Arm, as its team decided (nothing in it is tied to x86); Google Cloud; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "gcp" && $6 == "arm" && $7 >= 2.97 && $8 >= 13.50 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# w4, press-check: the 95th percentile, 6.0% of NV36ads_A10_v5's 36 vCPUs, is
#   2.16 vCPUs, at most 60% of the new size: 2.16 / 0.6 = 3.60 vCPUs.
#   Memory: the peak, 12.0 GiB, at most 80%: 15.00 GiB.
#   GPU memory: the peak, 17.0 GiB, at most 90%: 18.89 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; AWS or Azure; Linux; 730 hours a month.
awk -F, 'NR > 1 && ($2 == "aws" || $2 == "azure") && $6 == "x86" && $7 >= 3.60 && $8 >= 15.00 && $11 != "" && $11 >= 18.89 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# w5, staff-handbook: the 95th percentile, 26.2% of m7i.xlarge's 4 vCPUs, is
#   1.05 vCPUs, at most 60% of the new size: 1.05 / 0.6 = 1.75 vCPUs.
#   Memory: the peak, 5.6 GiB, at most 80%: 7.00 GiB.
#   Its peaks are short, so a burstable size may do if its average,
#   12.81% of 4 vCPUs = 0.51 vCPUs, is within the baseline.
#   x86 only; AWS; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "aws" && $6 == "x86" && $7 >= 1.75 && $8 >= 7.00 && ($12 == "" || 0.51 <= $12 / 100 * $7) {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

# Today: 280.32 + 1316.98 + 264.84 + 2336.00 + 147.17 = 4345.31 a month.
# The new sizes: 1578.00. The saving: 4345.31 - 1578.00 = 2767.31.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,D4s_v5,140.16
w2,n4-highmem-4,658.49
w3,c4a-standard-4,131.11
w4,g6.xlarge,587.50
w5,t3.large,60.74
saving,,2767.31
EOF
cat ~/sizing/answers.csv
