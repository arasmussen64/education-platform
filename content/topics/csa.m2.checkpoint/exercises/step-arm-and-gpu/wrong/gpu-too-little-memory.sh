# Wrong: w4 on a T4 with 16 GiB, too little for its peak.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,g4dn.xlarge,94.68
w5,B2ls_v2,30.37
saving,,1815.49
EOF
