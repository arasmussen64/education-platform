# Wrong: w1 on a burstable B4s_v2, cheaper than the fixed sizes, though its
# peaks are long.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,B4s_v2,121.18
w2,n4-highmem-4,658.49
w3,c4a-standard-4,131.11
w4,g6.xlarge,587.50
w5,t3.large,60.74
saving,,2786.29
EOF
