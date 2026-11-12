# Wrong: every workload left where it is.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-8,264.84
w2,D16s_v5,2265.92
w3,m7i.xlarge,147.17
w4,NC24ads_A100_v4,661.14
w5,m7i.large,73.58
saving,,0.00
EOF
