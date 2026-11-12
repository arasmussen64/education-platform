# Wrong: w1 moved to Arm for the lower price, though its vendor's licence
# server runs only on x86.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,D4ps_v6,102.20
w2,n4-highmem-4,658.49
w3,c4a-standard-4,131.11
w4,g6.xlarge,587.50
w5,t3.large,60.74
saving,,2805.27
EOF
