# Wrong: the right sizes, but w2 costed with Windows Server and without SQL
# Server Standard.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,m7i.xlarge,147.17
w2,r7i.xlarge,327.48
w3,D4ps_v6,102.20
w4,g6e.xlarge,223.32
w5,D2s_v5,70.08
saving,,1515.28
EOF
