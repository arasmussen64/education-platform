# Wrong: the right families, each a size larger to be safe: every workload
# pays about twice what it needs.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-8,264.84
w2,E16s_v5,2441.12
w3,m7g.2xlarge,238.27
w4,g2-standard-8,153.65
w5,t3.large,60.74
saving,,254.03
EOF
