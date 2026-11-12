# Wrong: w3 kept on x86, though nothing in it stops the move its team
# decided on.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,1220.56
w3,m7i.xlarge,147.17
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,1754.91
EOF
