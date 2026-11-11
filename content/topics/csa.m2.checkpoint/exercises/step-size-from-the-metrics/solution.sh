# A reference, one way among several: each brief, metric-summary for each
# workload, the policy worked out by hand, then an awk filter over
# prices.csv for the sizes that meet it, the cheapest first. The numbers
# in the filters are the ones metric-summary prints. cat > FILE <<'EOF'
# writes the lines up to EOF into FILE.
# The rows for w2, w3, w4, w5 were already in the sheet.
cd /srv/sizing
cat README.txt
cat workloads/w1/brief.txt
metric-summary workloads/w1/metrics.csv

# w1, orders-api: the 95th percentile, 27.2% of n4-standard-8's 8 vCPUs, is
#   2.18 vCPUs, at most 60% of the new size: 2.18 / 0.6 = 3.64 vCPUs.
#   Memory: the peak, 11.2 GiB, at most 80%: 14.00 GiB.
#   Its peaks are long, so no burstable size.
#   x86 only; Google Cloud; Linux; 730 hours a month.
awk -F, 'NR > 1 && $2 == "gcp" && $6 == "x86" && $7 >= 3.64 && $8 >= 14.00 && $12 == "" {print $13 * 730, $4}' prices.csv | sort -n | head -n 3

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
