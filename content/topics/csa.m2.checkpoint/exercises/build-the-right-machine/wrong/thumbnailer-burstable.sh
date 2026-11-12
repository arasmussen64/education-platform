# Wrong: w3 on a burstable Arm size, t4g.large: 2 vCPUs are too few for its
# busy hours, and its average is far above the baseline.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,1220.56
w3,t4g.large,49.06
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,1853.02
EOF
