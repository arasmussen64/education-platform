# Wrong: w5 on t3.medium, the smallest burstable size: 4 GiB for a 5.6 GiB
# peak.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,D4s_v5,140.16
w2,n4-highmem-4,658.49
w3,c4a-standard-4,131.11
w4,g6.xlarge,587.50
w5,t3.medium,30.37
saving,,2797.68
EOF
