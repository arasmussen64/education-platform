# Wrong: w3 kept on its x86 size, though nothing in it stops the move its
# team decided on.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,m7i.xlarge,147.17
w2,r7i.xlarge,677.88
w3,D4s_v6,147.46
w4,g6e.xlarge,223.32
w5,D2s_v5,70.08
saving,,1119.62
EOF
