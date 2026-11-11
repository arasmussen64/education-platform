# Wrong: c2 given 4 vCPUs to be safe, paying for twice the vCPUs it needs.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
c1,n4-standard-2,66.21
c2,r7i.xlarge,677.88
c3,NC4as_T4_v3,47.34
saving,,919.71
EOF
