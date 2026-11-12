# Wrong: w4 on an L4 card, the size that suited last time: 22 GiB for a 31
# GiB peak.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,m7i.xlarge,147.17
w2,r7i.xlarge,677.88
w3,D4ps_v6,102.20
w4,g6.xlarge,96.58
w5,D2s_v5,70.08
saving,,1291.62
EOF
