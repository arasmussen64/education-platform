# Wrong: w5 on a fixed-size D2s_v5 out of habit, though its peaks are short
# and its average sits far under a burstable baseline.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,D2s_v5,70.08
saving,,1743.23
EOF
