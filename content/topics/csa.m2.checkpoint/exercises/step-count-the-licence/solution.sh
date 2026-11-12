# A reference, one way among several: each brief, metric-summary for each
# workload, the policy worked out by hand, then an awk filter over
# prices.csv for the sizes that meet it, the cheapest first. The numbers
# in the filters are the ones metric-summary prints. cat > FILE <<'EOF'
# writes the lines up to EOF into FILE.
# The rows for w1, w3, w4, w5 were already in the sheet.
cd /srv/sizing
cat README.txt
cat workloads/w2/brief.txt
metric-summary workloads/w2/metrics.csv

# w2, ledger-db: the 95th percentile, 24.2% of D16s_v5's 16 vCPUs, is
#   3.87 vCPUs, at most 60% of the new size: 3.87 / 0.6 = 6.45 vCPUs.
#   Memory: the peak, 41.3 GiB, at most 80%: 51.63 GiB.
#   Its peaks are long, so no burstable size.
#   a size with a Windows price; Azure; Windows Server and SQL Server Standard; 730 hours a month.
awk -F, 'NR > 1 && $2 == "azure" && $7 >= 6.45 && $8 >= 51.63 && $12 == "" && $14 != "" {print ($14 + 0.10 * ($7 < 4 ? 4 : $7)) * 730, $4}' prices.csv | sort -n | head -n 3

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
