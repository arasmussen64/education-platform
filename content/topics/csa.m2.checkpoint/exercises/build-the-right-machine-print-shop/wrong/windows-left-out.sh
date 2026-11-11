# Wrong: the right sizes, but w2 costed at its Linux price: neither Windows
# Server nor SQL Server counted.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,D4s_v5,140.16
w2,n4-highmem-4,173.77
w3,c4a-standard-4,131.11
w4,g6.xlarge,587.50
w5,t3.large,60.74
saving,,3252.03
EOF
