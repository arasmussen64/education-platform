# Wrong: every workload stays on the machine it runs on now, costed
# correctly.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,D8s_v5,280.32
w2,n4-highmem-8,1316.98
w3,n4-standard-8,264.84
w4,NV36ads_A10_v5,2336.00
w5,m7i.xlarge,147.17
saving,,0.00
EOF
