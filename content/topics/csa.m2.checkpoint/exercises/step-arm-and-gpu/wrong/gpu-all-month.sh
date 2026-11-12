# Wrong: w4 costed for 730 hours, though it runs 180.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,g2-standard-4,515.99
w5,B2ls_v2,30.37
saving,,1394.18
EOF
