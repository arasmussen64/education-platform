# Wrong: every workload stays on the machine it runs on now, costed
# correctly.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,m7i.2xlarge,294.34
w2,r7i.2xlarge,1355.76
w3,D4s_v6,147.46
w4,a2-highgpu-1g,440.81
w5,m7i.xlarge,147.17
saving,,0.00
EOF
