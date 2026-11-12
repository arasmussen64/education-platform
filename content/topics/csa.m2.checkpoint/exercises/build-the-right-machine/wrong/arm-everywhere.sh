# Wrong: w1 and w5 moved to Arm too, for the lower price, though w1's vendor
# agent and w5's image run only on x86.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,c4a-standard-4,131.11
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,t4g.medium,24.53
saving,,1790.09
EOF
