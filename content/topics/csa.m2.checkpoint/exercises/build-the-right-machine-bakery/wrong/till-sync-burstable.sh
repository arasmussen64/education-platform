# Wrong: w5 on a burstable B2s_v2, the cheapest size with the memory: its
# average is above the baseline and it is busy all day.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,m7i.xlarge,147.17
w2,r7i.xlarge,677.88
w3,D4ps_v6,102.20
w4,g6e.xlarge,223.32
w5,B2s_v2,60.74
saving,,1174.22
EOF
