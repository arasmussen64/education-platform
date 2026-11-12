# Wrong: every workload stays on the machine it runs on now.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
c1,n4-standard-8,264.84
c2,r7i.2xlarge,1355.76
c3,g5.xlarge,90.54
saving,,0.00
EOF
