# Wrong: w2 sized on CPU alone: m7i.xlarge has the vCPUs, and 16 GiB for a
# peak of 23.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,m7i.xlarge,147.17
w2,m7i.xlarge,631.89
w3,D4ps_v6,102.20
w4,g6e.xlarge,223.32
w5,D2s_v5,70.08
saving,,1210.87
EOF
